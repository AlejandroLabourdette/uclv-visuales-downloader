# uclv-visuales-downloader

An automatic downloader for `https://visuales.uclv.cu` directories

## Installation Guide

This project requires [uv](https://docs.astral.sh/uv/getting-started/installation/). To install the downloader open a terminal in the folder you would like to place the repo and follow these steps:

1. Clone the repo and move to it:

    ``` bash
    git clone https://github.com/AlejandroLabourdette/uclv-visuales-downloader
    ```

    ``` bash
    cd uclv-visuales-downloader 
    ```

2. Install dependencies:

    ``` bash
    uv sync
    ```

3. To check if the program is working as expected execute:

    ``` bash
    uv run visuales --version
    ```

    It should output something like:

    ``` bash
    > visuales, version 0.1.0
    ```

Now you are ready to go.

## Use Guide

Execute commands with `uv run`:

``` bash
uv run visuales '<url>'
```

Feel free to substitute `<url>` with the URL to the directory to be downloaded.

> Note: The URL must point to a directory (not video, img, ... ).
>
> Note: Some shells can get confused with urls used as options without enclose them in quotes. That's why its advised to use `''`.

This command will start the download of the directory inside a folder with the same name. This folder will be placed under `downloads/` in project's root.

You can download more than one directory at once:

``` bash
uv run visuales '<url1>' '<url2>' ... '<urlN>'
```

Make sure to separate urls with a white space.

>Tip: In case you forgot to add an url to the download, you can always have more than one terminal working ;) .

## Documentation

``` bash
uv run visuales --help
```

The command will output all available commands and options:

``` bash
Usage: visuales [OPTIONS] [URLS]...

  Download full directory from specified URL's

Options:
  --version     Show the version and exit.
  --onlyvideos  download only videos
  --help        Show this message and exit.
```
