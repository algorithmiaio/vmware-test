import unittest
import array

from pyVmomi import vim

from helpers.Proxy import Proxy
from helpers.Configuration import Configuration

class CreateVirtualMachine(unittest.TestCase):

    def test_action(self):
        config = Configuration()

        proxy = Proxy()
        proxy.connect(config)

        vm_template = proxy.fetch([vim.VirtualMachine], config.vcenter_test_template)

        self.assertTrue(vm_template != None)

        print("Found Template > {0}".format(vm_template.name))

        vm_name = config.vcenter_test_virtual_machine

        vm_memory = 1024
        vm_config_spec = vim.vm.ConfigSpec(numCPUs=1, memoryMB=vm_memory)

        vm_adapter_mapping = vim.vm.customization.AdapterMapping()
        vm_adapter_mapping.adapter = vim.vm.customization.IPSettings(ip=vim.vm.customization.DhcpIpGenerator(), dnsDomain=config.vcenter_test_domain)

        vm_global_ip = vim.vm.customization.GlobalIPSettings()
        vm_identity = vim.vm.customization.LinuxPrep(domain=config.vcenter_test_domain, hostName=vim.vm.customization.FixedName(name=vm_name))

        vm_custom_spec = vim.vm.customization.Specification(nicSettingMap=[vm_adapter_mapping], globalIPSettings=vm_global_ip, identity=vm_identity)

        vm_resource_pool = proxy.fetch([vim.ResourcePool], config.vcenter_test_resource_pool)

        vm_relocate_spec = vim.vm.RelocateSpec(pool=vm_resource_pool)

        # vm_clone_space = vim.vm.CloneSpec(powerOn=True, template=False, location=vm_relocate_spec, customization=vm_custom_spec, config=vm_config_spec)
        vm_clone_space = vim.vm.CloneSpec(powerOn=False, template=False, location=vm_relocate_spec, customization=None, config=vm_config_spec)

        print("Launch Clone Task for {0}".format(vm_name))
        task_clone = vm_template.Clone(name=vm_name, folder=vm_template.parent, spec=vm_clone_space)
        proxy.wait([task_clone])
        print("Task Complete > state={0}".format(task_clone.info.state))

        self.assertTrue(task_clone.info.state == Proxy.State.success)




