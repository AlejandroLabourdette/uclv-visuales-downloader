import click
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .link_finder import get_links
from .progress_bar import DownloadProgressBar
from .constants import *
from .utils import get_remote_file_size

_CHUNK_SIZE = 1024 * 1024  # 1 MB


def _make_session() -> requests.Session:
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _download_file(session: requests.Session, url: str, path: str):
    remote_size = get_remote_file_size(url)
    local_size = os.stat(path).st_size if os.path.exists(path) else 0

    if remote_size != -1 and local_size == remote_size:
        click.echo('Already downloaded')
        return

    headers, mode, initial_pos = {}, 'wb', 0
    if local_size > 0 and (remote_size == -1 or local_size < remote_size):
        headers['Range'] = f'bytes={local_size}-'
        mode, initial_pos = 'ab', local_size
    # local_size > remote_size → corrupt file, rewrite from scratch

    response = session.get(url, headers=headers, stream=True, timeout=30)
    response.raise_for_status()

    progress = DownloadProgressBar(total_size=remote_size, initial=initial_pos)
    with open(path, mode) as f:
        for chunk in response.iter_content(chunk_size=_CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                progress.update(len(chunk))
    progress.finish()


@click.command()
@click.version_option(version='0.1.0')
@click.argument('urls', nargs=-1)
@click.option('--onlyvideos', is_flag=True, help='download only videos')
@click.option('--use_urls_file', is_flag=True, help='download specified urls in "urls" file')
def download(urls, onlyvideos, use_urls_file):
    '''Download full directory from specified URL's'''
    url: str
    if use_urls_file:
        with open('urls') as file_urls:
            for url in file_urls:
                url = url.removesuffix('\n')
                if url == '':
                    continue
                download_url(url, onlyvideos)
    for url in urls:
        download_url(url, onlyvideos)


def download_url(url, onlyvideos):
    click.echo(f'Downloading from url: {url}')
    dir_name = url.split('/')[-2] + '/'
    click.echo(f'Saving under dir: {dir_name}')
    links = get_links(url, onlyvideos, dir_to_save=dir_name)
    session = _make_session()
    for link_data in links:
        url_to_file = link_data[0]
        file_name = link_data[1]
        dir_to_save = 'downloads/' + link_data[2]
        relative_path = dir_to_save + file_name

        if not os.path.isdir(dir_to_save):
            os.makedirs(dir_to_save)

        click.echo(f'dwnlding: {relative_path}')
        _download_file(session, url_to_file, relative_path)


if __name__ == '__main__':
    download()
