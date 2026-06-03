# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A CLI tool that recursively downloads entire directory trees served by Apache's
auto-generated directory listings at `https://visuales.uclv.cu`. It scrapes the
HTML index pages, walks subdirectories, and downloads the underlying media files.

## Commands

Setup (requires [uv](https://docs.astral.sh/uv/getting-started/installation/)):

```bash
uv sync
```

Run:

```bash
uv run visuales '<url>'                 # download one directory (quote the URL)
uv run visuales '<url1>' '<url2>'        # multiple directories
uv run visuales --onlyvideos '<url>'     # skip images/text/sound, videos only
uv run visuales --use_urls_file          # read URLs from a file named `urls` (one per line) in cwd
uv run visuales --help
uv run visuales --version
```

There is no build step, linter config, or test suite. To verify scraping logic
manually, the `src/uclv_visuales_downloader/examples_doc.py` module holds two real captured Apache index
pages (`html_doc1`, `html_doc2`) that can be fed to `BeautifulSoup` in a REPL,
and `src/uclv_visuales_downloader/examples_url.py` holds sample live URLs.

## Architecture

The flow is a single pass: `main.download` → `link_finder.get_links` (generator)
→ download each yielded file.

- **`src/uclv_visuales_downloader/main.py`** — Click entrypoint. Derives the output directory name from
  the second-to-last URL path segment, then iterates the generator from
  `get_links`. Files are written under `downloads/<remote dir tree>/`. Before
  each download it calls `was_already_downloaded` to skip files already fully
  present (resume support).

- **`src/uclv_visuales_downloader/link_finder.py`** — The scraper. `get_links` fetches an index page,
  parses each table row, and reads two cells: the icon's `alt` text (the file
  type marker) and the link's `href`. On a `[DIR]` row it recurses into the
  subdirectory, accumulating the relative path in `dir_to_save`; on a media row
  it yields `(url_to_file, file_name, dir_to_save)`. URLs are URL-decoded with
  `urllib.parse.unquote` for local filenames.

- **`src/uclv_visuales_downloader/constants.py`** — The Apache `alt`-text markers (`[VID]`, `[DIR]`,
  `[IMG]`, `[TXT]`, `[SND]`) that drive row classification in `get_links`. These
  string values are the contract with the remote server's HTML; adding support
  for a new file type means adding its marker here and to the membership check
  in `link_finder.get_links`.

- **`src/uclv_visuales_downloader/utils.py`** — `was_already_downloaded` compares the remote
  `Content-Length` header against the local file size to decide whether to skip.

- **`src/uclv_visuales_downloader/progress_bar.py`** — `DownloadProgressBar` is a callable passed as the
  `reporthook` to `urllib.request.urlretrieve`; it lazily builds a
  `progressbar.ProgressBar` on first call once `total_size` is known.

### Network access

`https://visuales.uclv.cu` is only accessible from within Cuba. Do not attempt
to test live scraping or verify URLs against the real server from outside Cuban
networks. Use the captured HTML in `src/examples_doc.py` for local testing instead.

### Important constraints

- The target URL **must point to a directory listing**, not a file. The output
  directory name is taken from `url.split('/')[-2]`, so the URL should end with a
  trailing slash.
- Scraping is tightly coupled to the exact structure of these Apache index pages
  (first `td` = icon, second `td` = link). Changes to the remote HTML layout
  would break `get_links`.
- The package is `src/uclv_visuales_downloader/`. Modules use relative imports
  (`from .link_finder import ...`). The program is invoked via the `visuales`
  entry point registered in `pyproject.toml`.
