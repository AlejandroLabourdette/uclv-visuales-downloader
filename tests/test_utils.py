from unittest.mock import MagicMock, patch

from uclv_visuales_downloader.utils import was_already_downloaded


PATCH_TARGET = "uclv_visuales_downloader.utils.urllib.request.urlopen"


def make_mock_urlopen(content_length: int):
    mock = MagicMock()
    mock.info.return_value = {"Content-Length": str(content_length)}
    return mock


def test_returns_true_when_sizes_match(tmp_path):
    f = tmp_path / "video.mp4"
    f.write_bytes(b"x" * 100)
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(100)):
        assert was_already_downloaded("https://x/video.mp4", str(f)) is True


def test_returns_false_when_local_smaller(tmp_path):
    f = tmp_path / "video.mp4"
    f.write_bytes(b"x" * 50)
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(100)):
        assert was_already_downloaded("https://x/video.mp4", str(f)) is False


def test_returns_false_when_local_larger(tmp_path):
    f = tmp_path / "video.mp4"
    f.write_bytes(b"x" * 200)
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(100)):
        assert was_already_downloaded("https://x/video.mp4", str(f)) is False


def test_returns_false_when_file_missing(tmp_path):
    missing = tmp_path / "nonexistent.mp4"
    with patch(PATCH_TARGET, return_value=make_mock_urlopen(100)):
        assert was_already_downloaded("https://x/video.mp4", str(missing)) is False
