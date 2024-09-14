# decorators.py
import time
import logging

logging.basicConfig(level=logging.INFO)


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Function '{func.__name__}' took {elapsed_time:.6f} seconds to run.")
        return result

    return wrapper
