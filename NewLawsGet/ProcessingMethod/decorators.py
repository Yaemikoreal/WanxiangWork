import time
from .logger import logger


def timer(func):
    """
    A decorator that logs the execution time of a function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"函数 [{func.__name__}]  共计运行用时: [{elapsed_time:.6f}] 秒.")
        return result

    return wrapper


@timer
def example_function(n):
    """
    An example function that simulates some work.
    """
    time.sleep(n)
    print(f"Function executed after {n} seconds.")


# 示例用法
if __name__ == "__main__":
    example_function(2)
