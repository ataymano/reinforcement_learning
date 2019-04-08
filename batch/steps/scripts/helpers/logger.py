from azureml.core.run import Run
import datetime

def log_scalar_global(key, value, env):
    if env.is_master():
        Run.get_context().log(key, value)
    trace(key + ': ' + str(value))

def log_scalar_local(key, value):
    Run.get_context().log(key, value)
    trace(key + ': ' + str(value))

def trace(message):
    print('[' + str(datetime.datetime.now()) + ']  ' +  message)