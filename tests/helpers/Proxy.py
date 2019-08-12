from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

class Proxy():
    def __init__(self):
        self.connected = False

    def __del__(self):
        self.disconnect()

    def connect(self, config):
        print("vcenter_host: {0}".format(config.vcenter_host))
        print("vcenter_port: {0}".format(config.vcenter_port))
        print("vcenter_username: {0}".format(config.vcenter_username))
        print("vcenter_password: {0}".format(config.vcenter_password))
        print("vcenter_test_prefix: {0}".format(config.vcenter_test_prefix))
        print("vcenter_test_domain: {0}".format(config.vcenter_test_domain))
        print("vcenter_test_resource_pool: {0}".format(config.vcenter_test_resource_pool))

        try:
            self.si = SmartConnect(host=config.vcenter_host, port=config.vcenter_port, user=config.vcenter_username, pwd=config.vcenter_password)
            self.connected = True

        except IOError as error:
            print("IOError: {0}".format(error))
            self.connected = False

            raise

    def disconnect(self):
        if self.connected:
            self.connected = False
            Disconnect(self.si)

    def fetch(self, object_type, object_name):
        fetched = None

        content = self.si.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, object_type, True)

        for c in container.view:
            if c.object_name == object_name:
                fetched = c
                break

        return fetched
