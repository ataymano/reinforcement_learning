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
        commands,
        procs
    ):
        cache_folder = cache_folder.as_download()
        self.output = PipelineData(
            "Predictions",
            datastore=workspace.get_default_datastore()
        )

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        config = RunConfiguration()
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.96"
        config.environment.python.user_managed_dependencies = True

        args = [
            "--cache_folder", cache_folder,
            "--model_folder", '/home/',
            "--output_folder", self.output,
            "--procs", procs,
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
                'extractorf16',
                vm_size='Standard_F16s_v2',
                max_nodes=2
            ),
            inputs=[cache_folder, commands],
            outputs=[self.output],
            runconfig=config,
            allow_reuse=True
        )

        print("Vw predict step is successfully created")
