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
        input_folder,
        policy_name,
        command=None,
        commandline=None
    ):
        self.input = input_folder
        if not (command or commandline):
            raise ValueError('predict step error: command cannot be empty')

        if command is None:
            self.preprocessor = prepare_command_step.prepare_command_step(
                workspace=workspace,
                command=commandline
            )
            command = self.preprocessor.output

        self.command = command

        self.output = PipelineData(
            "Predictions",
            datastore=workspace.get_default_datastore()
        )

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        config = RunConfiguration()
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.9"

        super().__init__(
            name="Predict",
            source_directory=os.path.join(dir_path, 'scripts'),
            script_name="vw_predict.py",
            arguments=[
                "--input_folder", self.input,
                "--output_folder", self.output,
                '--command', self.command,
                '--policy_name', policy_name
            ],
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'vw-predict',
                vm_size='Standard_DS1_v2',
                max_nodes=4
            ),
            inputs=[self.input, self.command],
            outputs=[self.output],
            runconfig=config,
            allow_reuse=True
        )

        print("Vw predict step is successfully created")
