import pytest
import openshift as oc
from logger import log

from tests.base_test import BaseTest
from tests.conftest import env_variables


@pytest.mark.proxy
class TestProxy(BaseTest):
    def _is_proxy_defined_in_install_config(self, cluster_id, api_client, http_proxy, https_proxy):
        install_config = self.get_cluster_install_config(cluster_id=cluster_id, api_client=api_client)
        log.info(f'Verifying proxy parameters are deinfied in install-config.yaml for Cluster {cluster_id}')
        assert install_config['proxy']['httpProxy'] == http_proxy
        assert install_config['proxy']['httpsProxy'] == https_proxy

    def _are_proxy_paramas_defined_in_clusterwide_proxy(self, cluster_id, api_client, http_proxy, https_proxy):
        api_client.download_kubeconfig(cluster_id, env_variables['KUBECONFIG_PATH'])
        log.info(f'Verifying proxy parameters are deinfied in cluster wide proxy object for Cluster {cluster_id}')
        proxy_object = oc.selector('proxy/cluster').objects()[0]
        assert proxy_object.model.spec.httpProxy == http_proxy
        assert proxy_object.model.spec.httpsProxy == https_proxy


    @pytest.mark.parametrize(
        "http_proxy, https_proxy", 
        [
            (env_variables['HTTP_PROXY'], ""), 
            (env_variables['HTTP_PROXY'], env_variables['HTTPS_PROXY'])
        ]
    )
    @pytest.mark.proxy
    def test_http_proxy(self, api_client, node_controller, http_proxy, https_proxy):
        expected_http_proxy_value = http_proxy
        expected_https_proxy_value = https_proxy if https_proxy else http_proxy
        cluster = self.create_cluster(api_client=api_client)
        cluster_id = cluster.id
        cluster = api_client.set_cluster_proxy(
            cluster_id=cluster_id, 
            http_proxy=http_proxy, 
            https_proxy=https_proxy
        )

        assert cluster.http_proxy == expected_http_proxy_value
        assert cluster.https_proxy == expected_https_proxy_value
        self.generate_and_download_image(
            cluster_id=cluster_id, api_client=api_client
        )
        # Boot nodes into ISO
        node_controller.start_all_nodes()
        # Wait until hosts are disovered and update host roles
        self.wait_until_hosts_are_discovered(cluster_id=cluster_id, api_client=api_client)
        self.set_host_roles(cluster_id=cluster_id, api_client=api_client)
        self.set_network_params(cluster_id=cluster_id,
                                api_client=api_client,
                                controller=node_controller
                                )
        #wait until cluster is ready to install
        self.wait_until_cluster_is_ready_for_install(cluster_id=cluster_id, api_client=api_client)
        #Start cluster install
        self.start_cluster_install(cluster_id=cluster_id, api_client=api_client)

        #Assert proxy is defined in install config
        self._is_proxy_defined_in_install_config(
            cluster_id=cluster_id,
            api_client=api_client,
            http_proxy=expected_http_proxy_value,
            https_proxy=expected_https_proxy_value
        )

        #Wait for cluster to install
        self.wait_for_nodes_to_install(cluster_id=cluster_id, api_client=api_client)
        self.wait_for_cluster_to_install(cluster_id=cluster_id, api_client=api_client)

        #Assert proxy value is defined in cluster wide proxy object
        self._are_proxy_paramas_defined_in_clusterwide_proxy(
            cluster_id=cluster_id,
            api_client=api_client,
            http_proxy=expected_http_proxy_value,
            https_proxy=expected_https_proxy_value
        )







