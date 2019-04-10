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

def generate():
 #   return [product(dimension('--power_t', [1e-5, 0.5, 4]),
 #                     dimension('--l1', [1e-9, 0.1, 5]),
 #                     dimension('-l', [1e-5, 0.5, 4])),
 #           dimension('--cb_type', ['mtr', 'ips'])]
     return [grid(product(dimension('--power_t', [1e-5, 0.5, 2, 4]),
                      dimension('--l1', [1e-9, 0.1, 2, 5]),
                      dimension('--cb_type', ['mtr', 'ips'])),
                  configuration(name = 'my_grid', output = 2))]
 #     return [product(dimension('--power_t', [1e-5, 0.5]))]

if __name__ == '__main__':
    multiprocessing.freeze_support()

    