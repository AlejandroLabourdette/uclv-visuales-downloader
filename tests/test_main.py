from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from uclv_visuales_downloader.main import download


runner = CliRunner()
FAKE_LINK = ("https://x/MyDir/file.mp4", "file.mp4", "MyDir/")


def _make_fake_session(content=b'x' * 100):
    mock_resp = MagicMock()
    mock_resp.iter_content.return_value = iter([content])
    mock_resp.raise_for_status.return_value = None
    mock_sess = MagicMock()
    mock_sess.get.return_value = mock_resp
    return mock_sess


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
        import os
        os.makedirs("downloads/MyDir/")
        with open("downloads/MyDir/file.mp4", "wb") as f:
            f.write(b"x" * 100)
        fake_session = _make_fake_session()
        with patch("uclv_visuales_downloader.main.get_links", return_value=[FAKE_LINK]):
            with patch("uclv_visuales_downloader.main.get_remote_file_size", return_value=100):
                with patch("uclv_visuales_downloader.main._make_session", return_value=fake_session):
                    runner.invoke(download, ["https://x/MyDir/"])
    fake_session.get.assert_not_called()


def test_downloads_when_not_present():
    with runner.isolated_filesystem():
        fake_session = _make_fake_session()
        with patch("uclv_visuales_downloader.main.get_links", return_value=[FAKE_LINK]):
            with patch("uclv_visuales_downloader.main.get_remote_file_size", return_value=100):
                with patch("uclv_visuales_downloader.main._make_session", return_value=fake_session):
                    runner.invoke(download, ["https://x/MyDir/"])
    assert fake_session.get.call_count == 1


def test_creates_output_dir():
    with runner.isolated_filesystem():
        fake_session = _make_fake_session()
        with patch("uclv_visuales_downloader.main.get_links", return_value=[FAKE_LINK]):
            with patch("uclv_visuales_downloader.main.get_remote_file_size", return_value=100):
                with patch("uclv_visuales_downloader.main._make_session", return_value=fake_session):
                    runner.invoke(download, ["https://x/MyDir/"])
        import os
        assert os.path.isdir("downloads/MyDir/")


def test_resumes_partial_download():
    with runner.isolated_filesystem():
        import os
        os.makedirs("downloads/MyDir/")
        with open("downloads/MyDir/file.mp4", "wb") as f:
            f.write(b"x" * 50)
        fake_session = _make_fake_session()
        with patch("uclv_visuales_downloader.main.get_links", return_value=[FAKE_LINK]):
            with patch("uclv_visuales_downloader.main.get_remote_file_size", return_value=100):
                with patch("uclv_visuales_downloader.main._make_session", return_value=fake_session):
                    runner.invoke(download, ["https://x/MyDir/"])
    call_kwargs = fake_session.get.call_args
    assert call_kwargs[1]['headers'] == {'Range': 'bytes=50-'}


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
