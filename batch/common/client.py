import tempfile
from common.parser import DSJsonParser
from azure.storage.blob import BlockBlobService
import datetime
import os


class _AzureBlobIterator:
    def __init__(self, block_blob_service, container, path):
        self.bbs = block_blob_service
        self.container = container
        self.path = path
        self.local_copy = os.path.join(tempfile.mkdtemp(), "file.json")
        self.bbs.get_blob_to_path(self.container, self.path, self.local_copy, max_connections=4)

    def iterate(self):
        for line in open(self.local_copy, 'r', encoding='utf-8'):
            if line.startswith('{"_label_cost'):
                yield line


class TenantStorageClient:
    def __init__(self, context):
        self.context = context
        self.bbs = BlockBlobService(
            account_name=context.account_name,
            account_key=context.account_key
        )

    def _date_2_path(self, date):
        return '%s/data/%s/%s/%s_0.json' % (
            self.context.folder,
            str(date.year),
            str(date.month).zfill(2),
            str(date.day).zfill(2)
        )

    def _iterate_lines(self, start, end):
        for i in range((end - start).days + 1):
            current = _AzureBlobIterator(
                self.bbs,
                self.context.container,
                self._date_2_path(start + datetime.timedelta(i)))
            for line in current.iterate():
                yield line

    def iterate(self, start, end, batch_size):
        result = []
        i = 0
        for line in self._iterate_lines(start, end):
            result.append(line)
            i = (i + 1) % batch_size
            if i == 0:
                yield result
                result = []

        yield result


class DSJsonLogsClient:
    def __init__(self, context, problem, is_dense):
        self.parser = DSJsonParser(problem, is_dense)
        self.client = TenantStorageClient(context)

    def iterate(self, start, end, batch_size):
        for lines in self.client.iterate(start, end, batch_size):
            yield map(lambda l: self.parser.parse(l), lines)

