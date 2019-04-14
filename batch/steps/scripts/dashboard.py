import argparse
import os
import datetime
from helpers import dashboard, path_generator, input_provider, environment, pool

def create_dashboard(logs, start, end, predictions, dashboard_path):
    env = environment.environment(
        vw_path = None,
        runtime = None,
        job_pool = pool.seq_pool(),
        txt_provider = input_provider.ps_logs_provider(logs, start, end),
        pred_path_gen = path_generator.pred_path_generator(predictions),
        cache_path_gen = path_generator.cache_path_generator('fake')
        )
    env.logger.log_scalar_global('Logs', logs)
    env.logger.log_scalar_global('Predictions', predictions)
    env.logger.log_scalar_global('Dashboard', dashboard_path)
    dashboard.create(dashboard_path, env)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--logs', help="log", required=True)
    parser.add_argument("--start_date", type=str, help="start date")
    parser.add_argument("--end_date", type=str, help="end date")
    parser.add_argument('--predictions', help="predict", required=True)
    parser.add_argument('--dashboard', help="dashboard", required=True)
    args = parser.parse_args()

    date_format = '%m/%d/%Y'
    start = datetime.datetime.strptime(args.start_date, date_format)
    end = datetime.datetime.strptime(args.end_date, date_format)

    os.makedirs(args.dashboard, exist_ok=True)
    output_path = os.path.join(
        args.dashboard,
        'dashboard.txt'
    )
    create_dashboard(args.logs, start, end, args.predictions, output_path)
