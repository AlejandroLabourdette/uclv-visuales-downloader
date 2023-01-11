import os
import urllib.request


def was_already_downloaded(url_to_file: str, relative_path: str):
    online_file_len = int(urllib.request.urlopen(url_to_file).info()['Content-Length'])
    stored_file_len = os.stat(relative_path).st_size if os.path.exists(relative_path) else 0
    return online_file_len == stored_file_len
