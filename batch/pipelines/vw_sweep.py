import application
from application import context

import helpers
from helpers import compute

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
from azureml.data.data_reference import DataReference
from azureml.pipeline.steps import PythonScriptStep, DataTransferStep

import datetime
import os

def create_pipeline(ws, ctx, node_count, process_per_node):
    extractStep = extract_step.extract_step(
        workspace = ws,
        context = ctx
    )

    trainStep = vw_train_step.vw_train_step(
        workspace = ws,
        input_folder = extractStep.output,
    )
#    mpiStep = vw_mpi_step.vw_mpi_step(
#        workspace=ws,
#        input_folder = extractStep.output,
#        node_count = node_count,
#        process_per_node = process_per_node)

    sweep_pipeline = Pipeline(workspace=ws, steps=[trainStep])
    print ("VwTrainPipeline is succesfully created.")

    sweep_pipeline.validate()
    print("VwTrainPipeline is succesfully validated.")

    return sweep_pipeline        