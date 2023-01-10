# uclv-visuales-downloader
An automatic downloader for `https://visuales.uclv.cu` directories

## Installation Guide
This project is developed with Python3, so make sure you have it (tested with Python3.9.6). To install the downloader open a terminal in the folder you would like to place the repo and follow these steps:

1. Clone the repo and move to it: 
    ``` bash
    git clone https://github.com/AlejandroLabourdette/uclv-visuales-downloader
    ```
    ``` bash
    cd uclv-visuales-downloader 
    ```
2. Create a python virtual environment and activate it:
    ``` bash
    python3 -m venv venv
    ```
    ``` bash
    source venv/bin/activate
    ```
3. Install required dependencies:
    ``` bash
    pip install -r requirements.txt
    ```
4. To check if the program is working as expected execute:
    ``` bash
    python3 src/main.py --version
    ```
    It should output something like:
     ```
    > main.py, version 0.1.0
    ```

Now you are ready to go.

## Use Guide
Open a terminal inside the project folder that use the virtual environment:
``` bash
source venv/bin/activate
```
Then execute:
``` bash
python3 src/main.py <url>
```
Feel free to substitute `<url>` with the URL to the directory to be downloaded.
> Note: The URL must point to a directory (not video, img, ... ).

This command will start the download of the directory inside a folder with the same name. This folder will be placed under the project's root.

You can download more than one directory at once:
``` bash
python3 src/main.py <url1> <url2> ... <urlN>
```
Make sure to separate urls with a white space.

>Tip: In case you forgot to add an url to the download, you can always have more than one terminal working ;) .

## Documentation
``` bash
python3 src/main.py --help
```
The command will output all avaible commands and options:
```
Usage: main.py [OPTIONS] [URLS]...

  Download full directory from specified URL's

Options:
  --version     Show the version and exit.
  --onlyvideos  download only videos
  --help        Show this message and exit.
```