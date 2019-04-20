import multiprocessing

from helpers import vw, vw_opts

def _top(candidates, k):
    if k >= len(candidates):
        return candidates

    return sorted(candidates, key = lambda item: item[1])[:k]

def _promote(candidates, grid_config, env):
    return list(map(lambda item: item[0], _top(candidates, grid_config.promote)))

def _output(candidates, grid_config, env):
    return list(map(lambda item: vw_opts.labeled(grid_config.name + str(item[0]), item[1][0]), enumerate(_top(candidates, grid_config.output))))

def _iteration(grid, env):
    candidates = vw.train(grid.points, env)
    env.logger.info('Local job is finished. Reducing...')
    candidates = env.runtime.reduce(candidates)
    for c in candidates:
        env.logger.info(str(vw_opts.to_commandline(c[0])) + ': ' + str(c[1]))
    env.logger.info('All candidates are reduced.')
    return _promote(candidates, grid.config, env), _output(candidates, grid.config, env)

def sweep(multi_grid, env, base_command = {}):
    promoted = [base_command]
    result = []
    for grid in multi_grid:
        env.logger.info('Iteration ' + grid.config.name)
        grid.points = env.runtime.map(vw_opts.product(promoted, grid.points))
        promoted, output = _iteration(grid, env)
        result = result + output
    return result

if __name__ == '__main__':
    multiprocessing.freeze_support()
