import argparse
import os
import glob
from helpers import vw, utils, grid_generator, path_generator, vw_opts, sweep, pool

def vw_sweep(vw_path, input_folder, output, procs, models_path):
    model_path_gen = path_generator.folder_path_generator(models_path)
    pattern=os.path.join(input_folder, '*.cache')
    caches = list(glob.glob(pattern))
    grid = grid_generator.generate()
    p = pool.multiproc_pool(procs)
    result = sweep.multi(vw_path, caches, model_path_gen, grid, p)
   
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, 'w') as fout:
        fout.write(vw_opts.serialize(result[0]))

def main():
    print("Extracting data from application logs...")

    parser = argparse.ArgumentParser("create cache")
    parser.add_argument("--input_folder", type=str, help="input folder")
    parser.add_argument("--output", type=str, help="output")
    parser.add_argument("--vw", type=str, help="vw path")
    parser.add_argument("--procs", type=int, help="procs")
    parser.add_argument("--models", type=str, help="models folder")
    args = parser.parse_args()

    utils.logger('Input folder', args.input_folder)
    utils.logger('Output', args.output)

    print('Sweeping...')
    vw_sweep(
        args.vw,
        args.input_folder,
        args.output,
        args.procs,
        args.models
    )
    print('Done.')


if __name__ == '__main__':
    main()
