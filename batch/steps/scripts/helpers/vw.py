import subprocess
from subprocess import check_output
import sys


def _parse_vw_output(txt):
    result = {}
    for line in txt.split('\n'):
        if '=' in line:
            index = line.find('=')
            key = line[0:index].strip()
            value = line[index+1:].strip()
            result[key] = value
    return result


def parse_average_loss(vw_output):
    for line in vw_output.split('\n'):
        if (line.startswith('average loss =')):
            loss = line.split('=')[1].strip()
            if (loss == 'n.a.'):
                loss = sys.float_info.max
            return float(loss)


def run(command):
    process = subprocess.Popen(
        command.split(),
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, stderr = process.communicate()
    return stdout


def build_command(command='', opts={}):
    vw_path = '/usr/local/bin/vw'
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
