import os
import azureml.core
import datetime
from azureml.pipeline.steps import PythonScriptStep, DataTransferStep
from azureml.pipeline.core.graph import PipelineParameter


class deployment_step(DataTransferStep):
    def __init__(self, input_folder, output_folder, compute):
        super().__init__(
            name="deployment",
            source_data_reference=input_folder,
            source_reference_type='directory',
            destination_data_reference=output_folder,
            destination_reference_type='directory',
            compute_target=compute
        )