import os
import azureml.core
import datetime
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import PipelineParameter


class extract_step(PythonScriptStep):
    def __init__(self, input_folder, output_folder, compute):
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        
        pattern = "%Y-%m-%dT%H:%M:%S.%f0Z"
        start = PipelineParameter(name = "start_datetime", default_value = '')
        end = PipelineParameter(name = "end_datetime", default_value = '')

        if not start or not end:
            raise ValueError("start_datetime or end_datetime is not specified")

        super().__init__(
            name="extract_batch",
            script_name="extract.py", 
            arguments=["--input_folder", input_folder, "--output_folder", output_folder, "--start_datetime", start, "--end_datetime", end, "--pattern", pattern],
            inputs=[input_folder],
            outputs=[output_folder],
            compute_target=compute, 
            source_directory=os.path.join(dir_path, 'scripts')
        )