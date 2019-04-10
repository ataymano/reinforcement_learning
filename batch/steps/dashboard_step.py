import os
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import OutputPortBinding
from azureml.core.runconfig import CondaDependencies, RunConfiguration
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineData
from utils import compute


class dashboard_step(PythonScriptStep):
    def __init__(self, workspace, ctx, metadata_folder, predictions_folder):
        self.input = DataReference(
            datastore=ctx.get_datastore(workspace),
            data_reference_name="Application_logs",
            path_on_datastore=ctx.appFolder
        )

        self.output = OutputPortBinding(
            name='dashboard',
            datastore=workspace.get_default_datastore(),
            bind_mode='mount'
        )

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        cd = CondaDependencies()

        cd.add_conda_package("pandas")
        cd.add_conda_package("numpy")

        run_config = RunConfiguration(conda_dependencies=cd)

        super().__init__(
            name="Dashboard",
            script_name='dashboard.py',
            arguments=[
                "--log_folder", self.input,
                "--metadata_folder", metadata_folder,
                "--predictions_folder", predictions_folder,
                "--output_folder", self.output
            ],
            inputs=[self.input, metadata_folder, predictions_folder],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'extractorf8',
                vm_size='Standard_F8s_v2',
                max_nodes=1
            ),
            source_directory=os.path.join(dir_path, 'scripts'),
            runconfig=run_config,
            allow_reuse=True
        )
        print("Dashboard step is successfully created")
