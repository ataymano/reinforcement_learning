class Context:
    def __init__(self, account_name, account_key, container, folder):
        self.account_name = account_name
        self.account_key = account_key
        self.container = container
        self.folder = folder
    
    def GetBlockBlobService(self):
        from azure.storage.blob import BlockBlobService
        return BlockBlobService(
            account_name=self.account_name,
            account_key=self.account_key
        )

    def deploy_model(self, model_path):
        service = self.GetBlockBlobService()
        service.create_blob_from_path(container_name=self.container, blob_name='current', file_path=model_path)