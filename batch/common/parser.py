class Base64Tensor:
    @staticmethod
    def parse(line):
        import numpy as np
        import base64
        import struct

        prefix, value = line.split(';')
        #many hacks
        shape = struct.unpack('4Q', base64.b64decode(prefix))
        shape = shape[1:]
        return np.array(struct.unpack('%df' % np.prod(shape), base64.b64decode(value))).reshape(shape)

    @staticmethod
    def parse_dict(context):
        return dict(map(lambda kv: (kv[0], Base64Tensor.parse(kv[1])), \
            context.items()))

class CbDsjsonParser:
    @staticmethod
    def parse(line):
        import json
        obj = json.loads(line)
        return {'features': Base64Tensor.parse_dict(obj['c']), 'label': obj['_labelIndex'], 'cost': obj['_label_cost']}
