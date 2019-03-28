import os

from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import OutputPortBinding
from azureml.core.runconfig import CondaDependencies, RunConfiguration
from utils import compute


class dashboard_step(PythonScriptStep):
    def __init__(self, workspace, log, predictions):
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

        # p_args = []
        # for p in predictions:
        #     p_args.extend(['--pred_fp', p])

        # args = ['--log_fp', data]
        # args.extend(p_args)
        # args.extend(['--output_fp', self.output])

        # inputs = [data]
        # inputs.extend(predictions)
        super().__init__(
            name="Dashboard",
            script_name='dashboard.py',
            arguments=args,
            inputs=inputs,
            outputs=[self.output],
            compute_target=compute.get_or_create_aml_compute_target(
                workspace,
                'dashboard',
                vm_size='Standard_F2s_v2'
            ),
            source_directory=os.path.join(dir_path, 'scripts'),
            runconfig=run_config,
            allow_reuse=True
        )
        print("Dashboard step is successfully created")
