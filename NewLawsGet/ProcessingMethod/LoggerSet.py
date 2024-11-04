import atexit
import logging
import os
from datetime import datetime

# 日志文件名模板
LOG_FILE_TEMPLATE = "logs/{}-运行日志-{}.log"

# 记录运行次数的文件
RUN_COUNT_FILE = "logs/运行日志统计.txt"

ensure_logs_dir_exists_called = False


def ensure_logs_dir_exists():
    global ensure_logs_dir_exists_called
    if not ensure_logs_dir_exists_called:
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        ensure_logs_dir_exists_called = True


def get_log_filename():
    ensure_logs_dir_exists()
    today = datetime.now().strftime("%Y%m%d")
    count = get_run_count(today)
    return LOG_FILE_TEMPLATE.format(today, count)


def get_run_count(today):
    run_count_path = RUN_COUNT_FILE
    if not os.path.exists(run_count_path):
        with open(run_count_path, "w") as f:
            f.write("{}:1\n".format(today))
        return 1

    with open(run_count_path, "r+") as f:
        content = f.read()
        lines = content.split("\n")
        found_today = False
        for line in lines:
            if line.startswith(today):
                count = int(line[len(today) + 1:])
                f.seek(0)
                f.write("{}:{}\n".format(today, count + 1))
                f.truncate()
                found_today = True
                break

        if not found_today:
            with open(run_count_path, "a") as f:
                f.write("{}:1\n".format(today))
            return 1

    return count + 1


def update_run_count(today, count):
    run_count_path = RUN_COUNT_FILE
    with open(run_count_path, "r+") as f:
        content = f.read()
        lines = content.split("\n")
        new_content = ""
        for line in lines:
            if line.startswith(today):
                new_content += "{}:{}\n".format(today, count)
            else:
                new_content += line + "\n"
        f.seek(0)
        f.write(new_content)
        f.truncate()


def setup_logger():
    # 创建一个日志记录器
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # 确保只有一个处理器
    if not logger.hasHandlers():
        # 获取今天的日期和运行次数
        log_filename = get_log_filename()

        # 创建一个文件处理器
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)

        # 创建日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 将文件处理器添加到日志记录器
        logger.addHandler(file_handler)

        # 创建一个流处理器，输出到标准输出（命令行）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # 将控制台处理器添加到日志记录器
        logger.addHandler(console_handler)

    return logger


# 设置日志记录器
logger = setup_logger()


def on_exit():
    today = datetime.now().strftime("%Y%m%d")
    count = get_run_count(today)
    update_run_count(today, count)


# 注册退出钩子，确保在程序退出时更新运行次数
atexit.register(on_exit)
