import application
from steps import create_cache_step, vw_sweep_step, vw_predict_step, vw_sweep_step_mpi
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
    extractPipeline = Pipeline(workspace=ws, steps=[predictStep])
    print ("extractPipeline is succesfully created.")

    extractPipeline.validate()
    print("extractPipeline is succesfully validated.")
    return extractPipeline







