import os
import sys
import time

from GetTitleUrl import calculate as get_title_url
from ObtainingNewRegulations import main_test as get_new_data
from ProcessingMethod.decorators import timer
import logging
from ProcessingMethod.LoggerSet import logger
# 动态修改sys.path以包含包的根目录
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)


@timer
def main():
    # 获取chl法律法规新内容的标题和url,为True时处理法律法规新内容，为False时处理地方法规内容
    logger.info("[chl] 正在获取法律法规新内容的标题和url!!!")
    status_chl = get_title_url(choose=True)
    if status_chl:
        time.sleep(5)
        # 获取chl法律法规到数据库
        logger.info("[chl] 正在获取法律法规新内容到数据库!!!")
        get_new_data(choose_t=True, types_regulations_t=True)
    else:
        logger.error("[chl]法律法规新内容为空!!!")

    # 获取lar法律法规新内容的标题和url
    logger.info("[lar] 正在获取法律法规新内容的标题和url!!!")
    status_lar = get_title_url(choose=False)

    if status_lar:
        time.sleep(5)
        # 获取lar法律法规到数据库
        logger.info("[lar] 正在获取法律法规新内容到数据库!!!")
        get_new_data(choose_t=True, types_regulations_t=False)
    else:
        logger.error("[lar]法律法规新内容为空!!!")

    logger.info("脚本运行完毕!!!")


if __name__ == '__main__':
    main()
