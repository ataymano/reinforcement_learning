#from azureml.core.run import Run
import datetime

class logger:
    def __init__(self, runtime):
        self.runtime = runtime

    def log_scalar_global(self, key, value):
 #       if self.runtime and self.runtime.is_master():
 #           Run.get_context().log(key, value)
        self.trace(key + ': ' + str(value))

    def log_scalar_local(self, key, value):
  #      Run.get_context().log(key, value)
        self.trace(key + ': ' + str(value))

    def trace(self, message):
        print('[' + str(datetime.datetime.now()) + ']  ' +  message)