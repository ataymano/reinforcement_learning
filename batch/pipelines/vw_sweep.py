import application
from steps import create_cache_step, vw_sweep_step, vw_predict_step, vw_sweep_step_mpi, dashboard_step
from azureml.pipeline.core import Pipeline
from azureml.pipeline.core.graph import PipelineParameter


def create_pipeline(ws, ctx):
    cacheStep = create_cache_step.create_cache_step(
        workspace=ws,
        context=ctx
    )

    sweepStep = vw_sweep_step.vw_sweep_step(workspace=ws,
                                            input_folder = cacheStep.output,
                                            process_per_node = PipelineParameter(name="procs", default_value='1'), allow_reuse = True)

    predictStep = vw_predict_step.vw_predict_step(workspace = ws,
                                                  cache_folder = cacheStep.output,
                                                  commands = sweepStep.output)

    dashboardStep = dashboard_step.dashboard_step(workspace = ws,
                                                  ctx = ctx,
                                                  metadata_folder = cacheStep.output,
                                                  predictions_folder = predictStep.output)
    pipeline = Pipeline(workspace=ws, steps=[dashboardStep])
    print ("Vw Sweep pipeline is succesfully created.")

    pipeline.validate()
    print("Vw Sweep pipeline is succesfully validated.")
    return pipeline







