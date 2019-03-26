import application
from application import context

import helpers
from helpers import compute
from helpers import utils

import steps
from steps import create_cache_step

import azureml.core
from azureml.pipeline.core import Pipeline
from azureml.train.hyperdrive import GridParameterSampling, RandomParameterSampling, choice
from steps import vw_predict_step
from azureml.pipeline.core.graph import PipelineParameter

import os

def create_pipeline(ws, ctx, parallel_jobs):
    cacheStep = create_cache_step.create_cache_step(
        workspace = ws,
        context = ctx #login info
    )

    predict_4 = vw_predict_step.vw_predict_step(
        workspace = ws,
        input_folder = cacheStep.output,
        commandline = PipelineParameter(name = "extra_2", default_value = '--cb_explore_adf --epsilon 0.2 --dsjson'),
        name = 'NoMarginal'
    )

    # dashboard = dashboard_step.dashboard_step(
    #     workspace = ws,
    #     data = cacheStep.output, # should be original log
    #     predictions = [predict_4.output]
    # )

    extractPipeline = Pipeline(workspace=ws, steps=[cacheStep, predict_4])
    print ("extractPipeline is succesfully created.")

    extractPipeline.validate()
    print("extractPipeline is succesfully validated.")

    return extractPipeline
