import urllib.request
import sys

from bs4 import BeautifulSoup, element
from progress_bar import DownloadProgressBar as PB
from examples_doc import html_doc1
from examples_url import url1, url2

def get_links(html_doc: str):
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

        yield f'{link_type}, {link}'



print('Downloading files:')
urllib.request.urlretrieve(url2, 'video.mp4', PB('pepito')) 
# generator = get_links(html_doc1)
# for i in generator:
#     print(i)
