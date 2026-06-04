import progressbar


class DownloadProgressBar:
    def __init__(self, total_size: int, initial: int = 0):
        self._downloaded = initial
        widgets = [
            progressbar.Percentage(),
            ' ', progressbar.Bar(),
            ' ', progressbar.ETA(),
            ' ', progressbar.FileTransferSpeed(),
        ]
        if total_size > 0:
            self._bar = progressbar.ProgressBar(maxval=total_size, widgets=widgets, term_width=100)
            self._bar.start()
            if initial > 0:
                self._bar.update(initial)
        else:
            self._bar = progressbar.ProgressBar(
                widgets=[progressbar.AnimatedMarker(), ' ', progressbar.FileTransferSpeed()],
                maxval=progressbar.UnknownLength,
                term_width=100,
            )
            self._bar.start()

    def update(self, n_bytes: int):
        self._downloaded += n_bytes
        try:
            self._bar.update(self._downloaded)
        except ValueError:
            pass  # last chunk may overshoot maxval by up to CHUNK_SIZE-1 bytes

    def finish(self):
        self._bar.finish()
