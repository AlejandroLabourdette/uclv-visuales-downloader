import urllib.request
import urllib.parse

from typing import Generator
from bs4 import BeautifulSoup, element
from constants import *


def get_links(url: str, only_videos: bool, dir_to_save='') -> Generator[ str, str, str]:
    '''
    Generator that return all downloadable links under url.

    Returns (link_type, link, dir_to_save)
    * link: URL to the file
    * file_name: name of the file to be downloaded
    * dir_to_save: relative path to the file unquoted
    '''
    html_doc = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    table_rows = soup.find_all('tr')
    tr: element.Tag
    for tr in table_rows:
        table_data = tr.find_all('td')
        if len(table_data) == 0:
            continue

        td0: element.Tag = table_data[0]
        td1: element.Tag = table_data[1]

        link_type = td0.img.get('alt')
        link = td1.a.get('href')

        if link_type == DIR:
            new_url = url+link
            new_dir_to_save = dir_to_save + urllib.parse.unquote(link)
            yield from get_links(new_url, only_videos, new_dir_to_save)
        elif link_type in [VID, IMG, TXT]:
            if only_videos and link_type != VID:
                continue
            url_to_file = url+link
            file_name = urllib.parse.unquote(link)
            yield url_to_file, file_name, dir_to_save
