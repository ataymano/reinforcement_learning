import application
from azureml.pipeline.core import Pipeline
from steps import create_cache_step
from steps import vw_predict_step
from steps import dashboard_step
from steps import prepare_command_step
from steps import vw_sweep_step
from azureml.pipeline.core.graph import PipelineParameter
from azureml.train.hyperdrive import GridParameterSampling
from azureml.train.hyperdrive import RandomParameterSampling
from azureml.train.hyperdrive import choice


def create_pipeline(ws, ctx, parallel_jobs):
    base_command_step = prepare_command_step.prepare_command_step(
        workspace=ws,
        command=PipelineParameter(
            name="base_command",
            default_value='--cb_adf --dsjson'
        )
    )

    cache_step = create_cache_step.create_cache_step(
        workspace=ws,
        context=ctx
    )

    grid_1 = RandomParameterSampling({
        '--power_t': choice(0, 1e-3, 0.5),
        '--l1': choice(0, 1e-06, 1e-04, 1e-3),
        '-l': choice(1e-05, 1e-3, 1e-2, 1e-1, 0.5, 10),
        '--cb_type': choice('mtr', 'ips')
    })

    sweep_step_1 = vw_sweep_step.vw_sweep_step(
        workspace=ws,
        input_folder=cache_step.output,
        base_command=base_command_step.output,
        policy_name='Hyper1',
        param_grid=grid_1,
        parallel_jobs=parallel_jobs,
        jobs_limit=2
    )

    predict = vw_predict_step.vw_predict_step(
        workspace=ws,
        cache_folder=cache_step.output,
        commands_folder=sweep_step_1.output
    )

    # predict = vw_predict_step.vw_predict_step(
    #     workspace=ws,
    #     input_folder=cache_step.output,
    #     commandline=PipelineParameter(
    #         name='extra_2',
    #         default_value='--cb_explore_adf --epsilon 0.2 --dsjson'
    #     ),
    #     policy_name='NoMarginal'
    # )

    dashboard = dashboard_step.dashboard_step(
        workspace=ws,
        ctx=ctx,
        metadata_folder=cache_step.output,
        predictions_folder=predict.output
    )

    extractPipeline = Pipeline(
        workspace=ws,
        steps=[
            base_command_step,
            cache_step,
            predict,
            dashboard
        ]
    )
    print ("extractPipeline is succesfully created.")

    extractPipeline.validate()
    print("extractPipeline is succesfully validated.")

    return extractPipeline
