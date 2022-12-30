import click
import os
import urllib.request

from link_finder import get_links
from progress_bar import DownloadProgressBar
from constants import *


@click.command()
@click.version_option(version='0.1.0')
@click.argument('urls', nargs=-1)
@click.option('--onlyvideos', is_flag=True, help='download only videos')
def download(urls, onlyvideos):
    '''Download full directory from specified URL's'''
    url: str
    for url in urls:
        click.echo(f'Downloading from url: {url}')
        dir_name = url.split('/')[-2] + '/'
        click.echo(f'Saving under dir: {dir_name}')
        links = get_links(url, onlyvideos, dir_to_save=dir_name)
        for link_data in links:
            url_to_file = link_data[0]
            file_name = link_data[1]
            dir_to_save = link_data[2]
            relative_path = dir_to_save + file_name

            if not os.path.isdir(dir_to_save):
                os.makedirs(dir_to_save)

            click.echo(f'dwnlding: {relative_path}')
            urllib.request.urlretrieve(
                url_to_file, relative_path, 
                DownloadProgressBar()) 


if __name__ == '__main__':
    download()
    