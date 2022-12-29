import progressbar

class DownloadProgressBar():
    def __init__(self):
        self.p_bar: progressbar.ProgressBar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.p_bar:
            self.p_bar=progressbar.ProgressBar(maxval=total_size)
            self.p_bar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.p_bar.update(downloaded)
        else:
            self.p_bar.finish()
    