from helpers import vw_opts
from helpers.vw_opts import dimension, product

class configuration:
    def __init__(self, name, promote = 1, output = 1):
        self.name = name
        self.promote = promote
        self.output = output

class grid:
    def __init__(self, points, config):
        self.points = points
        self.config = config

def points_from_file(fname, limit = -1):
    result = list(map(lambda line: vw_opts.deserialize(line), open(fname, 'r')))
    return result if limit == -1 or len(result) < limit else result[:limit]

def points_to_file(points, fname):
    open(fname, 'w').writelines(map(lambda p : vw_opts.serialize(p) + '\n', points))


def generate_test():
 #   return [product(dimension('--power_t', [1e-5, 0.5, 4]),
 #                     dimension('--l1', [1e-9, 0.1, 5]),
 #                     dimension('-l', [1e-5, 0.5, 4])),
 #           dimension('--cb_type', ['mtr', 'ips'])]
     return [grid(dimension('--power_t', [1e-5, 0.5, 2, 4]),
                  configuration(name = 'testgrid', output = 2))]
 #     return [product(dimension('--power_t', [1e-5, 0.5]))]

def generate(interactions_grid, marginals_grid):
     return [grid(dimension('--power_t', [1e-5, 0.5, 2, 4]),
                  configuration(name = 'testgrid', output = 2, promote = 2)),
             grid(product(interactions_grid, marginals_grid),
                  configuration(name = 'final', output = 1))]

if __name__ == '__main__':
    multiprocessing.freeze_support()

    