import os
import azureml.core
import datetime

from azureml.data.data_reference import DataReference
from azureml.pipeline.steps import PythonScriptStep, DataTransferStep
from azureml.pipeline.core.graph import PipelineParameter, OutputPortBinding
from azureml.pipeline.core import PipelineData
from azureml.core.runconfig import CondaDependencies, RunConfiguration

import helpers
from helpers import compute

class dashboard_step(PythonScriptStep):
    def __init__(self, workspace, data, predictions):
        self.output = OutputPortBinding(
            name = 'dashboard',
            datastore = workspace.get_default_datastore(),
            bind_mode='mount')
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        
        cd = CondaDependencies()

        cd.add_conda_package("pandas")
        cd.add_conda_package("numpy")

        run_config = RunConfiguration(conda_dependencies=cd)

        super().__init__(
            name="Dashboard",
            script_name='dashboard.py', 
            arguments=["--log_fp", data, "--pred_fp", predictions, "--output_fp", self.output],
            inputs=[data, predictions],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(workspace, 'dashboard', vm_size = 'Standard_F2s_v2'), 
            source_directory=os.path.join(dir_path, 'scripts'),
            runconfig = run_config,
            allow_reuse=True
        )
        print("Dashboard step is successfully created")
