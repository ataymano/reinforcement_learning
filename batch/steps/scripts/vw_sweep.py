import argparse
import os
import glob
from helpers import vw, logger, grid, path_generator, vw_opts, sweep, pool, environment, runtime

def vw_sweep(vw_path, input_folder, output, procs, env, models_path):
    pattern=os.path.join(input_folder, '*.cache')
    caches = sorted(list(glob.glob(pattern)))
    base_command = {
        '#method':'--cb_adf',
        '#format':'--dsjson',
        '#saveresume':'--save_resume',
        '#savepercounters':'--preserve_performance_counters'}
    multi_grid = grid.generate()
    env = environment.environment(
        vw_path = vw_path,
        runtime = runtime.mpi() if env == 'mpi' else runtime.local(),
        job_pool = pool.multiproc_pool(procs) if procs > 1 else pool.seq_pool(),
        model_path_gen = path_generator.model_path_generator(models_path),
        )

    env.logger.log_scalar_global('Input folder', input_folder)
    env.logger.log_scalar_global('Output', output)
    env.logger.trace('Sweeping...')

    result = sweep.sweep(caches, multi_grid, env, base_command)
    env.logger.trace('Done.')

    os.makedirs(os.path.dirname(output), exist_ok=True)
    open(output, 'w').writelines(map(lambda r : r.serialize() + '\n', result))

def main():
    parser = argparse.ArgumentParser("Sweep")
    parser.add_argument("--input_folder", type=str, help="input folder")
    parser.add_argument("--output", type=str, help="output")
    parser.add_argument("--vw", type=str, help="vw path")
    parser.add_argument("--procs", type=int, help="procs")
    parser.add_argument("--env", type=str, help="environment (local / mpi)")
    parser.add_argument("--models", type=str, help="models folder")
    args = parser.parse_args()


    vw_sweep(
        args.vw,
        args.input_folder,
        args.output,
        args.procs,
        args.env,
        args.models
    )

if __name__ == '__main__':
    main()
