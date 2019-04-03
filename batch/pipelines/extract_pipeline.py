import application
from steps import create_cache_step, vw_sweep_step, vw_predict_step
from azureml.pipeline.core import Pipeline
from azureml.pipeline.core.graph import PipelineParameter


def create_pipeline(ws, ctx):
    cacheStep = create_cache_step.create_cache_step(
        workspace=ws,
        context=ctx
    )

    sweepStep = vw_sweep_step.vw_sweep_step(workspace=ws,
                                            input_folder = cacheStep.output,
                                            process_per_node = PipelineParameter(name = "procs", default_value = '1'))
   # predict = vw_predict_step.vw_predict_step(
   #     workspace=ws,
   #     input_folder=cacheStep.output,
   #     commandline=PipelineParameter(
   #         name='extra_2',
   #         default_value='--cb_explore_adf --epsilon 0.2 --dsjson'
   #     ),
   #     policy_name='NoMarginal'
   # )

    extractPipeline = Pipeline(workspace=ws, steps=[sweepStep])
    print ("extractPipeline is succesfully created.")

    extractPipeline.validate()
    print("extractPipeline is succesfully validated.")

    return extractPipeline
