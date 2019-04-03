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
        command_folders
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
        config.environment.docker.base_image = "ataymano/test:0.9"

        command_folders_args = []
        for command_folder in command_folders:
            command_folders_args.extend([
                '--command_folders', command_folder
            ])

        args = [
            "--cache_folder", cache_folder,
            "--model_folder", self.model_folder,
            "--output_folder", self.output
        ]
        args.extend(command_folders_args)
        print(args)

        inputs = [cache_folder]
        inputs.extend(command_folders)
        print("==inputs==")
        print(inputs)
        super().__init__(
            name="Predict",
            source_directory=os.path.join(dir_path, 'scripts'),
            script_name="vw_predict.py",
            arguments=args,
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'vw-predict',
                vm_size='Standard_DS1_v2',
                max_nodes=4
            ),
            inputs=inputs,
            outputs=[self.output, self.model_folder],
            runconfig=config,
            allow_reuse=True
        )

        print("Vw predict step is successfully created")
