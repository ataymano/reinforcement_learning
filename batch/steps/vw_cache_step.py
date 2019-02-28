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
 
    def __init__(self, workspace, context):
        self.input = InputPortBinding(name="Application_logs", bind_object=DataReference(
                datastore=context.get_datastore(workspace),
                data_reference_name="Application_logs",
                path_on_datastore=context.appFolder))
        self.output = PipelineData("cache", datastore = workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        pattern = "%m/%d/%Y %H:%M:%S"
        start = PipelineParameter(name = "start_datetime", default_value = '')
        end = PipelineParameter(name = "end_datetime", default_value = '')

        config = RunConfiguration()
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.7"
        config.environment.python.user_managed_dependencies = True


#        config.environment.docker.enabled = True
#        config.environment.docker.gpu_support = True
#        config.environment.docker.base_image = "pytorch/pytorch"
#        config.environment.spark.precache_packages = False

        super().__init__(
            name="Cache [vw]",
            source_directory=os.path.join(dir_path, 'scripts'),
            script_name="vw_cache.py", 
            arguments=["--input_folder", self.input, "--output_folder", self.output, "--start_datetime", start, "--end_datetime", end, "--pattern", pattern], 
            inputs=[self.input],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(workspace, 'extractor', vm_size = 'Standard_F2s_v2'), 
            runconfig = config
        )
    
        print("Vw cache step is successfully created") 

    def input(self):
        return self.input

    def output(self):
        return self.output