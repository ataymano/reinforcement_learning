import os
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import PipelineData
from utils import compute


class prepare_command_step(PythonScriptStep):
    def __init__(self, workspace, command):
        self.output = PipelineData(
            "command",
            datastore=workspace.get_default_datastore()
        )

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        super().__init__(
            name="Prepare command",
            script_name='prepare_command.py',
            arguments=["--command_output", self.output, command],
            inputs=[],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'python',
                vm_size='STANDARD_D2_v2'
            ),
            source_directory=os.path.join(dir_path, 'scripts')
        )
        print("Best command selection step is created successfully")
