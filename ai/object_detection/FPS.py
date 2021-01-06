import time


class FPS:
    def __init__(self):
        self._start = time.time()
        self._end = None

    def end(self):
        self._end = time.time()

    @property
    def label(self):
        if self._end is None:
            self.end()

        return "FPS: %.2f" % (1 / (self._end - self._start))
