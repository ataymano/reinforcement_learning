import argparse
import os
import datetime
from shutil import copyfile
from common import vw, client, vw_trainer


def train_on_days(start, end, connection_string, container, folder, tmp_folder, vw_path, vw_args, output_folder):
    model_path = os.path.join(tmp_folder, 'current')
    tenant_storage_client = client.TenantStorageClient(connection_string, container, folder, tmp_folder)
    trainer = vw.Vw(vw_path, vw_args, tmp_folder)

    for data in tenant_storage_client.range_days(start, end):
        trainer.train(data.get())

    tenant_storage_client.deploy(trainer.get_model())
    copyfile(trainer.get_model(), model_path)


def train(start, end, connection_string, container, folder, tmp_folder, vw_args, output_folder):
    model_path = os.path.join(tmp_folder, 'current')
    tenant_storage_client = client.TenantStorageClient(connection_string, container, folder, tmp_folder)
    trainer = vw_trainer.vw_trainer(vw_args)

    for data in tenant_storage_client.range_batches(start, end, 2):
        trainer.train(data)

    trainer.save_model(model_path)
    tenant_storage_client.deploy(model_path)


def main():
    parser = argparse.ArgumentParser("vw train")
    parser.add_argument("--folder", type=str, help="application folder")
    parser.add_argument("--vw", type=str, help="vw path")
    parser.add_argument("--start_date", type=str, help="start date")
    parser.add_argument("--end_date", type=str, help="end date")
    parser.add_argument("--tmp_folder", type=str, help="temporary folder")
    parser.add_argument("--container", type=str, help="application container")
    parser.add_argument("--connection_string", type=str, help="connection_string")
    parser.add_argument("--output_folder", type=str, help="output_folder")

    args = parser.parse_args()

    date_format = '%m/%d/%Y'

    os.makedirs(args.tmp_folder, exist_ok=True)

    start = datetime.datetime.strptime(args.start_date, date_format)
    end = datetime.datetime.strptime(args.end_date, date_format)
    if args.vw:
        train_on_days(start, end, args.connection_string, args.container, args.folder, args.tmp_folder, args.vw, '--cb_adf --dsjson', args.output_folder)
    else:
        train(start, end, args.connection_string, args.container, args.folder, args.tmp_folder, '--cb_adf --dsjson', args.output_folder)

if __name__ == '__main__':
    main()