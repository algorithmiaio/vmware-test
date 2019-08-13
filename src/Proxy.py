import ssl

from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect

class Proxy():

    class State():
        success = vim.TaskInfo.State.success
        error = vim.TaskInfo.State.error

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
        print("vcenter_test_template: {0}".format(config.vcenter_test_template))
        print("vcenter_test_domain: {0}".format(config.vcenter_test_domain))
        print("vcenter_test_resource_pool: {0}".format(config.vcenter_test_resource_pool))

        try:
            self.service_instance = SmartConnect(
                host=config.vcenter_host,
                port=config.vcenter_port,
                user=config.vcenter_username,
                pwd=config.vcenter_password
                sslContext=ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            )

            self.connected = True

        except IOError as error:
            print("IOError: {0}".format(error))
            self.connected = False

            raise

    def disconnect(self):
        if self.connected:
            self.connected = False
            Disconnect(self.service_instance)

    def fetch(self, object_type, object_name):
        fetched = None

        content = self.service_instance.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, object_type, True)

        for c in container.view:
            if c.name == object_name:
                fetched = c
                break

        return fetched

    def wait(self, tasks):
        collector = self.service_instance.content.propertyCollector
        queue = [str(task) for task in tasks]

        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = [vmodl.query.PropertyCollector.ObjectSpec(obj=task) for task in tasks]
        filter_spec.propSet = [vmodl.query.PropertyCollector.PropertySpec(type=vim.Task, pathSet=[], all=True)]

        collector_filter = collector.CreateFilter(filter_spec, True)

        try:
            version, state = None, None

            while len(queue):
                update = collector.WaitForUpdates(version)

                for filter_set in update.filterSet:
                    for obj_set in filter_set.objectSet:
                        task = obj_set.obj
                        for change in obj_set.changeSet:
                            if change.name == 'info':
                                state = change.val.state
                            elif change.name == 'info.state':
                                state = change.val
                            else:
                                continue

                            if not str(task) in queue:
                                continue

                            if state in [Proxy.State.success, Proxy.State.error]:
                                queue.remove(str(task))

                version = update.version

        finally:
            if collector_filter:
                collector_filter.Destroy()
