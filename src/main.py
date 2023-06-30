import click
import os
import urllib.request

from link_finder import get_links
from progress_bar import DownloadProgressBar
from constants import *
from utils import was_already_downloaded


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
    for link_data in links:
        url_to_file = link_data[0]
        file_name = link_data[1]
        dir_to_save = 'downloads/' + link_data[2]
        relative_path = dir_to_save + file_name

        if not os.path.isdir(dir_to_save):
            os.makedirs(dir_to_save)

        click.echo(f'dwnlding: {relative_path}')
        if not was_already_downloaded(url_to_file, relative_path):
            urllib.request.urlretrieve(
                url_to_file, relative_path, 
                DownloadProgressBar())
        else:
            click.echo('Already downloaded')

if __name__ == '__main__':
    download()
    