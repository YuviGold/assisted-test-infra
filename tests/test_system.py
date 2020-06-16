import socket
import paramiko
import libvirt
import subprocess
import os
import random
from string import ascii_lowercase
from tempfile import NamedTemporaryFile
from contextlib import suppress

from assisted_service_client.rest import ApiException
from discovery_infra.start_discovery import nodes_flow, _create_node_details
from discovery_infra.utils import get_local_assisted_service_url
from discovery_infra.assisted_service_api import create_client
from discovery_infra.consts import DEFAULT_BASE_DNS_DOMAIN
from discovery_infra.structs import Deployment
from discovery_infra.delete_nodes import delete_clusters_from_all_namespaces, delete_cluster

import pytest
from hypothesis import given, note, strategies as st

SSH_UESR = 'core'
SSH_KEY = 'ssh_key/key'
IMAGE_ISO = '/tmp/installer-image.iso'
TEST_DEPLOYMENT = Deployment(namespace=os.getenv('NAMESPACE'), 
                             profile=os.getenv('PROFILE'), 
                             storage_pool_path=os.getenv('STORAGE_POOL_PATH'),
                             master_count=int(os.getenv('NUM_MASTERS')))


@pytest.fixture()
def exposed_services():
    yield {'bm-inventory': 6000, 'ocp-metal-ui': 6008}


@pytest.fixture()
def host_ip():
    yield socket.gethostbyname(socket.gethostname())


@pytest.fixture()
def ssh_conn():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    yield ssh

    ssh.close()


@pytest.fixture()
def communicate_minikube():
    def func(service_name):
        kubeconfig = os.path.expanduser('~/.kube/config')
        command = f'curl $(minikube ip):$(kubectl --kubeconfig={kubeconfig} \
                    get svc/{service_name} -n assisted-installer -o=jsonpath="{{.spec.ports[0].nodePort}}")'

        return subprocess.check_output(command, shell=True).decode()

    yield func


@pytest.fixture(scope="module", autouse=True)
def deploy_service():
    try:
        get_local_assisted_service_url(os.getenv('PROFILE'), TEST_DEPLOYMENT.namespace, 'assisted-service')
    except RuntimeError:
        subprocess.call("make -C assisted-service/ deploy-all", shell=True)
        # subprocess.call("make -C assisted-service/ clear-all", shell=True)

# @pytest.fixture(scope="module")
# def minikube():
#     subprocess.call("minikube start", shell=True)


@pytest.fixture()
def deploy_nodes():
    clusters = []
    def func(cluster):
        nodes_details = _create_node_details(TEST_DEPLOYMENT, cluster.name, cluster.base_dns_domain,
                                             '192.168.126.0/24', f'tt{TEST_DEPLOYMENT.namespace_index}', int(os.getenv('NETWORK_MTU')),
                                             int(os.getenv('MASTER_DISK')), int(os.getenv('MASTER_MEMORY')),
                                             int(os.getenv('WORKER_DISK')), int(os.getenv('WORKER_MEMORY')))
        clusters.append(cluster)
        nodes_flow(TEST_DEPLOYMENT, None, cluster.name, cluster, nodes_details, IMAGE_ISO)

    yield func

    for cluster in clusters:
        delete_cluster(False, cluster.name, TEST_DEPLOYMENT.namespace, TEST_DEPLOYMENT.profile, 'assisted-service', inventory_url=None)


    # subprocess.call("make _deploy_nodes NAMESPACE_INDEX=0", shell=True)
    # yield
    # subprocess.call("make _destroy_nodes", shell=True)


@pytest.fixture(scope="module", autouse=True)
def clean(client):
    clusters = client.clusters_list()
    for cluster in clusters:
        client.delete_cluster(cluster['id'])

    delete_clusters_from_all_namespaces(False, TEST_DEPLOYMENT.namespace, TEST_DEPLOYMENT.profile, 'assisted-service', None)


@pytest.fixture(autouse=True)
def iso(client, cluster):
    if os.path.exists(IMAGE_ISO):
        return
    c = cluster()
    client.generate_and_download_image(cluster_id=c.id, ssh_key=SSH_KEY, image_path=IMAGE_ISO)
    client.delete_cluster(c.id)


@pytest.fixture(scope="module")
def client(deploy_service):
    yield create_client(get_local_assisted_service_url(os.getenv('PROFILE'), TEST_DEPLOYMENT.namespace, 'assisted-service'))


@pytest.fixture()
def cluster(client):
    clusters = []

    def func():
        res = client.create_cluster(''.join(random.choice(ascii_lowercase) for i in range(10)), 
                                    openshift_version=os.getenv('OPENSHIFT_VERSION'),
                                    pull_secret=os.getenv('PULL_SECRET'),
                                    base_dns_domain=DEFAULT_BASE_DNS_DOMAIN)
        clusters.append(res)
        return res

    yield func

    for cluster in clusters:
        with suppress(ApiException):
            client.delete_cluster(cluster.id)


def test_get_clusters(client):
    assert not client.clusters_list()


def test_create_cluster(client, cluster):
    c = cluster()
    assert c.id in map(lambda cluster: cluster['id'], client.clusters_list())
    assert client.cluster_get(c.id)


def test_delete_cluster(client, cluster):
    c = cluster()
    assert client.cluster_get(c.id)
    client.delete_cluster(c.id)

    with pytest.raises(ApiException):
        assert client.cluster_get(c.id)


def test_deploy_nodes(cluster, deploy_nodes):
    c = cluster()
    deploy_nodes(c)

# def test_download_and_generate_image(client, cluster):
#     c = cluster()

#     with NamedTemporaryFile(delete=False) as temp_file:
#         client.generate_and_download_image(cluster_id=c.id, ssh_key=None, image_path=temp_file.name)


# def test_connectivity_from_vms(communicate_minikube, ssh_conn,
#                                host_ip, exposed_services):
#     conn = libvirt.open('qemu:///system')

#     for dom in filter(lambda dom: dom.name().startswith('test-infra-cluster'),
#                       conn.listAllDomains()):
#         interfaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
#         ip = list(interfaces.values())[0]['addrs'][0]['addr']
#         ssh_conn.connect(ip, username=SSH_UESR, key_filename=SSH_KEY)

#         for name, port in exposed_services.items():
#             ssh_stdin, ssh_stdout, ssh_stderr = ssh_conn.exec_command(f"curl {host_ip}:{port}")
#             assert communicate_minikube(name) == ''.join(ssh_stdout.readlines())
#     else:
#         raise OSError('test-infra-cluster')
