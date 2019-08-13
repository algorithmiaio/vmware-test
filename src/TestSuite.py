import unittest
import array
import time

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
            try:
                print("\nStep {0} Start".format(name))
                step = getattr(self, 'step_' + name)
                step()
                print("Step {0} End".format(name))

            except Exception as e:
                self.fail("{0} failed ({1}: {2})".format(step, type(e), e))


    def step_create(self):
        vm_template = self.proxy.fetch([vim.VirtualMachine], self.config.vcenter_test_template)

        self.assertTrue(vm_template != None)

        print("Found Virtual Machine Template > {0}".format(vm_template.name))

        vm_name = self.config.vcenter_test_virtual_machine

        vm_config_spec = vim.vm.ConfigSpec(numCPUs=1, memoryMB=1024)

        vm_resource_pool = self.proxy.fetch([vim.ResourcePool], self.config.vcenter_test_resource_pool)

        vm_relocate_spec = vim.vm.RelocateSpec(pool=vm_resource_pool)

        vm_clone_space = vim.vm.CloneSpec(powerOn=False, template=False, location=vm_relocate_spec, customization=None, config=vm_config_spec)

        print("Launch Clone Task for {0}".format(vm_name))
        task_clone = vm_template.Clone(name=vm_name, folder=vm_template.parent, spec=vm_clone_space)
        self.proxy.wait([task_clone])
        print("Task Complete > state={0}".format(task_clone.info.state))

        self.assertTrue(task_clone.info.state == Proxy.State.success)

    def step_attach_disk(self):
        vm = self.proxy.fetch([vim.VirtualMachine], self.config.vcenter_test_virtual_machine)

        self.assertTrue(vm != None)

        print("Found Virtual Machine > {0}".format(vm.name))

        print("VM Power State > {0}".format(vm.runtime.powerState))

        vm_config_spec = vim.vm.ConfigSpec()

        vm_controller = None
        vm_device_unit_number = 0
        for vm_device in vm.config.hardware.device:
            if hasattr(vm_device.backing, 'fileName'):
                vm_device_unit_number = int(vm_device.unitNumber) + 1
                if vm_device_unit_number == 7:
                    vm_device_unit_number += 1

            if isinstance(vm_device, vim.vm.device.VirtualSCSIController):
                vm_controller = vm_device

        self.assertTrue(vm_device_unit_number < 16)

        vm_disk_spec = vim.vm.device.VirtualDeviceSpec()

        vm_disk_spec.fileOperation = "create"
        vm_disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        vm_disk_spec.device = vim.vm.device.VirtualDisk()
        vm_disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        vm_disk_spec.device.backing.thinProvisioned = True

        vm_disk_spec.device.backing.diskMode = 'persistent'
        vm_disk_spec.device.unitNumber = vm_device_unit_number
        vm_disk_spec.device.capacityInKB = int(10) * 1024 * 1024
        vm_disk_spec.device.controllerKey = vm_controller.key

        vm_config_spec.deviceChange = [vm_disk_spec]

        # self.assertTrue(format(vm.runtime.powerState) != "poweredOn")

        print("Launch Reconfigure VM Task on {0}".format(vm.name))
        task_reconfigure_vm = vm.ReconfigVM_Task(spec=vm_config_spec)
        self.proxy.wait([task_reconfigure_vm])
        print("Task Complete > state={0}".format(task_reconfigure_vm.info.state))

        self.assertTrue(task_reconfigure_vm.info.state == Proxy.State.success)

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

        print("Found Virtual Machine > {0}".format(vm.name))

        print("VM Power State > {0}".format(vm.runtime.powerState))

        self.assertTrue(format(vm.runtime.powerState) != "poweredOff")

        print("Launch Power Off Task on {0}".format(vm.name))
        task_power_off = vm.PowerOffVM_Task()
        self.proxy.wait([task_power_off])
        print("Task Complete > state={0}".format(task_power_off.info.state))

        self.assertTrue(task_power_off.info.state == Proxy.State.success)

    def step_create_template(self):
        vm = self.proxy.fetch([vim.VirtualMachine], self.config.vcenter_test_virtual_machine)

        self.assertTrue(vm != None)

        print("Found Virtual Machine > {0}".format(vm.name))

        vm_template_name = self.config.vcenter_test_virtual_machine + '-template'

        vm_resource_pool = self.proxy.fetch([vim.ResourcePool], self.config.vcenter_test_resource_pool)

        vm_relocate_spec = vim.vm.RelocateSpec(pool=vm_resource_pool)

        vm_clone_space = vim.vm.CloneSpec(powerOn=False, template=True, location=vm_relocate_spec, customization=None)

        print("Launch Clone Task for {0}".format(vm_template_name))
        task_clone = vm.Clone(name=vm_template_name, folder=vm.parent, spec=vm_clone_space)
        self.proxy.wait([task_clone])
        print("Task Complete > state={0}".format(task_clone.info.state))

        self.assertTrue(task_clone.info.state == Proxy.State.success, "Task to clone VM failed.")

    def step_download_template(self):
        vm = self.proxy.fetch([vim.VirtualMachine], self.config.vcenter_test_virtual_machine)

        self.assertTrue(vm != None)

        print("Found Virtual Machine > {0}".format(vm.name))

        print("VM Power State > {0}".format(vm.runtime.powerState))

        self.assertTrue(format(vm.runtime.powerState) == "poweredOff")

        vm_ovf_files = []
        vm_http_lease = vm.ExportVm()

        try:

            while vm_http_lease.state == vim.HttpNfcLease.State.initializing:
                print "HTTP NFC Lease Initializing."
                time.sleep(2)

            if vm_http_lease.state != vim.HttpNfcLease.State.ready:
                print "HTTP NFC Lease error: {0}".format(vm_http_lease.state.error)

            for deviceUrl in vm_http_lease.info.deviceUrl:
                if not deviceUrl.targetId:
                    print("No targetId found for url: {0}.".format(deviceUrl.url))
                    continue

                export_path = "./export/" + deviceUrl.targetId

                print 'Downloading {0} to {1}'.format(deviceUrl.url, export_path)

                size = self.proxy.download(deviceUrl.url, export_path)

                print 'Creating OVF file for {0}'.format(export_path)

                vm_ovf_file = vim.OvfManager.OvfFile()
                vm_ovf_file.deviceId = deviceUrl.key
                vm_ovf_file.path = deviceUrl.targetId
                vm_ovf_file.size = size

                vm_ovf_files.append(vm_ovf_file)

            vm_descriptor = self.proxy(vm.name, vm_ovf_files)

            if vm_descriptor_result.error:
                raise vm_descriptor_result.error[0].fault

        finally:
            vm_http_lease.HttpNfcLeaseComplete()


    def step_destroy(self):

        vm = self.proxy.fetch([vim.VirtualMachine], self.config.vcenter_test_virtual_machine)

        self.assertTrue(vm != None)

        print("Found Virtual Machine > {0}".format(vm.name))

        print("VM Power State > {0}".format(vm.runtime.powerState))

        self.assertTrue(format(vm.runtime.powerState) == "poweredOff")

        print("Launch Destroy Task on {0}".format(vm.name))
        task_destroy = vm.Destroy_Task()
        self.proxy.wait([task_destroy])
        print("Task Complete > state={0}".format(task_destroy.info.state))

        self.assertTrue(task_destroy.info.state == Proxy.State.success)


