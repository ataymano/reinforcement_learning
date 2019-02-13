import os
import azureml.core
import datetime

from azureml.data.data_reference import DataReference
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core import PipelineData

class extract_step(PythonScriptStep):
    def __init__(self, workspace, context, compute):
        self.input = DataReference(
                datastore=context.get_datastore(workspace),
                data_reference_name="Application_logs",
                path_on_datastore=context.appFolder)
        self.output = PipelineData("extract_step_intermediate_data", datastore=workspace.get_default_datastore())

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
            arguments=["--input_folder", self.input, "--output_folder", self.output, "--start_datetime", start, "--end_datetime", end, "--pattern", pattern],
            inputs=[self.input],
            outputs=[self.output],
            compute_target=compute, 
            source_directory=os.path.join(dir_path, 'scripts')
        )
        print("Data extraction step is successfully created")

    def input(self):
        return self.input

    def output(self):
        return self.output