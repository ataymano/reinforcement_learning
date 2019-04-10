
import application
from steps import create_cache_step, vw_sweep_step, vw_predict_step, vw_sweep_step_mpi
from azureml.pipeline.core import Pipeline
from azureml.pipeline.core.graph import PipelineParameter


def create_pipeline(ws, ctx, node_count, process_per_node, is_mpi):
    cacheStep = create_cache_step.create_cache_step(
        workspace=ws,
        context=ctx
    )

    if is_mpi:
        sweepStep = vw_sweep_step_mpi.vw_sweep_step_mpi(workspace=ws,
                                            input_folder = cacheStep.output,
                                            node_count = node_count,
                                            process_per_node = process_per_node,
                                            allow_reuse = False)
        extractPipeline = Pipeline(workspace=ws, steps=[sweepStep.step])
        print ("extractPipeline is succesfully created.")

        extractPipeline.validate()
        print("extractPipeline is succesfully validated.")

        return extractPipeline
    else:
        sweepStep = vw_sweep_step.vw_sweep_step(workspace=ws,
                                            input_folder = cacheStep.output,
                                            process_per_node = process_per_node,
                                            allow_reuse = False)
        extractPipeline = Pipeline(workspace=ws, steps=[sweepStep])
        print ("extractPipeline is succesfully created.")

        extractPipeline.validate()
        print("extractPipeline is succesfully validated.")
        return extractPipeline







