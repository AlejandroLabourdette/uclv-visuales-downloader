from bs4 import BeautifulSoup, element
from examples import html_doc1


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
        print(f'{link_type}, {link}')



get_links(html_doc1)
