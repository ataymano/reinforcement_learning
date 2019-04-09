import os
import azureml.core
import datetime
from azureml.pipeline.steps import PythonScriptStep, MpiStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.runconfig import CondaDependencies, RunConfiguration
from azureml.pipeline.core import PipelineData

from utils import compute

class vw_sweep_step(PythonScriptStep):
    def __init__(self, workspace, input_folder, process_per_node):
        self.input = input_folder.as_download()
        self.output = PipelineData("command", datastore=workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        config = RunConfiguration()
        print(config)
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.96"
        config.environment.python.user_managed_dependencies = True

        super().__init__(
            name="Sweep",

            script_name='vw_sweep.py',
            arguments=[
                "--input_folder", self.input,
                "--output", self.output,
                "--procs", process_per_node,
                "--vw", "/usr/local/bin/vw",
                "--env", "local",
                "--models", "/home/"
            ],
            inputs=[self.input],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'extractorf16',
                vm_size='Standard_F16s_v2',
                max_nodes=2
            ),
            source_directory=os.path.join(dir_path, 'scripts'),
            runconfig=config,
            allow_reuse=False
        )
        print("Vw sweep step is successfully created")
