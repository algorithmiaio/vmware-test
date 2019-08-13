import unittest
import array

from pyVmomi import vim

from helpers.Proxy import Proxy
from helpers.Configuration import Configuration

class StartVirtualMachine(unittest.TestCase):

    def test_action(self):
        config = Configuration()

        proxy = Proxy()
        proxy.connect(config)

        vm = proxy.fetch([vim.VirtualMachine], config.vcenter_test_virtual_machine)

        self.assertTrue(vm != None)

        print("Found VM > {0}".format(vm.name))

        print("VM Power State > {0}".format(vm.runtime.powerState))

        self.assertTrue(format(vm.runtime.powerState) != "poweredOn")

        print("Launch Power On Task on {0}".format(vm.name))
        task_power_on = vm.PowerOnVM_Task()
        proxy.wait([task_power_on])
        print("Task Complete > state={0}".format(task_power_on.info.state))

        self.assertTrue(task_power_on.info.state == Proxy.State.success)
