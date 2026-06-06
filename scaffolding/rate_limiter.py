import time

class RateLimiter:
    def __init__(self, max_calls=100 ):
        self.calls_made = 0
        self.window_start = time.time()
        self.max_calls = max_calls
    def wait_if_needed(self):
        if time.time() - self.window_start > 60:
            self.calls_made = 0
            self.window_start = time.time()
        else:
            if self.calls_made > self.max_calls:
                time.sleep(60 - (time.time() - self.window_start))

        self.calls_made+=1






