import unittest
import array

from pyVmomi import vim

from Proxy import Proxy
from Configuration import Configuration

class TestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(target):
        target.config = Configuration()

        target.proxy = Proxy()
        target.proxy.connect(target.config)

    def test_suite(self):
        steps = ['create', 'start', 'stop', 'destroy']
        for i, name in enumerate(steps):
            print(name)
            try:
                step = getattr(self, 'step_' + name)
                step()

            except Exception as e:
                self.fail("{0} failed ({1}: {2})".format(step, type(e), e))


    def step_create(self):
        vm_template = self.proxy.fetch([vim.VirtualMachine], self.config.vcenter_test_template)

        self.assertTrue(vm_template != None)

        print("Found Template > {0}".format(vm_template.name))

        vm_name = self.config.vcenter_test_virtual_machine

        vm_memory = 1024
        vm_config_spec = vim.vm.ConfigSpec(numCPUs=1, memoryMB=vm_memory)

        vm_adapter_mapping = vim.vm.customization.AdapterMapping()
        vm_adapter_mapping.adapter = vim.vm.customization.IPSettings(ip=vim.vm.customization.DhcpIpGenerator(), dnsDomain=self.config.vcenter_test_domain)

        vm_global_ip = vim.vm.customization.GlobalIPSettings()
        vm_identity = vim.vm.customization.LinuxPrep(domain=self.config.vcenter_test_domain, hostName=vim.vm.customization.FixedName(name=vm_name))

        vm_custom_spec = vim.vm.customization.Specification(nicSettingMap=[vm_adapter_mapping], globalIPSettings=vm_global_ip, identity=vm_identity)

        vm_resource_pool = self.proxy.fetch([vim.ResourcePool], self.config.vcenter_test_resource_pool)

        vm_relocate_spec = vim.vm.RelocateSpec(pool=vm_resource_pool)

        # vm_clone_space = vim.vm.CloneSpec(powerOn=True, template=False, location=vm_relocate_spec, customization=vm_custom_spec, config=vm_config_spec)
        vm_clone_space = vim.vm.CloneSpec(powerOn=False, template=False, location=vm_relocate_spec, customization=None, config=vm_config_spec)

        print("Launch Clone Task for {0}".format(vm_name))
        task_clone = vm_template.Clone(name=vm_name, folder=vm_template.parent, spec=vm_clone_space)
        self.proxy.wait([task_clone])
        print("Task Complete > state={0}".format(task_clone.info.state))

        self.assertTrue(task_clone.info.state == Proxy.State.success)

    def step_power_on(self):
        vm = self.proxy.fetch([vim.VirtualMachine], self.config.vcenter_test_virtual_machine)

        self.assertTrue(vm != None)

        print("Found VM > {0}".format(vm.name))

        print("VM Power State > {0}".format(vm.runtime.powerState))

        self.assertTrue(format(vm.runtime.powerState) != "poweredOn")

        print("Launch Power On Task on {0}".format(vm.name))
        task_power_on = vm.PowerOnVM_Task()
        self.proxy.wait([task_power_on])
        print("Task Complete > state={0}".format(task_power_on.info.state))

        self.assertTrue(task_power_on.info.state == Proxy.State.success)

    def step_power_off(self):
        vm = self.proxy.fetch([vim.VirtualMachine], self.config.vcenter_test_virtual_machine)

        self.assertTrue(vm != None)

        print("Found VM > {0}".format(vm.name))

        print("VM Power State > {0}".format(vm.runtime.powerState))

        self.assertTrue(format(vm.runtime.powerState) != "poweredOff")

        print("Launch Power Off Task on {0}".format(vm.name))
        task_power_off = vm.PowerOffVM_Task()
        self.proxy.wait([task_power_off])
        print("Task Complete > state={0}".format(task_power_off.info.state))

        self.assertTrue(task_power_off.info.state == Proxy.State.success)


    def step_destroy(self):

        vm = self.proxy.fetch([vim.VirtualMachine], self.config.vcenter_test_virtual_machine)

        self.assertTrue(vm != None)

        print("Found VM > {0}".format(vm.name))

        print("VM Power State > {0}".format(vm.runtime.powerState))

        self.assertTrue(format(vm.runtime.powerState) == "poweredOff")

        print("Launch Destroy Task on {0}".format(vm.name))
        task_destroy = vm.Destroy_Task()
        self.proxy.wait([task_destroy])
        print("Task Complete > state={0}".format(task_destroy.info.state))

        self.assertTrue(task_destroy.info.state == Proxy.State.success)


