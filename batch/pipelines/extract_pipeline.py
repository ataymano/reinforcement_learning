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
        context=ctx,
        input_folder=cache_step.output,
        base_command=base_command_step.output,
        policy_name='Hyper1',
        param_grid=grid_1,
        parallel_jobs=parallel_jobs,
        jobs_limit=2
    )

    # grid_2 = GridParameterSampling({
    #     '--marginals_index': choice(0, 1),
    #     '--interactions_index': choice(0, 1, 2, 3, 4, 5, 6, 7)
    # })

    # sweep_step_2 = vw_sweep_step.vw_sweep_step(
    #     workspace=ws,
    #     context=ctx,
    #     input_folder=cache_step.output,
    #     base_command=sweep_step_1.output,
    #     policy_name='Quad',
    #     previous_policy='Hyper1',
    #     param_grid=grid_2,
    #     parallel_jobs=parallel_jobs,
    #     jobs_limit=2
    # )

    # sweep_step_3 = vw_sweep_step.vw_sweep_step(
    #     workspace=ws,
    #     input_folder=cache_step.output,
    #     base_command=sweep_step_2.output,
    #     policy_name='Hyper2',
    #     previous_policy='Quad',
    #     param_grid=grid_1,
    #     parallel_jobs=parallel_jobs,
    #     jobs_limit=2
    # )

    predict = vw_predict_step.vw_predict_step(
        workspace=ws,
        cache_folder=cache_step.output,
        command_folders=[
            sweep_step_1.output,
            # sweep_step_2.output,
        ]
    )

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
