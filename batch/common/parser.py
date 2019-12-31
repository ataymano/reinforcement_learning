from vowpalwabbit import pyvw
import numpy as np
from common.types import Problem, Features
from common.cb import CB

class _DSJsonParserDense:
    def __init__(self, num_weights):
        self.num_weights = num_weights

    def parse(self, vw_single_ex):
        result = np.zeros(shape=(vw_single_ex.num_namespaces(), self.num_weights))
        for i in range(0, vw_single_ex.num_namespaces() - 1):
            for j in range(0, vw_single_ex.num_features_in(i)):
                result[i, vw_single_ex.feature(i, j)] = vw_single_ex.feature_weight(i, j)
        return result


class _DSJsonParserSparse:
    def parse(self, vw_single_ex):
        x = []
        y = []
        v = []
        for i in range(0, vw_single_ex.num_namespaces() - 1):
            for j in range(0, vw_single_ex.num_features_in(i)):
                x.append(vw_single_ex.namespace(i))
                y.append(vw_single_ex.feature(i, j))
                v.append(vw_single_ex.feature_weight(i, j))
        return [x, y], v


class DSJsonParser:
    def __init__(self, problem, is_dense):
        self.problem = problem
        if problem == problem.CB:
            self.vw = pyvw.vw('--cb_adf --dsjson --quiet')
        else:
            raise NotImplemented()
        self.impl = _DSJsonParserDense(self.vw.num_weights()) if is_dense else _DSJsonParserSparse()

    def parse(self, line):
        vw_multi_ex = self.vw.parse(line)
        if self.problem == Problem.CB:
            yield Features.CONTEXT, self.impl.parse(vw_multi_ex[0]), []
            for i in range(1, len(vw_multi_ex) - 1):
                yield Features.ACTION, self.impl.parse(vw_multi_ex[i]), CB.get_label(vw_multi_ex[i])
        else:
            raise NotImplemented()
