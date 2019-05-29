from azure.storage.blob import BlockBlobService
import azureml.dataprep as dprep
import os
import datetime

class AzureBlobFile:
    def __init__(self, block_blob_service, container, path, tmp_folder):
        self.bbs = block_blob_service
        self.container = container
        self.path = path
        self.local_path = os.path.join(tmp_folder, self.path)
        os.makedirs(os.path.dirname(self.local_path), exist_ok = True)
        self._download()

    def _download(self):
        self.bbs.get_blob_to_path(self.container, self.path, self.local_path, max_connections=4)

    def get(self):
        return self.local_path

class TenantStorageClient:
    def __init__(self, connection_string, container, folder, tmp_folder):
        self.bbs = BlockBlobService(connection_string = connection_string)
        self.container = container
        self.folder = os.path.join(folder, 'data')
        self.tmp_folder = tmp_folder

    @staticmethod
    def _get_log_relative_path(date):
        return '%s/%s/%s_0.json' % (
            str(date.year),
            str(date.month).zfill(2),
            str(date.day).zfill(2)
        )

    def range_days(self, start_date, end_date):
        for i in range((end_date - start_date).days + 1):
            current_date = start_date + datetime.timedelta(i)
            log_relative_path = TenantStorageClient._get_log_relative_path(
                current_date
            )
            log_path = self.folder + '/' + log_relative_path
            for blob in self.bbs.list_blobs(self.container, prefix = log_path):
                yield AzureBlobFile(self.bbs, self.container, log_path, self.tmp_folder)

        return
        yield

    def range_batches(self, start_date, end_date, batch_size):
        index = 0
        result = [None] * batch_size
        for path in self.range_days(start_date, end_date):
            for line in open(path.get(), 'r', encoding='utf-8'):
                if line.startswith('{"_label_cost'):
                    result[index] = line
                    index = (index + 1) % batch_size
                    if index == 0:
                        yield result

        return
        yield

    def deploy(self, model):
        self.bbs.create_blob_from_path(self.container, 'exported-models/current', model, max_connections=4)
        self.bbs.create_blob_from_path(self.container, 'exported-models/currenttrainer', model, max_connections=4)

