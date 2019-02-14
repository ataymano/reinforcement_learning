import application
from application import context

import steps
from steps import extract_step
from steps import vw_train_step
from steps import deployment_step
from steps import add_label_step
from steps import vw_mpi_step

import azureml.core
from azureml.core import Workspace, Experiment, Datastore
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import Pipeline, PipelineData

import datetime


def create_pipeline(ws, ctx):
    extractStep = extract_step.extract_step(
        workspace = ws,
        context = ctx
    )

    addLabelStep = add_label_step.add_label_step(
        workspace = ws,
        input_folder = extractStep.output
    )

    trainStep = vw_train_step.vw_train_step(
        workspace = ws,
        input_folder = addLabelStep.output,
    )

    deploymentStep = deployment_step.deployment_step(
        workspace = ws,
        context = ctx,
        input_folder = trainStep.output
    )

    train_pipeline = Pipeline(workspace=ws, steps=[deploymentStep])
    print ("VwTrainPipeline is succesfully created.")

    train_pipeline.validate()
    print("VwTrainPipeline is succesfully validated.")

    return train_pipeline        