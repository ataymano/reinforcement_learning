import argparse
import os
import datetime
import json
from helpers import vw, logger, runtime, environment, runtime, path_generator, input_provider, pool, preprocessing, grid
import collections
import itertools
from enum import Enum


def cache(input_folder, output_folder, vw_path, start_date, end_date):
    env = environment.environment(
        vw_path = vw_path,
        runtime = runtime.local(),
        job_pool = pool.seq_pool(),
        txt_provider = input_provider.ps_logs_provider(input_folder, start_date, end_date),
        cache_path_gen = path_generator.cache_path_generator(output_folder))
        
    env.logger.log_scalar_global('Input folder', input_folder)
    env.logger.log_scalar_global('Output folder', output_folder)

    command = {
        '#method':'--cb_adf',
        '#format':'--dsjson',
        '#saveresume':'--save_resume',
        '#savepercounters':'--preserve_performance_counters'}
    vw.cache(command, env)

def extract_interactions_marginals(input_path, output_folder):
    namespaces = preprocessing.extract_namespaces(open(input_path, 'r'))
    marginals_path = os.path.join(output_folder, 'marginals.txt')
    interactions_path = os.path.join(output_folder, 'interactions.txt')
    marginals = preprocessing.get_marginals_grid('#marginals', namespaces[2])
    interactions = preprocessing.get_interactions_grid('#interactions', namespaces[0], namespaces[1])
    grid.points_to_file(marginals, marginals_path)
    grid.points_to_file(interactions, interactions_path)

def main():
    print("Extracting data from application logs...")

    parser = argparse.ArgumentParser("create cache")
    parser.add_argument("--input_folder", type=str, help="input folder")
    parser.add_argument("--output_folder", type=str, help="output folder")
    parser.add_argument("--vw", type=str, help="vw path")
    parser.add_argument("--start_date", type=str, help="start date")
    parser.add_argument("--end_date", type=str, help="end date")
    args = parser.parse_args()

    date_format = '%m/%d/%Y'

    os.makedirs(args.output_folder, exist_ok=True)

    start = datetime.datetime.strptime(args.start_date, date_format)
    end = datetime.datetime.strptime(args.end_date, date_format)

    cache(
        args.input_folder,
        args.output_folder,
        args.vw,
        start,
        end
    )

    first_log_file_path = input_provider.ps_logs_provider(args.input_folder, start, end).get()[0]
    extract_interactions_marginals(
        first_log_file_path,
        args.output_folder
    )


if __name__ == '__main__':
    main()
