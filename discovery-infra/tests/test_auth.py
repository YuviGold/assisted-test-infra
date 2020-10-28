import logging
import pytest
import waiting
import os
import random
from contextlib import suppress
from string import ascii_lowercase
from typing import Optional
from tests.base_test import BaseTest
from tests.conftest import env_variables
from assisted_service_client.rest import ApiException

def random_name():
    return ''.join(random.choice(ascii_lowercase) for i in range(10))


class TestAuth(BaseTest):
    @pytest.fixture()
    def cluster(self):
        clusters = []
#TODO move to conftest
        def get_cluster_func(api_client, cluster_name: Optional[str] = None):
            if not cluster_name:
                cluster_name = random_name()

            res = api_client.create_cluster(cluster_name,
                                            ssh_public_key=env_variables['ssh_public_key'],
                                            openshift_version=env_variables['openshift_version'],
                                            pull_secret=env_variables['pull_secret'],
                                            base_dns_domain=env_variables['base_domain'],
                                            vip_dhcp_allocation=env_variables['vip_dhcp_allocation'])
            clusters.append(res)
            return res

        yield get_cluster_func
#TODO see how to do this
        # for cluster in clusters:
        #     with suppress(ApiException):
        #         api_client.delete_cluster(cluster.id)

    @pytest.mark.regression
    def test_user_authorization(self, api_client, node_controller, cluster):
        client_user1 = api_client()
        client_user2 = api_client(offline_token=env_variables['second_offline_token'])

        cluster_id = cluster(client_user1, env_variables['cluster_name']).id
#TODO move to assert_404 mthod
        #Try to fetch user1's cluster with user2's credentials 
        with pytest.raises(ApiException) as response:
            client_user2.cluster_get(cluster_id)
        assert response.value.status == 404
        assert response.value.reason == "Not Found"

        #user1 cluster is not seen by user2
        user2_clusters = client_user2.clusters_list()
        assert not list(filter(lambda cluster: cluster['id'] == cluster_id, user2_clusters))

#TODO negative negative, reomve
        #user1 cluster is not seen by user2
        user1_clusters = client_user1.clusters_list()
        assert not list(filter(lambda cluster: cluster['id'] == cluster_id, user1_clusters))

        #user2 cannot delete user1's cluster
        with pytest.raises(ApiException) as response:
            client_user2.delete_cluster(cluster_id)
        assert response.value.status == 404
        assert response.value.reason == "Not Found"

        #user2 cannot generate ISO user1's cluster
        with pytest.raises(ApiException) as response:
            self.generate_and_download_image(cluster_id, client_user2)
        assert response.value.status == 404
        assert response.value.reason == "Not Found"


        


        