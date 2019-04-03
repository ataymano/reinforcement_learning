from steps.scripts.helpers.vw_opts import dimension, cartesian

def generate():
    return [cartesian(dimension('--power_t', [1e-5, 0.5, 4]),
                      dimension('--l1', [1e-9, 0.1, 5]),
                      dimension('-l', [1e-5, 0.5, 4])),
            dimension('--cb_type', ['mtr', 'ips'])]

if __name__ == '__main__':
    multiprocessing.freeze_support()

    