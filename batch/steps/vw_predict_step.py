import os
import azureml.core
import datetime
from azureml.pipeline.steps import PythonScriptStep, MpiStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.runconfig import CondaDependencies, RunConfiguration
from azureml.pipeline.core import PipelineData

import helpers
from helpers import compute

class vw_predict_step(PythonScriptStep):
 
    def __init__(self, workspace, input_folder, command):
        self.input = input_folder
        self.command = command
        self.output = PipelineData("prediction", datastore = workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        config = RunConfiguration()
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.7"
        config.environment.python.user_managed_dependencies = True

        super().__init__(
            name="Predict [vw]",
            source_directory=os.path.join(dir_path, 'scripts'),
            script_name="vw_predict.py", 
            arguments=["--input_folder", self.input, "--output_folder", self.output, '--command', self.command],
            compute_target=compute.get_or_create_aml_compute_target(workspace, 'vw-predict', vm_size = 'Standard_DS1_v2', max_nodes = 4), 
            inputs=[self.input, self.command],
            outputs=[self.output],
            runconfig = config,
            allow_reuse = True
        )
    
        print("Vw predict step is successfully created") 
