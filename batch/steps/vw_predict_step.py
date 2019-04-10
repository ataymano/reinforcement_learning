import os
from azureml.pipeline.core import PipelineData
from steps import prepare_command_step
from utils import compute
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.steps import PythonScriptStep


class vw_predict_step(PythonScriptStep):

    def __init__(
        self,
        workspace,
        cache_folder,
        commands
    ):

        self.output = PipelineData(
            "Predictions",
            datastore=workspace.get_default_datastore()
        )

        self.model_folder = PipelineData(
            "models",
            datastore=workspace.get_default_datastore()
        )

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        config = RunConfiguration()
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.96"

        args = [
            "--cache_folder", cache_folder,
            "--model_folder", self.model_folder,
            "--output_folder", self.output,
            "--procs", 1,
            "--vw", "/usr/local/bin/vw",
            "--commands", commands
        ]
        super().__init__(
            name="Predict",
            source_directory=os.path.join(dir_path, 'scripts'),
            script_name="vw_predict.py",
            arguments=args,
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'extractorf8',
                vm_size='Standard_F8s_v2',
                max_nodes=1
            ),
            inputs=[cache_folder, commands],
            outputs=[self.output, self.model_folder],
            runconfig=config,
            allow_reuse=True
        )

        print("Vw predict step is successfully created")
