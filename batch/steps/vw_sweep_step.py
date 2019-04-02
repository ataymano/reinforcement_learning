import os
from azureml.pipeline.steps import PythonScriptStep
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core import PipelineData
from azureml.pipeline.steps import HyperDriveStep
from azureml.train.hyperdrive import PrimaryMetricGoal, HyperDriveRunConfig
from azureml.train.estimator import Estimator
from utils import compute


class vw_sweep_step(HyperDriveStep):
    def __init__(
        self,
        workspace,
        input_folder,
        base_command,
        policy_name,
        param_grid,
        parallel_jobs,
        jobs_limit,
        allow_reuse=True
    ):
        self.input = input_folder
        self.base_command = base_command
        self.metrics_output = PipelineData(
            "sweep_metrics",
            datastore=workspace.get_default_datastore()
        )

        self.output = PipelineData(
            "best_commands",
            datastore=workspace.get_default_datastore()
        )

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        config = RunConfiguration()
        config.environment.docker.enabled = True
        config.environment.docker.base_image = "ataymano/test:0.9"

        est = Estimator(
            source_directory=os.path.join(dir_path, 'scripts'),
            script_params={},
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'vw',
                vm_size='Standard_DS1_v2',
                max_nodes=2
            ),
            entry_script='vw_estimate.py',
            environment_definition=config.environment
        )

        hd_config = HyperDriveRunConfig(
            estimator=est,
            hyperparameter_sampling=param_grid,
            primary_metric_name='average loss',
            primary_metric_goal=PrimaryMetricGoal.MINIMIZE,
            max_total_runs=jobs_limit,
            max_concurrent_runs=parallel_jobs
        )

        self._hdStep = HyperDriveStep(
            name="Sweep [vw]",
            hyperdrive_run_config=hd_config,
            estimator_entry_script_arguments=[
                "--input_folder", self.input,
                "--metrics_folder", self.metrics_output,
                "--base_command", self.base_command
            ],
            inputs=[self.input, self.base_command],
            outputs=[self.metrics_output],
            allow_reuse=False
        )

        self._bestStep = PythonScriptStep(
            name="Best command",
            script_name='get_best_command.py',
            arguments=[
                "--metrics_folder", self.metrics_output,
                "--best_commands_folder", self.output,
                "--policy_name", policy_name
            ],
            inputs=[self.metrics_output],
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'python',
                vm_size='STANDARD_D2_v2'
            ),
            source_directory=os.path.join(dir_path, 'scripts'),
            allow_reuse=True
        )

        print("Vw sweep step is successfully created")
