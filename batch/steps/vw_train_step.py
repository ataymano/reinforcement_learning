import os
import azureml.core
import datetime
from azureml.pipeline.steps import PythonScriptStep, MpiStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.runconfig import CondaDependencies, RunConfiguration
from azureml.pipeline.core import PipelineData

class vw_train_step(PythonScriptStep):
 
    def __init__(self, workspace, input_folder, compute):
        self.input = input_folder
        self.output = PipelineData("Vw_model_intermediate_data", datastore = workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        config = RunConfiguration()
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.4"
        config.environment.python.user_managed_dependencies = True


#        config.environment.docker.enabled = True
#        config.environment.docker.gpu_support = True
#        config.environment.docker.base_image = "pytorch/pytorch"
#        config.environment.spark.precache_packages = False

        super().__init__(
            name="vw_learn",
            source_directory=os.path.join(dir_path, 'scripts'),
            script_name="vw_train.py", 
            arguments=["--input_folder", self.input, "--output_folder", self.output],
            compute_target=compute, 
            inputs=[self.input],
            outputs=[self.output],
            runconfig = config
        )
    
        print("Vw train step is successfully created") 

    def input(self):
        return self.input

    def output(self):
        return self.output