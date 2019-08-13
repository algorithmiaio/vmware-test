import unittest
import array

from pyVmomi import vim

from helpers.Proxy import Proxy
from helpers.Configuration import Configuration

class StopVirtualMachine(unittest.TestCase):

    def test_action(self):
        config = Configuration()

        proxy = Proxy()
        proxy.connect(config)

        vm = proxy.fetch([vim.VirtualMachine], config.vcenter_test_virtual_machine)

        self.assertTrue(vm != None)

        print("Found VM > {0}".format(vm.name))

        print("VM Power State > {0}".format(vm.runtime.powerState))

        self.assertTrue(format(vm.runtime.powerState) != "poweredOff")

        print("Launch Power Off Task on {0}".format(vm.name))
        task_power_off = vm.PowerOffVM_Task()
        proxy.wait([task_power_off])
        print("Task Complete > state={0}".format(task_power_off.info.state))

        self.assertTrue(task_power_off.info.state == Proxy.State.success)

