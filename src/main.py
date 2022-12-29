from progress_bar import DownloadProgressBar as PB
from link_finder import get_links
from constants import *
from examples_doc import html_doc1
from examples_url import url1, url2, url3, url4


generator = get_links(url3, False)

# print('Downloading files:')
# if not os.path.isdir('sometha ing/otro/video.mp4'):
#     os.makedirs('some thing/otro/video.mp4')
# urllib.request.urlretrieve(url2, 'something/otro/video.mp4', PB(url2)) 

# for i in generator:
#     print(i)
