import application
from application import context

import helpers
from helpers import compute
from helpers import utils

import steps
from steps import extract_step
from steps import vw_train_step
from steps import deployment_step
from steps import add_label_step
from steps import vw_sweep_step
from steps import vw_cache_step, base_command_step, best_command_step, vw_predict_step, dashboard_step

import azureml.core
from azureml.core import Workspace, Experiment, Datastore
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.data.data_reference import DataReference
from azureml.pipeline.steps import PythonScriptStep, DataTransferStep
from azureml.train.hyperdrive import GridParameterSampling, choice
import datetime
import os

def create_pipeline(ws, ctx, power_t_range, parallel_jobs):
    baseCommandStep = base_command_step.base_command_step(
        workspace = ws
    )

    cacheStep = vw_cache_step.vw_cache_step(
        workspace = ws,
        context = ctx
    )

#    grid_1 = GridParameterSampling(
#        {
#            '--power_t': choice(1e-09, 1.4953487812212204e-07, 2.2360679774997894e-05, 0.0033437015248821097, 0.5),
#            '--l1': choice(1e-09, 1e-07, 1e-05, 0.001, 0.1),
#            '-l': choice(1e-05, 0.00036840314986403866, 0.013572088082974531, 0.5),
#            '--cb_type': choice('mtr', 'ips')
#        }
#    )

    grid_1 = GridParameterSampling(
        {
            '--power_t': choice(1e-09, 1.4953487812212204e-07),
            '--l1': choice(1e-09, 1e-07),
            '-l': choice(1e-05, 0.00036840314986403866),
            '--cb_type': choice('mtr', 'ips')
        }
    )


    sweep_Step_1 = vw_sweep_step.vw_sweep_step(
        workspace = ws,
        input_folder = cacheStep.output,
        base_command = baseCommandStep.output,
        param_grid = grid_1,  
        parallel_jobs = parallel_jobs,
        jobs_limit = 100
    )

    best_1 = best_command_step.best_command_step(
        workspace = ws,
        input = sweep_Step_1.output
    )

    predict_1 = vw_predict_step.vw_predict_step(
        workspace = ws,
        input_folder = cacheStep.output,
        command = best_1.output
    )

    dashboard = dashboard_step.dashboard_step(
        workspace = ws,
        context = ctx,
        predictions = predict_1.output
    )
#    mpiStep = vw_mpi_step.vw_mpi_step(
#        workspace=ws,
#        input_folder = extractStep.output,
#        node_count = node_count,
#        process_per_node = process_per_node)

    sweep_pipeline = Pipeline(workspace=ws, steps=[dashboard.step2])
    print ("VwTrainPipeline is succesfully created.")

    sweep_pipeline.validate()
    print("VwTrainPipeline is succesfully validated.")

    return sweep_pipeline        