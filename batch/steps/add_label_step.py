import os
import azureml.core
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core import PipelineData

class add_label_step(PythonScriptStep):
    def __init__(self, workspace, input_folder, compute):
        self.input = input_folder
        self.output = PipelineData("add_label_step_intermediate_data", datastore=workspace.get_default_datastore())
        
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        
        super().__init__(
            name="add_labels",
            script_name="add_label.py", 
            arguments=["--input_folder", self.input, "--output_folder", self.output],
            inputs=[self.input],
            outputs=[self.output],
            compute_target=compute, 
            source_directory=os.path.join(dir_path, 'scripts')
        )
        print("Add labels step is successfully created")

    def input(self):
        return self.input

    def output(self):
        return self.output