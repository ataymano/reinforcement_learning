import subprocess


def _parse_vw_output(txt):
    result = {}
    for line in txt.split('\n'):
        if '=' in line:
            index = line.find('=')
            key = line[0:index].strip()
            value = line[index+1:].strip()
            result[key] = value
    return result


def run(command):
    process = subprocess.Popen(
        command.split(),
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # output, error = execution.communicate()
    # return Vw._parse_vw_output(error)
    # utils.logger(process.communicate())
    print(process.communicate())


def build_command(command='', opts={}):
    vw_path = '/usr/local/bin/vw'
    print('build command: ' + command)
    if command:
        command = ' '.join([
            vw_path,
            command,
            '--save_resume',
            '--preserve_performance_counters'
        ])
    else:
        command = ' '.join([
            vw_path,
            '--cb_adf',
            '--dsjson',
            '--save_resume',
            '--preserve_performance_counters'
        ])

    for key, val in opts.items():
        command = ' '.join([
            command,
            key,
            val
        ])

    return command
