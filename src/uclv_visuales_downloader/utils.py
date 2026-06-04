import requests


def get_remote_file_size(url: str, session: requests.Session = None) -> int:
    requester = session or requests
    response = requester.head(url, timeout=30)
    response.raise_for_status()
    return int(response.headers.get('Content-Length', -1))
