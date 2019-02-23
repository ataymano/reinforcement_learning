import os
import azureml.core
import datetime

from azureml.data.data_reference import DataReference
from azureml.pipeline.steps import PythonScriptStep, DataTransferStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core import PipelineData
from azureml.core.runconfig import CondaDependencies, RunConfiguration

import helpers
from helpers import compute

class dashboard_step(PythonScriptStep):
    def __init__(self, workspace, context, predictions):
        self.input = DataReference(
                datastore=context.get_datastore(workspace),
                data_reference_name="Application_logs",
                path_on_datastore=context.appFolder)
        self.predictions = predictions
        dashboard_tmp = PipelineData("dashboard", datastore=workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        
        cd = CondaDependencies()

        cd.add_conda_package("pandas")
        cd.add_conda_package("numpy")

        # Runconfig
        run_config = RunConfiguration(conda_dependencies=cd)

        self.step1 = PythonScriptStep(
            name="Dashboard",
            script_name='dashboard.py', 
            arguments=["--log_fp", self.input, "--pred_fp", self.predictions, "--output_fp", dashboard_tmp],
            inputs=[self.input, self.predictions],
            outputs=[dashboard_tmp],
            compute_target=compute.get_or_create_aml_compute_target(workspace, 'dashboard', vm_size = 'Standard_F2s_v2'), 
            source_directory=os.path.join(dir_path, 'scripts'),
            runconfig = run_config,
            allow_reuse=True
        )

        self.output = DataReference(
            datastore=context.get_datastore(workspace),
            data_reference_name="dashboard",
            path_on_datastore="dashboard.json")

        self.step2 = DataTransferStep(
            name="Dashboard deploy",
            source_data_reference=dashboard_tmp,
            source_reference_type='file',
            destination_data_reference=self.output,
            destination_reference_type='file',
            compute_target=compute.get_or_create_data_factory(workspace, 'adf-compute-0')
        )
        print("Dashboard step is successfully created")

    def input(self):
        return self.input

    def output(self):
        return self.output