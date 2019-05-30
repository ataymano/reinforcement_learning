import argparse
import os
import datetime
from common import vw, client, vw_trainer


def deploy(connection_string, container, model_path):
    tenant_storage_client = client.TenantStorageClient(connection_string, container, None, None)
    tenant_storage_client.deploy(model_path)

def main():
    parser = argparse.ArgumentParser("vw deploy")
    parser.add_argument("--model", type=str, help="model path")
    parser.add_argument("--container", type=str, help="application container")
    parser.add_argument("--connection_string", type=str, help="connection_string")

    args = parser.parse_args()
    deploy(args.connection_string, args.container, args.model)

if __name__ == '__main__':
    main()