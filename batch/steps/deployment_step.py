import os
import azureml.core
import datetime
from azureml.pipeline.steps import PythonScriptStep, DataTransferStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.data.data_reference import DataReference

import helpers
from helpers import compute

class deployment_step(DataTransferStep):
    def __init__(self, workspace, context, input_folder):
        self.input = input_folder
        self.output = DataReference(
            datastore=context.get_datastore(workspace),
            data_reference_name="Vw_model",
            path_on_datastore="exported-models")

        super().__init__(
            name="deployment",
            source_data_reference=self.input,
            source_reference_type='directory',
            destination_data_reference=self.output,
            destination_reference_type='directory',
            compute_target=compute.get_or_create_data_factory(workspace, 'adf-compute-0')
        )
        print("Deployment step is successfully created")