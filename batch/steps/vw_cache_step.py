import os
import azureml.core
import datetime
from azureml.pipeline.steps import PythonScriptStep, MpiStep
from azureml.pipeline.core.graph import PipelineParameter, InputPortBinding
from azureml.core.runconfig import CondaDependencies, RunConfiguration
from azureml.pipeline.core import PipelineData
from azureml.data.data_reference import DataReference

import helpers
from helpers import compute

class vw_cache_step(PythonScriptStep):
 
    def __init__(self, workspace, input):
        self.input = input
        self.output = PipelineData("cache", datastore = workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        config = RunConfiguration()
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.7"
        config.environment.python.user_managed_dependencies = True

        super().__init__(
            name="Cache [vw]",
            source_directory=os.path.join(dir_path, 'scripts'),
            script_name="vw_cache.py", 
            arguments=["--input_path", self.input, "--output_folder", self.output], 
            inputs=[self.input],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(workspace, 'extractor', vm_size = 'Standard_F2s_v2'), 
            runconfig = config
        )
    
        print("Vw cache step is successfully created")