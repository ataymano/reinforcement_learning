import azureml.core
from azureml.core.compute_target import ComputeTargetException
from azureml.core.compute import AmlCompute
from azureml.core.compute import ComputeTarget, DataFactoryCompute

def get_or_create_aml_compute_target(ws, name, vm_size = "STANDARD_D2_v2", max_nodes = 1):
    try:
        cluster = AmlCompute(ws, name)
        print("found existing cluster.")
        return cluster
    except ComputeTargetException:
        print("creating new cluster")
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
            print('Data factory not found, creating...')
            provisioning_config = DataFactoryCompute.provisioning_configuration()
            data_factory = ComputeTarget.create(ws, name, provisioning_config)
            data_factory.wait_for_completion()
            return data_factory
        else:
            raise e      