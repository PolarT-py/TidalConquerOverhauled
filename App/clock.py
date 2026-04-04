class Timer:
    def __init__(self, duration: float, start=True, repeat=False):
        self.duration = duration
        self.time_left = duration if start else 0.0
        self.repeat = repeat
        self.finished = False if start else True

    def update(self, dt: float):
        if self.finished and not self.repeat:
            return False
        self.time_left -= dt

        if self.time_left <= 0:
            if self.repeat:
                self.time_left += self.duration
            else:
                self.time_left = 0
                self.finished = True
            return True
        return False

    def reset(self):
        self.time_left = self.duration
        self.finished = False

    def is_finished(self):
        return self.finished