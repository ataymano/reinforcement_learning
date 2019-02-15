import os
import azureml.core
import datetime

from azureml.data.data_reference import DataReference
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core import PipelineData

import helpers
from helpers import compute

class extract_step(PythonScriptStep):
    def __init__(self, workspace, context, with_labels = True):
        self.input = DataReference(
                datastore=context.get_datastore(workspace),
                data_reference_name="Application_logs",
                path_on_datastore=context.appFolder)
        self.output = PipelineData("extract_step_intermediate_data", datastore=workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        
    #    pattern = "%Y-%m-%dT%H:%M:%S.%f0Z"
        pattern = "%m/%d/%Y %H:%M:%S"

        start = PipelineParameter(name = "start_datetime", default_value = '')
        end = PipelineParameter(name = "end_datetime", default_value = '')

        if not start or not end:
            raise ValueError("start_datetime or end_datetime is not specified")

        if with_labels:
            script_name = 'extract_with_labels.py'
        else:
            script_name = 'extract_no_labels.py'

        super().__init__(
            name="extract_batch",
            script_name=script_name, 
            arguments=["--input_folder", self.input, "--output_folder", self.output, "--start_datetime", start, "--end_datetime", end, "--pattern", pattern],
            inputs=[self.input],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(workspace, 'aml-compute-0'), 
            source_directory=os.path.join(dir_path, 'scripts')
        )
        print("Data extraction step is successfully created")

    def input(self):
        return self.input

    def output(self):
        return self.output