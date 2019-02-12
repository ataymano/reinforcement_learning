import application
from application import context

import helpers
from helpers import compute

import steps
from steps import extract_step
from steps import vw_train_step
from steps import deployment_step

import azureml.core
from azureml.core import Workspace, Experiment, Datastore
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import Pipeline, PipelineData

import datetime


def create_pipeline(ws, ctx):
    ds = Datastore.register_azure_blob_container(workspace = ws,
                                            datastore_name='app_storage',
                                            container_name=ctx.appId,
                                            account_name=ctx.accountName,
                                            account_key=ctx.accountKey,
                                            create_if_not_exists=False
                                            )

    train_target = compute.get_or_create_aml_compute_target(ws, 'train-compute-0')
    aml_compute = compute.get_or_create_aml_compute_target(ws, 'aml-compute-0')
    adf_compute = compute.get_or_create_data_factory(ws, 'adf-compute-0')

    blob_input_data = DataReference(
        datastore=ds,
        data_reference_name="batch",
        path_on_datastore=ctx.appFolder)
    print("Input batch data reference object created")

    output_data = PipelineData("output_data", datastore=ws.get_default_datastore())
    intermediate_data = PipelineData("intermediate_data", datastore=ws.get_default_datastore())
    print("PipelineData object created")

    model_data = DataReference(
        datastore=ws.get_default_datastore(),
        data_reference_name="model",
        path_on_datastore="exported-models")

    extractStep = extract_step.extract_step(
        input_folder = blob_input_data,
        output_folder = intermediate_data,
        compute = aml_compute
    )
    print("extractStep created")

    trainStep = vw_train_step.vw_train_step(
        input_folder = intermediate_data,
        output_folder = output_data,
        compute = train_target
    )
    print("trainStep created")

    import datetime
    deploymentStep = deployment_step.deployment_step(
        input_folder = output_data,
        output_folder = model_data,
        compute = adf_compute
    )
    print("deploymentStep created")

    train_pipeline = Pipeline(workspace=ws, steps=[deploymentStep])
    print ("Train Pipeline is built")

    train_pipeline.validate()
    print("Simple validation complete")

    return train_pipeline        