from vowpalwabbit import pyvw
from azure.storage.blob import BlockBlobService
import numpy as np
import azureml.dataprep as dprep
import os
import datetime

class AzureBlobFile:
    def __init__(self, block_blob_service, container, path, tmp_folder, logger):
        self.bbs = block_blob_service
        self.container = container
        self.path = path
        self.local_path = os.path.join(tmp_folder, self.path)
        self.logger = logger
        os.makedirs(os.path.dirname(self.local_path), exist_ok = True)
        if not os.path.isfile(self.local_path):
            self._download()

    def _download(self):
        self.logger.info('Downloading: ' + self.path)
        self.bbs.get_blob_to_path(self.container, self.path, self.local_path, max_connections=4)
        self.logger.info('Downloaded.')

    def get(self):
        return self.local_path

class TenantStorageClient:
    def __init__(self, context, tmp_folder, logger, converter = None):
        self.bbs = BlockBlobService(
            account_name = context.account_name,
            account_key = context.account_key)
        self.container = context.container
        self.folder = context.folder + '/' + 'data'
        self.tmp_folder = tmp_folder
        self.logger = logger
        self.vw = pyvw.vw('--cb_adf --dsjson')

    @staticmethod
    def _get_log_relative_path(date):
        return '%s/%s/%s_0.json' % (
            str(date.year),
            str(date.month).zfill(2),
            str(date.day).zfill(2)
        )

    @staticmethod
    def _get_cb_label(vw_ex, result):
        for i in range(1, len(vw_ex)):
            if vw_ex[i].get_cbandits_num_costs() == 1:
                result[i-1, 0] = vw_ex[i].get_cbandits_cost(0)
                result[i-1, 1] = vw_ex[i].get_cbandits_probability(0)
        return result

    @staticmethod
    def _to_sparse_single(vw_ex, shape, values, index1, index2):
        for i in range(0, vw_ex.num_namespaces()):
            for j in range(0, vw_ex.num_features_in(i)):
                shape.append([index1, index2, vw_ex.namespace(i), vw_ex.feature(i, j)])
                values.append(vw_ex.feature_weight(i, j))

    @staticmethod
    def _to_sparse(vw_ex, shape, values, index):
        for i in range(0, len(vw_ex)):
            TenantStorageClient._to_sparse_single(vw_ex[i], shape, values, index, i)

    @staticmethod
    def _to_dense_single(vw_ex, result):
        for i in range(1, vw_ex.num_namespaces() - 1):
            print(vw_ex.namespace(i))
            for j in range(0, vw_ex.num_features_in(i)):
                print(vw_ex.feature(i, j))
                result[i, vw_ex.feature(i, j)] = vw_ex.feature_weight(i, j)

    @staticmethod
    def _to_dense(vw_ex, result):
        for i in range(0, len(vw_ex)):
            TenantStorageClient._to_dense_single(vw_ex[i], result[i, :, :])

    def range_days(self, start_date, end_date):
        for i in range((end_date - start_date).days + 1):
            current_date = start_date + datetime.timedelta(i)
            log_relative_path = TenantStorageClient._get_log_relative_path(
                current_date
            )
            log_path = self.folder + '/' + log_relative_path
            for blob in self.bbs.list_blobs(self.container, prefix = log_path):
                yield AzureBlobFile(self.bbs, self.container, log_path, self.tmp_folder, self.logger)

        return
        yield

    def range_lines(self, start_date, end_date, batch_size = 1):
        index = 0
        result = [None] * batch_size
        for path in self.range_days(start_date, end_date):
            for line in open(path.get(), 'r', encoding='utf-8'):
                if line.startswith('{"_label_cost'):
                    result[index] = line
                    index = (index + 1) % batch_size
                    if index == 0:
                        yield line
        if index > 0: yield result[0:index]
        return
        yield

    #returns tuple of (features, labels)
    # features: batch_size x actions x namespaces x features
    # labels: batch_size x actions x 2
    def range_dense(self, start_date, end_date, actions, batch_size = 1):
        index = 0
        result = (np.zeros((batch_size, actions, 256, self.vw.num_weights()), dtype = float),
            np.zeros((batch_size, actions - 1, 2), dtype = float))

        for path in self.range_days(start_date, end_date):
            for line in open(path.get(), 'r', encoding='utf-8'):
                if line.startswith('{"_label_cost'):
                    examples = self.vw.parse(line)
                    TenantStorageClient._to_dense(examples, result[0][index, :, :, :])
                    TenantStorageClient._get_cb_label(examples, result[1][index, :, :])
                    index = (index + 1) % batch_size
                    if index == 0:
                        yield result
        
        if index > 0: yield (result[0][0:index], result[1][0:index])
        return
        yield

    #returns tuple of (features_idx, features_values, labels)
    # features_idx, features_values: sparse representation of  
    # features: batch_size x actions x namespaces x features
    # labels: batch_size x actions x 2
    def range_sparse(self, start_date, end_date, actions, batch_size = 1):
        index = 0
        result = ([], [],
            np.zeros((batch_size, actions - 1, 2), dtype = float))

        for path in self.range_days(start_date, end_date):
            for line in open(path.get(), 'r', encoding='utf-8'):
                if line.startswith('{"_label_cost'):
                    examples = self.vw.parse(line)
                    TenantStorageClient._to_sparse(examples, result[0], result[1], index)
                    TenantStorageClient._get_cb_label(examples, result[2][index, :, :])
                    index = (index + 1) % batch_size
                    if index == 0:
                        yield result
        
        if index > 0: yield (result[0][0:index], result[1][0:index])
        return
        yield

    def deploy(self, model):
        self.bbs.create_blob_from_path(self.container, 'exported-models/current', model, max_connections=4)
        self.bbs.create_blob_from_path(self.container, 'exported-models/currenttrainer', model, max_connections=4)
