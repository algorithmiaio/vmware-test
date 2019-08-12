import unittest

from pyVmomi import vim

from helpers.Proxy import Proxy
from helpers.Configuration import Configuration

class CreateVirtualMachine(unittest.TestCase):

    def test_action(self):
        config = Configuration()

        proxy = Proxy()
        proxy.connect(config)

        vm_template = proxy.fetch([vim.VirtualMachine], config.vcenter_test_template)

        vm_name = config.vcenter_test_prefix + '-' + 'create-virtual-machine'

        vm_memory = 1024
        vm_config_spec = vim.vm.ConfigSpec(numCPUs=1, memoryMB=vm_memory)

        vm_adapter_mapping = vim.vm.customization.AdapterMapping()
        vm_adapter_mapping.adapter = vim.vm.customization.IPSettings(ip=vim.vm.customization.DhcpIpGenerator(), dnsDomain=config.vcenter_test_domain)

        vm_global_ip = vim.vm.customization.GlobalIPSettings()
        vm_identity = vim.vm.customization.LinuxPrep(domain=config.vcenter_test_domain, hostName=vim.vm.customization.FixedName(name=vm_name))

        vm_custom_spec = vim.vm.customization.Specification(nicSettingMap=[vm_adapter_mapping], globalIPSettings=vm_global_ip, identity=vm_identity)

        vm_resource_pool = proxy.fetch([vim.ResourcePool], config.vcenter_test_resource_pool)

        vm_relocate_spec = vim.vm.RelocateSpec(pool=vm_resource_pool)

        vm_clone_space = vim.vm.CloneSpec(powerOn=True, template=False, location=vm_relocate_spec, customization=vm_custom_spec, config=vm_config_spec)

        vm = vm_template.Clone(name=vm_name, folder=vm_template.parent, spec=vm_clone_space)

        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")



