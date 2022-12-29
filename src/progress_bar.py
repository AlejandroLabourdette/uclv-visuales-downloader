import progressbar

class DownloadProgressBar():
    def __init__(self, file_name: str):
        self.p_bar: progressbar.ProgressBar = None
        self.file_name = file_name

    def __call__(self, block_num, block_size, total_size):
        if not self.p_bar:
            widgets = [
                self.file_name, ': ', progressbar.Percentage(),
                ' ', progressbar.Bar(),
                ' ', progressbar.ETA(),
                ' ', progressbar.FileTransferSpeed(),
            ]
            self.p_bar=progressbar.ProgressBar(maxval=total_size,widgets=widgets,term_width=100)
            self.p_bar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.p_bar.update(downloaded)
        else:
            self.p_bar.finish()
    