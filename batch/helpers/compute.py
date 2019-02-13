import azureml.core
from azureml.core.compute_target import ComputeTargetException
from azureml.core.compute import AmlCompute
from azureml.core.compute import ComputeTarget, BatchCompute, DataFactoryCompute

def get_or_create_aml_compute_target(ws, name, vm_size = "STANDARD_D2_v2", max_nodes = 1):
    try:
        cluster = AmlCompute(ws, name)
        print("Found existing cluster: " + name)
        return cluster
    except ComputeTargetException:
        print("Creating new AmlCompute cluster: " + name)
        provisioning_config = AmlCompute.provisioning_configuration(vm_size = vm_size,
                                                                    max_nodes = max_nodes)

        # create the cluster
        cluster = ComputeTarget.create(ws, name, provisioning_config)
        cluster.wait_for_completion(show_output=True)
        return cluster

def get_or_create_data_factory(ws, name):
    try:
        return DataFactoryCompute(ws, name)
    except ComputeTargetException as e:
        if 'ComputeTargetNotFound' in e.message:
            print('Data factory "' + name + '" is not found, creating...')
            provisioning_config = DataFactoryCompute.provisioning_configuration()
            data_factory = ComputeTarget.create(ws, name, provisioning_config)
            data_factory.wait_for_completion()
            return data_factory
        else:
            raise e      

def get_or_create_batch_compute(ws, name, batch_resource_group, batch_account_name):
    try:
        # check if already attached
        batch_compute = BatchCompute(ws, name)
        print('Batch compute is found: ' + name)
        return batch_compute
    except ComputeTargetException:
        print('Attaching Batch compute: ' + name)
        provisioning_config = BatchCompute.attach_configuration(resource_group=batch_resource_group, account_name=batch_account_name)
        batch_compute = ComputeTarget.attach(ws, name, provisioning_config)
        batch_compute.wait_for_completion()
        print("Provisioning state:{}".format(batch_compute.provisioning_state))
        print("Provisioning errors:{}".format(batch_compute.provisioning_errors))
        return batch_compute