import os

class Configuration():

    def __init__(self):
        self.vcenter_host = os.getenv('VCENTER_HOST', '127.0.0.1')
        self.vcenter_port = os.getenv('VCENTER_PORT', 443)
        self.vcenter_username = os.getenv('VCENTER_USERNAME', 'root')
        self.vcenter_password = os.getenv('VCENTER_PASSWORD', '')
        self.vcenter_test_prefix = os.getenv('VCENTER_TEST_PREFIX', '')
        self.vcenter_test_template = self.vcenter_test_prefix + os.getenv('VCENTER_TEST_TEMPLATE', 'default')
        self.vcenter_test_domain = self.vcenter_test_prefix + os.getenv('VCENTER_TEST_DOMAIN', 'vmware-testing.local')
        self.vcenter_test_resource_pool = self.vcenter_test_prefix + os.getenv('VCENTER_TEST_RESOURCE_POOL', 'vmware-testing-resource-pool')
        self.vcenter_test_virtual_machine = self.vcenter_test_prefix + os.getenv('VCENTER_TEST_VIRTUAL_MACHINE', 'vmware-testing-virtual-machine')
