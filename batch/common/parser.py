import numpy as np

class Base64Loader:
    @staticmethod
    def _load_tensor(line):
        import numpy as np
        import base64
        import struct

        prefix, value = line.split(';')
        #many hacks
        shape = struct.unpack('4Q', base64.b64decode(prefix))
        shape = shape[1:]
        return np.array(struct.unpack('784f', base64.b64decode(value))).reshape(shape)

    @staticmethod
    def load(line):
        import json
        pos = line.find('|')
        label = int(line[0:pos])

        obj = json.loads(line[pos+1:])
        features = {}
        for k, v in obj.items():
            features[k] = Base64Loader._load_tensor(v)
        return {'label': label, 'features': features}


