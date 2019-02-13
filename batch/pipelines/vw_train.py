import application
from application import context

import helpers
from helpers import compute

import steps
from steps import extract_step
from steps import vw_train_step
from steps import deployment_step
from steps import add_label_step

import azureml.core
from azureml.core import Workspace, Experiment, Datastore
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import Pipeline, PipelineData

import datetime


def create_pipeline(ws, ctx):
    train_target = compute.get_or_create_aml_compute_target(ws, 'train-compute-0')
    aml_compute = compute.get_or_create_aml_compute_target(ws, 'aml-compute-0')
    adf_compute = compute.get_or_create_data_factory(ws, 'adf-compute-0')

    model_data = DataReference(
        datastore=ctx.get_datastore(ws),
        data_reference_name="model",
        path_on_datastore="exported-models")

    extractStep = extract_step.extract_step(
        workspace = ws,
        context = ctx,
        compute = aml_compute
    )

    addLabelStep = add_label_step.add_label_step(
        workspace = ws,
        input_folder = extractStep.output,
        compute = aml_compute
    )

    trainStep = vw_train_step.vw_train_step(
        workspace = ws,
        input_folder = addLabelStep.output,
        compute = train_target
    )

    deploymentStep = deployment_step.deployment_step(
        workspace = ws,
        context = ctx,
        input_folder = trainStep.output,
        compute = adf_compute
    )

    train_pipeline = Pipeline(workspace=ws, steps=[deploymentStep])
    print ("VwTrainPipeline is succesfully created.")

    train_pipeline.validate()
    print("VwTrainPipeline is succesfully validated.")

    return train_pipeline        