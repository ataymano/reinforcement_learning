import os
from azureml.data.data_reference import DataReference
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core import PipelineData
from azureml.core.runconfig import RunConfiguration
from utils import compute


class create_cache_step(PythonScriptStep):

    def __init__(self, workspace, context):
        self.input = DataReference(
            datastore=context.get_datastore(workspace),
            data_reference_name="Application_logs",
            path_on_datastore=context.appFolder
        )

        self.output = PipelineData(
            "Cache",
            datastore=workspace.get_default_datastore()
        )

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        start_date = PipelineParameter(name="start_date", default_value='')
        end_date = PipelineParameter(name="end_date", default_value='')

        if not start_date or not end_date:
            raise ValueError("start_date or end_date is not specified")

        config = RunConfiguration()
        print(config)
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.9"

        super().__init__(
            name="Cache",
            script_name='create_cache.py',
            arguments=[
                "--input_folder", self.input,
                "--output_folder", self.output,
                "--start_date", start_date,
                "--end_date", end_date
            ],
            inputs=[self.input],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'extractorf8',
                vm_size='Standard_F8s_v2',
                max_nodes=1
            ),
            source_directory=os.path.join(dir_path, 'scripts'),
            runconfig=config
        )
        print("Cache step is successfully created")
