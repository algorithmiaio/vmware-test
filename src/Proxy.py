import requests
import os

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

    def download(self, url, params, destination):
        # Set headers
        headers = {'Content-Type': 'application/octet-stream'}

        # Create cookie
        cookie_parts = (self.service_instance._stub.cookie).split('=')

        cookie_name = cookie_parts[0]
        cookie_split = cookie_parts[1].split(';')

        cookie_value = cookie_split[0]

        cookie_path_split = cookie_split[1].split(";")
        cookie_path = cookie_path_split[0].lstrip()

        cookies = {cookie_name: " {0}; ${1}".format(cookie_value, cookie_path)}

        # Fetch file contents
        result = requests.get(url, params=params, headers=headers,cookies=cookies, allow_redirects=True)

        # Create any missing parent directories
        if not os.path.exists(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination))

        # Write to file
        open(destination, 'wb').write(result.content)


    def createOvfDescriptor(self, target, files):
        ovf_parameters = vim.OvfManager.CreateDescriptorParams()
        ovf_parameters.name = target.name
        ovf_parameters.ovfFiles = files

        return self.service_instance.content.ovfManager.CreateDescriptor(obj=target, cdp=ovf_parameters)

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
