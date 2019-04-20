
import argparse
import os
import datetime

from helpers import vw, logger, runtime, environment, runtime, path_generator, input_provider, pool, preprocessing, grid, sweep, command, dashboard

def dashboard_e2e(app_container, connection_string, app_folder, output, vw_path, start, end, tmp_folder, env, procs):
    cache_folder = os.path.join(tmp_folder, 'cache')
    model_folder = os.path.join(tmp_folder, 'model')
    pred_folder = os.path.join(tmp_folder, 'pred')
    logs_folder = os.path.join(tmp_folder, 'logs')
    env = environment.environment(
        vw_path = vw_path,
        runtime = runtime.mpi() if env == 'mpi' else runtime.local(),
        job_pool = pool.multiproc_pool(procs) if procs > 1 else pool.seq_pool(),
   #     txt_provider = input_provider.ps_logs_provider(input_folder, start, end),
        txt_provider = input_provider.azure_logs_provider(app_container, connection_string, app_folder, start, end, logs_folder),
        cache_path_gen = path_generator.cache_path_generator(cache_folder),
        pred_path_gen = path_generator.pred_path_generator(pred_folder),
        model_path_gen = path_generator.model_path_generator(model_folder),
        cache_provider = input_provider.cache_provider(cache_folder))

    base_command = {
        '#method':'--cb_adf',
        '#format':'--dsjson',
        '#saveresume':'--save_resume',
        '#savepercounters':'--preserve_performance_counters'}
    vw.cache(base_command, env)
    
    namespaces = preprocessing.extract_namespaces(open(env.txt_provider.get()[0], 'r', encoding='utf-8'))

    marginals_grid = preprocessing.get_marginals_grid('#marginals', namespaces[2])[:2]
    interactions_grid = preprocessing.get_interactions_grid('#interactions', namespaces[0], namespaces[1])[:2]

    multi_grid = grid.generate_test(interactions_grid, marginals_grid)
    best = sweep.sweep(multi_grid, env, base_command)

    predict_opts = {'#method': '--cb_explore_adf --epsilon 0.2'}
    commands = list(map(lambda lo: command.labeled(lo.name, command.apply(lo.opts, predict_opts)), best))
    vw.predict(commands, env)
    dashboard.create(output, env)


def main():
    parser = argparse.ArgumentParser("dashboard e2e")
    parser.add_argument("--app_folder", type=str, help="app folder")
    parser.add_argument("--output", type=str, help="dashboard file")
    parser.add_argument("--vw", type=str, help="vw path")
    parser.add_argument("--start_date", type=str, help="start date")
    parser.add_argument("--end_date", type=str, help="end date")
    parser.add_argument("--tmp_folder", type=str, help="temporary folder")
    parser.add_argument("--app_container", type=str, help="app_container")
    parser.add_argument("--connection_string", type=str, help="connection_string")
    parser.add_argument("--procs", type=int, help="procs")
    parser.add_argument("--env", type=str, help="environment (local / mpi)")
    args = parser.parse_args()

    date_format = '%m/%d/%Y'

    os.makedirs(args.tmp_folder, exist_ok=True)

    start = datetime.datetime.strptime(args.start_date, date_format)
    end = datetime.datetime.strptime(args.end_date, date_format)

    dashboard_e2e(args.app_container, args.connection_string, args.app_folder, args.output, args.vw, start, end, args.tmp_folder, args.env, args.procs)


if __name__ == '__main__':
    main()
