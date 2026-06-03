from unittest.mock import MagicMock, patch

from uclv_visuales_downloader.link_finder import get_links
from examples_doc import html_doc1, html_doc2, html_doc3


EMPTY_HTML = '<html><body><table></table></body></html>'
BASE_URL_DOC1 = "https://visuales.uclv.cu/Infantiles/Cubanos/Elpidio Valdes/"
BASE_URL_DOC2 = "https://visuales.uclv.cu/Series/Ingles/Genius/Genius x 1/"
BASE_URL_DOC3 = "https://visuales.uclv.cu/Series/"

PATCH_TARGET = "uclv_visuales_downloader.link_finder.urllib.request.urlopen"


def make_mock_urlopen(html: str):
    mock = MagicMock()
    mock.read.return_value = html.encode()
    return mock


# --- Tests con html_doc2 (VID + IMG + TXT + [   ], sin DIRs) ---

def test_yields_video_links():
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results = list(get_links(BASE_URL_DOC2, only_videos=False))
    filenames = [r[1] for r in results]
    assert any(f.endswith('.mkv') or f.endswith('.mp4') for f in filenames)


def test_yields_img_links():
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results = list(get_links(BASE_URL_DOC2, only_videos=False))
    filenames = [r[1] for r in results]
    assert any(f.endswith('.jpg') for f in filenames)


def test_yields_txt_links():
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results = list(get_links(BASE_URL_DOC2, only_videos=False))
    filenames = [r[1] for r in results]
    assert any(f.endswith('.srt') for f in filenames)


def test_skips_unknown_type():
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results = list(get_links(BASE_URL_DOC2, only_videos=False))
    filenames = [r[1] for r in results]
    assert not any(f.endswith('.nfo') for f in filenames)


def test_only_videos_filters_img_and_txt():
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results_all = list(get_links(BASE_URL_DOC2, only_videos=False))
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results_vid = list(get_links(BASE_URL_DOC2, only_videos=True))
    assert len(results_vid) < len(results_all)
    filenames_vid = [r[1] for r in results_vid]
    assert not any(f.endswith('.jpg') or f.endswith('.srt') for f in filenames_vid)


def test_result_is_tuple_of_three():
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results = list(get_links(BASE_URL_DOC2, only_videos=False))
    assert len(results) > 0
    for item in results:
        assert len(item) == 3


def test_url_decoding_brackets():
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results = list(get_links(BASE_URL_DOC2, only_videos=False))
    filenames = [r[1] for r in results]
    assert any('[eztv]' in f for f in filenames)
    assert not any('%5b' in f.lower() for f in filenames)


def test_url_decoding_spaces():
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results = list(get_links(BASE_URL_DOC2, only_videos=False))
    filenames = [r[1] for r in results]
    assert any(' ' in f for f in filenames)
    assert not any('%20' in f for f in filenames)


def test_parentdir_row_skipped():
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(html_doc2)):
        results = list(get_links(BASE_URL_DOC2, only_videos=False))
    filenames = [r[1] for r in results]
    assert not any('Parent Directory' in f for f in filenames)


# --- Tests con html_doc1 (VIDs + 2 DIRs, caracteres acentuados) ---

def test_url_decoding_accents():
    def fake_urlopen(url):
        if url == BASE_URL_DOC1:
            return make_mock_urlopen(html_doc1)
        return make_mock_urlopen(EMPTY_HTML)

    with patch(PATCH_TARGET, side_effect=fake_urlopen):
        results = list(get_links(BASE_URL_DOC1, only_videos=False))
    filenames = [r[1] for r in results]
    assert any('é' in f for f in filenames)
    assert not any('%c3%a9' in f.lower() for f in filenames)


# --- Tests de recursión con html_doc3 → html_doc2 ---

def test_recurse_into_dirs():
    def fake_urlopen(url):
        if url == BASE_URL_DOC3:
            return make_mock_urlopen(html_doc3)
        return make_mock_urlopen(html_doc2)

    with patch(PATCH_TARGET, side_effect=fake_urlopen):
        results = list(get_links(BASE_URL_DOC3, only_videos=False))
    assert len(results) > 0


def test_dir_path_accumulated():
    def fake_urlopen(url):
        if url == BASE_URL_DOC3:
            return make_mock_urlopen(html_doc3)
        return make_mock_urlopen(html_doc2)

    with patch(PATCH_TARGET, side_effect=fake_urlopen):
        results = list(get_links(BASE_URL_DOC3, only_videos=False))
    dirs = [r[2] for r in results]
    assert all(d != '' for d in dirs)
    assert any('Completar/' in d for d in dirs)


def test_only_videos_flag_propagates_through_recursion():
    def fake_urlopen(url):
        if url == BASE_URL_DOC3:
            return make_mock_urlopen(html_doc3)
        return make_mock_urlopen(html_doc2)

    with patch(PATCH_TARGET, side_effect=fake_urlopen):
        results = list(get_links(BASE_URL_DOC3, only_videos=True))
    filenames = [r[1] for r in results]
    assert not any(f.endswith('.jpg') or f.endswith('.srt') for f in filenames)
