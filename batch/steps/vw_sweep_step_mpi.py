import os
import azureml.core
import datetime
from azureml.pipeline.steps import PythonScriptStep, MpiStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.runconfig import CondaDependencies, RunConfiguration
from azureml.pipeline.core import PipelineData

from utils import compute

class vw_sweep_step_mpi:
    def __init__(self, workspace, input_folder, node_count, process_per_node, allow_reuse):
        self.input = input_folder.as_download()
        self.output = PipelineData("command", datastore=workspace.get_default_datastore())

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        config = RunConfiguration()
        print(config)
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.96"
        config.environment.python.user_managed_dependencies = True

        self.step = MpiStep(
            name="SweepMpi_"+str(node_count) + "_" + str(process_per_node),
            source_directory=os.path.join(dir_path, 'scripts'),
            script_name='vw_sweep.py',
            arguments=[
                "--input_folder", self.input,
                "--output", self.output,
                "--procs", 1,
                "--vw", "/usr/local/bin/vw",
                "--env", "mpi",
                "--models", "/home/"
            ],
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'extractorf16',
                vm_size='Standard_F16s_v2',
                max_nodes=node_count
            ),
            node_count = node_count,
            process_count_per_node = process_per_node,
            inputs=[self.input],
            outputs=[self.output],
            allow_reuse = allow_reuse,
            version = None,
            hash_paths = None,
            environment_definition = config.environment
        )
        print("Vw sweep step is successfully created")
