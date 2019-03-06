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
from steps import vw_cache_step, prepare_command_step, best_command_step, vw_predict_step, dashboard_step

import azureml.core
from azureml.core import Workspace, Experiment, Datastore
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.data.data_reference import DataReference
from azureml.pipeline.steps import PythonScriptStep, DataTransferStep
from azureml.train.hyperdrive import GridParameterSampling, RandomParameterSampling, choice
from azureml.pipeline.core.graph import PipelineParameter

import datetime
import os

def create_pipeline(ws, ctx, parallel_jobs):
    baseCommandStep = prepare_command_step.prepare_command_step(
        workspace = ws,
        command = PipelineParameter(name = "base_command", default_value = '--cb_adf --dsjson')
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

    grid_2 = GridParameterSampling(
        {
            '--marginals_index': choice(0, 1),
            '--interactions_index': choice(0, 1, 2, 3, 4, 5, 6, 7)        
        }
    )

    sweep_Step_2 = vw_sweep_step.vw_sweep_step(
        workspace = ws,
        input_folder = cacheStep.output,
        base_command = sweep_Step_1.output,
        param_grid = grid_2,  
        parallel_jobs = parallel_jobs,
        jobs_limit = 100
    )


    predict_1 = vw_predict_step.vw_predict_step(
        workspace = ws,
        input_folder = cacheStep.output,
        command = sweep_Step_1.output,
        name = 'Hyper1'
    )

    predict_2 = vw_predict_step.vw_predict_step(
        workspace = ws,
        input_folder = cacheStep.output,
        command = sweep_Step_2.output,
        name = 'Best'
    )

    predict_3 = vw_predict_step.vw_predict_step(
        workspace = ws,
        input_folder = cacheStep.output,
        commandline = PipelineParameter(name = "extra_1", default_value = '--cb_explore_adf --epsilon 0.2 --dsjson'),
        name = 'NoHyper'
    )

    predict_4 = vw_predict_step.vw_predict_step(
        workspace = ws,
        input_folder = cacheStep.output,
        commandline = PipelineParameter(name = "extra_2", default_value = '--cb_explore_adf --epsilon 0.2 --dsjson'),
        name = 'NoMarginal'
    )

    dashboard = dashboard_step.dashboard_step(
        workspace = ws,
        data = extractStep.output,
        predictions = [predict_1.output, predict_2.output, predict_3.output, predict_4.output]
    )

    sweep_pipeline = Pipeline(workspace=ws, steps=[dashboard])
    print ("VwTrainPipeline is succesfully created.")

    sweep_pipeline.validate()
    print("VwTrainPipeline is succesfully validated.")

    return sweep_pipeline        