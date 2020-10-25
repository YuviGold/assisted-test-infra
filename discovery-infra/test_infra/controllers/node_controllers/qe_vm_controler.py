import logging
import tempfile
from xml.dom import minidom

from test_infra import utils
from test_infra.controllers.node_controllers.libvirt_controller import LibvirtController


class QeVmController(LibvirtController):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def format_node_disk(self, node_name):
        logging.info("Formating disk for %s", node_name)
        command = f"qemu-img info /var/lib/libvirt/images/linchpin/{node_name}.qcow2 | grep 'virtual size'"
        output = utils.run_command(command, shell=True)        
        image_size = output[0].split(' ')[2]

        command = f'qemu-img create -f qcow2 /var/lib/libvirt/images/linchpin/{node_name}.qcow2 {image_size}'
        utils.run_command(command, shell=True)

    def get_ingress_and_api_vips(self):
        return {"api_vip": "192.168.123.5", "ingress_vip": "192.168.123.10"}

    def set_boot_order_to_node(self, vm_name, cd_first=False):
        logging.info("Setting the following boot order: cd_first:%s", cd_first)
        logging.info("Bringing down vm: %s", vm_name)
        self.shutdown_node(vm_name)
        command = f"virsh dumpxml {vm_name}"
        current_xml = utils.run_command(command, shell=True)
        dom = minidom.parseString(current_xml)
        os_element = dom.getElementsByTagName('os')[0]
        for el in os_element.getElementsByTagName('boot'):
            dev = el.getAttribute('dev')
            if dev in ['cdrom', 'hd']:
                os_element.removeChild(el)
            else:
                raise ValueError(f'Found unexpected boot device: \'{dev}\'')
        dom = dom.toprettyxml()
        first = dom.createElement('boot')
        first.setAttribute('dev', 'cdrom' if cd_first else 'hd')
        os_element.appendChild(first)
        second = dom.createElement('boot')
        second.setAttribute('dev', 'hd' if cd_first else 'cdrom')
        os_element.appendChild(second)
        with tempfile.NamedTemporaryFile() as f:
            f.write(dom)
            f.seek(0)
            command = f"virsh define {f.name}"
            utils.run_command(command=command, shell=True)
        self.start_node(vm_name)
