import multiprocessing

from helpers import vw, command


def _top(candidates, k):
    if k >= len(candidates):
        return candidates

    return sorted(candidates, key = lambda item: item[1])[:k]


def _promote(candidates, grid_config, env):
    step_name = '[' + grid_config.name + '] '
    result = list(map(lambda item: item[0], _top(candidates, grid_config.promote)))
    for c in result:
        env.logger.info(step_name + 'Promoted: ' + command.to_commandline(c))
    return result


def _output(candidates, grid_config, env):
    step_name = '[' + grid_config.name + '] '
    result = dict(map(lambda item: (grid_config.name + str(item[0]), item[1][0]), enumerate(_top(candidates, grid_config.output))))
    for k, v in result.items():
        env.logger.info(step_name +  'Output: [' + k + '] ' + command.to_commandline(v))
    return result


def _iteration(grid, env):
    candidates = vw.train(grid.points, env)
    step_name = '[' + grid.config.name + '] '
    env.logger.info(step_name +  'Local job is finished. Reducing...')
    candidates = env.runtime.reduce(candidates)
    for c in candidates:
        env.logger.info(step_name + str(command.to_commandline(c[0])) + ': ' + str(c[1]))
    env.logger.info(step_name + 'All candidates are reduced.')
    return _promote(candidates, grid.config, env), _output(candidates, grid.config, env)


def sweep(multi_grid, env, base_command = {}):
    promoted = [base_command]
    result = {}
    for grid in multi_grid:
        step_name = '[' + grid.config.name + '] '
        env.logger.info(step_name + 'Started...')
        grid.points = env.runtime.map(command.product(promoted, grid.points))
        promoted, output = _iteration(grid, env)
        result = dict(result, **output)
    return result

if __name__ == '__main__':
    multiprocessing.freeze_support()
