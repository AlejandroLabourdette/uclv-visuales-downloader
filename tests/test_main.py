from unittest.mock import patch

from click.testing import CliRunner

from uclv_visuales_downloader.main import download


runner = CliRunner()
FAKE_LINK = ("https://x/MyDir/file.mp4", "file.mp4", "MyDir/")


def test_basic_invocation():
    with patch("uclv_visuales_downloader.main.get_links", return_value=[]):
        result = runner.invoke(download, ["https://x/MyDir/"])
    assert result.exit_code == 0


def test_multiple_urls():
    with patch("uclv_visuales_downloader.main.get_links", return_value=[]) as mock_gl:
        runner.invoke(download, ["https://x/Dir1/", "https://x/Dir2/"])
    assert mock_gl.call_count == 2


def test_onlyvideos_passed_to_get_links():
    with patch("uclv_visuales_downloader.main.get_links", return_value=[]) as mock_gl:
        runner.invoke(download, ["--onlyvideos", "https://x/MyDir/"])
    args, _ = mock_gl.call_args
    assert args[1] is True


def test_dir_name_derived_from_url():
    with patch("uclv_visuales_downloader.main.get_links", return_value=[]) as mock_gl:
        runner.invoke(download, ["https://x/MyDir/"])
    _, kwargs = mock_gl.call_args
    assert kwargs.get("dir_to_save") == "MyDir/"


def test_skips_already_downloaded():
    with runner.isolated_filesystem():
        with patch("uclv_visuales_downloader.main.get_links", return_value=[FAKE_LINK]):
            with patch("uclv_visuales_downloader.main.was_already_downloaded", return_value=True):
                with patch("uclv_visuales_downloader.main.urllib.request.urlretrieve") as mock_retr:
                    runner.invoke(download, ["https://x/MyDir/"])
    mock_retr.assert_not_called()


def test_downloads_when_not_present():
    with runner.isolated_filesystem():
        with patch("uclv_visuales_downloader.main.get_links", return_value=[FAKE_LINK]):
            with patch("uclv_visuales_downloader.main.was_already_downloaded", return_value=False):
                with patch("uclv_visuales_downloader.main.urllib.request.urlretrieve") as mock_retr:
                    runner.invoke(download, ["https://x/MyDir/"])
    assert mock_retr.call_count == 1


def test_creates_output_dir():
    with runner.isolated_filesystem():
        with patch("uclv_visuales_downloader.main.get_links", return_value=[FAKE_LINK]):
            with patch("uclv_visuales_downloader.main.was_already_downloaded", return_value=False):
                with patch("uclv_visuales_downloader.main.urllib.request.urlretrieve"):
                    runner.invoke(download, ["https://x/MyDir/"])
        import os
        assert os.path.isdir("downloads/MyDir/")


def test_use_urls_file():
    with runner.isolated_filesystem():
        with open("urls", "w") as f:
            f.write("https://x/Dir1/\nhttps://x/Dir2/\n")
        with patch("uclv_visuales_downloader.main.get_links", return_value=[]) as mock_gl:
            result = runner.invoke(download, ["--use_urls_file"])
    assert result.exit_code == 0
    assert mock_gl.call_count == 2


def test_use_urls_file_skips_blank_lines():
    with runner.isolated_filesystem():
        with open("urls", "w") as f:
            f.write("https://x/Dir1/\n\nhttps://x/Dir2/\n")
        with patch("uclv_visuales_downloader.main.get_links", return_value=[]) as mock_gl:
            runner.invoke(download, ["--use_urls_file"])
    assert mock_gl.call_count == 2


def test_version_flag():
    result = runner.invoke(download, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
