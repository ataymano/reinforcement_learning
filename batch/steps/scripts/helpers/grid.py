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


def generate_test(interactions_grid, marginals_grid):
    return [grid(dimension('--power_t', [1e-5, 0.5]),
                 configuration(name = 'testgrid')),
            grid(product(interactions_grid, marginals_grid),
                 configuration(name='interactions', output=1))]


def generate(interactions_grid, marginals_grid):
    hyper1_points = product(dimension('--power_t', [1e-09, 1.4953487812212204e-07, 2.2360679774997894e-05, 0.0033437015248821097, 0.5]),
                      dimension('--l1', [1e-09, 1e-07, 1e-05, 0.001, 0.1]),
                      dimension('-l', [1e-05, 0.00036840314986403866, 0.013572088082974531, 0.5]))
    return [grid(hyper1_points,
                 configuration(name = 'hyper1', output = 1, promote = 1)),
            grid(dimension('--cb_type', ['ips', 'mtr']),
                 configuration(name='cbtype')),
            grid(product(interactions_grid, marginals_grid),
                 configuration(name = 'interactions', output = 1)),
            grid(hyper1_points,
                 configuration(name = 'hyper2', output = 1, promote = 1))]

if __name__ == '__main__':
    multiprocessing.freeze_support()

    