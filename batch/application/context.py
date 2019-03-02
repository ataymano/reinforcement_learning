import azureml.core
from azureml.core import Workspace, Datastore

class Context:
    def __init__(self, accountName, accountKey, appId, appFolder):
        self.accountName = accountName
        self.accountKey = accountKey
        self.appId = appId
        self.appFolder = appFolder 

    def _datastore_name(self):
        return self.accountName + self.appId.replace('-', '')

    def get_datastore(self, workspace):
        name = self._datastore_name()
        if name in workspace.datastores:
            print("Data store for the app context {" + name + "} is found")
            return workspace.datastores[name]
            
        print("Registering datastore for {" + name + "}")
        return Datastore.register_azure_blob_container(workspace = workspace,
                                            datastore_name=name,
                                            container_name=self.appId,
                                            account_name=self.accountName,
                                            account_key=self.accountKey,
                                            create_if_not_exists=False
                                            )