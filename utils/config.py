import json

def load_config(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        config = json.load(file)

    return config


def get_server_config(config: dict) -> dict:
    return config.get('server', {})


def get_request_config(config: dict) -> list:
    return config.get('requests', [])

def get_load_balancer_config(config: dict) -> dict:
    return config.get('load_balancer', {})