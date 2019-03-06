import os
import azureml.core
import datetime

from azureml.data.data_reference import DataReference
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core import PipelineData

import helpers
from helpers import compute

class best_command_step(PythonScriptStep):
    def __init__(self, workspace, input, allow_reuse = True):
        self.input = input
        self.output = PipelineData("command", datastore=workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        
        super().__init__(
            name="Best command",
            script_name='get_best_command.py', 
            arguments=["--input", self.input, "--output", self.output],
            inputs=[self.input],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(workspace, 'python', vm_size = 'STANDARD_D2_v2'), 
            source_directory=os.path.join(dir_path, 'scripts'),
            allow_reuse = allow_reuse
        )
        print("Best command selection step is created successfully")