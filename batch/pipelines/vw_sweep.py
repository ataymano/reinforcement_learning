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
from azureml.train.hyperdrive import GridParameterSampling, RandomParameterSampling, choice
import datetime
import os

def create_pipeline(ws, ctx, parallel_jobs):
    baseCommandStep = base_command_step.base_command_step(
        workspace = ws
    )

    extractStep = extract_step.extract_step(
        workspace = ws,
        context = ctx)

    cacheStep = vw_cache_step.vw_cache_step(
        workspace = ws,
        input = extractStep.output
    )

    grid_1 = RandomParameterSampling(
        {
            '--power_t': choice(0, 1e-3, 0.5),
            '--l1': choice(0, 1e-06, 1e-04, 1e-3),
            '-l': choice(1e-05, 1e-3, 1e-2, 1e-1, 0.5, 10),
            '--cb_type': choice('mtr', 'ips'),
            # '--with_marginal': choice(true, false)         
        }
    )

#Marginal:
#False
#True - {--marginal A}
#       {--marginal B}


#Quadratics:

    
#    grid_1 = GridParameterSampling(
#        {
#            '--power_t': choice(1e-09, 1.4953487812212204e-07),
#            '--l1': choice(1e-09, 1e-07),
#            '-l': choice(1e-05, 0.00036840314986403866),
#            '--cb_type': choice('mtr', 'ips')
#        }
#    )


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

    grid_2 = GridParameterSampling(
        {
            '--marginals_index': choice(0, 1),
            '--interactions_index': choice(0, 1, 2, 3, 4, 5, 6, 7)        
        }
    )

    sweep_Step_2 = vw_sweep_step.vw_sweep_step(
        workspace = ws,
        input_folder = cacheStep.output,
        base_command = best_1.output,
        param_grid = grid_2,  
        parallel_jobs = parallel_jobs,
        jobs_limit = 100
    )

    best_2 = best_command_step.best_command_step(
        workspace = ws,
        input = sweep_Step_2.output
    )

    predict_2 = vw_predict_step.vw_predict_step(
        workspace = ws,
        input_folder = cacheStep.output,
        command = best_2.output
    )

    dashboard = dashboard_step.dashboard_step(
        workspace = ws,
        data = extractStep.output,
        predictions = predict_2.output
    )

    sweep_pipeline = Pipeline(workspace=ws, steps=[dashboard])
    print ("VwTrainPipeline is succesfully created.")

    sweep_pipeline.validate()
    print("VwTrainPipeline is succesfully validated.")

    return sweep_pipeline        