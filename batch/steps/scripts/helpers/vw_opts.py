import json
import itertools
import functools
import re

def serialize(opts):
    if not isinstance(opts, dict):
        raise Error('opts are not dict')
    return json.dumps(opts)

def deserialize(s):
    candidate = json.loads(s)
    if not isinstance(candidate, dict):
        raise Error('candidate opts are not dict')
    return candidate

def to_commandline(opts):
    command = ''
    for key, val in opts.items():
        command = ' '.join([command, key if not key.startswith('#') else '', str(val)])
    return re.sub(' +', ' ', command)

def apply(first, second):
    return dict(first, **second)

def product(*dimensions):
    return functools.reduce(lambda d1, d2: 
                  list(map(lambda tuple: apply(tuple[0], tuple[1]), itertools.product(d1, d2))),
                  dimensions)

def dimension(name, values):
    return list(map(lambda v : dict([(name, str(v))]), values))

class labeled:
    def __init__(self, name, opts):
        self.name = name
        self.opts = opts

    def serialize(self):
        tmp = {'name' : self.name,
               'opts' : self.opts}
        return json.dumps(tmp)

    @staticmethod
    def deserialize(line):
        tmp = json.loads(line)
        return labeled(tmp['name'], tmp['opts'])

if __name__ == '__main__':
    multiprocessing.freeze_support()