from unittest.mock import MagicMock, patch

from uclv_visuales_downloader.utils import get_remote_file_size


PATCH_TARGET = "uclv_visuales_downloader.utils.requests.head"


def make_mock_head(content_length: int):
    mock = MagicMock()
    mock.headers = {"Content-Length": str(content_length)}
    mock.raise_for_status.return_value = None
    return mock


def test_returns_remote_size():
    with patch(PATCH_TARGET, return_value=make_mock_head(100)):
        assert get_remote_file_size("https://x/video.mp4") == 100


def test_returns_minus_one_when_no_content_length():
    mock = MagicMock()
    mock.headers = {}
    mock.raise_for_status.return_value = None
    with patch(PATCH_TARGET, return_value=mock):
        assert get_remote_file_size("https://x/video.mp4") == -1
