import pytest

from tests.base_test import BaseTest

NODE = 'master-0-0'


class TestWrongBootOrder(BaseTest):
    @pytest.mark.regression
    def test_wrong_boot_order_one_master(self, api_client, node_controller):
        # Define new cluster
        cluster_id = self.create_cluster(api_client=api_client).id
        # Generate and download cluster ISO
        self.generate_and_download_image(cluster_id=cluster_id, api_client=api_client)
        # Change boot order of master-0-0 TODO
        node_controller.set_boot_order_to_node(vm_name=NODE, cd_first=True)
        # Boot nodes into ISO
        node_controller.start_all_nodes()
        # Wait until hosts are discovered and update host roles
        self.wait_until_hosts_are_discovered(cluster_id=cluster_id, api_client=api_client)
        self.set_host_roles(cluster_id=cluster_id, api_client=api_client)
        self.set_network_params(cluster_id=cluster_id,
                                api_client=api_client,
                                controller=node_controller
                                )
        # Start cluster install
        self.start_cluster_install(cluster_id=cluster_id, api_client=api_client)
        # Cancel cluster install once cluster installation start
        self.wait_for_installing_in_progress(cluster_id=cluster_id, api_client=api_client)
        # self.wait_for_wrong_boot_order(cluster_id=cluster_id, api_client=api_client)
        # Reboot required nodes into ISO
        # self.reboot_nodes_into_iso_after_wrong_boot_order()
        # Wait for host to keep installing
        # self.wait_until_host_in_status()
        # wait until all nodes are in Installed status, will fail in case one host in error
        # self.wait_for_nodes_to_install(cluster_id=cluster_id, api_client=api_client)
        # self.wait_for_cluster_to_install(cluster_id=cluster_id, api_client=api_client)
