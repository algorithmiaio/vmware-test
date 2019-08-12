import os

class Configuration():

    def __init__(self):
        self.vcenter_host = os.getenv('VCENTER_HOST', '127.0.0.1')
        self.vcenter_port = os.getenv('VCENTER_HOST', 443)
        self.vcenter_username = os.getenv('VCENTER_USERNAME', 'root')
        self.vcenter_password = os.getenv('VCENTER_PASSWORD', '')
        self.vcenter_test_prefix = os.getenv('VCENTER_TEST_PREFIX', 'test')
        self.vcenter_test_template = os.getenv('VCENTER_TEST_TEMPLATE', 'centos-6.5-x64')
        self.vcenter_test_domain = os.getenv('VCENTER_TEST_DOMAIN', 'domain.local')
        self.vcenter_test_resource_pool = os.getenv('VCENTER_TEST_RESOURCE_POOL', 'DEV')
