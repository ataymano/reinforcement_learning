import os
import azureml.core
import datetime

from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core import PipelineData

import helpers
from helpers import compute

class base_command_step(PythonScriptStep):
    def __init__(self, workspace):
        self.output = PipelineData("command", datastore=workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        
        base_command = PipelineParameter(name = "base_command", default_value = '--cb_adf --dsjson')

        super().__init__(
            name="Base command",
            script_name='prepare_base_command.py', 
            arguments=["--base_command_output", self.output, base_command],
            inputs=[],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(workspace, 'python', vm_size = 'STANDARD_D2_v2'), 
            source_directory=os.path.join(dir_path, 'scripts')
        )
        print("Best command selection step is created successfully")