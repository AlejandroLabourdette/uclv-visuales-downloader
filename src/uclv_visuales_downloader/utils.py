import requests


def get_remote_file_size(url: str) -> int:
    response = requests.head(url, timeout=10)
    response.raise_for_status()
    return int(response.headers.get('Content-Length', -1))
