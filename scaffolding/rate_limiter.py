import time

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            time.sleep(2**attempt)
    raise Exception(f"Failed after {max_retries} attempts:{e}")