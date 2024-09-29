from GetTitleUrl import calculate as get_title_url
from NewInterface import main as interface_main
from ObtainingNewRegulations import main_test as get_new_data
from query.decorators import timer
import logging

# 配置日志输出到控制台
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@timer
def main():
    # 获取chl法律法规新内容的标题和url,为True时处理法律法规新内容，为False时处理地方法规内容
    logging.info("[chl] 正在获取法律法规新内容的标题和url!!!")
    get_title_url(choose=True)
    # 获取chl法律法规到数据库
    logging.info("[chl] 正在获取法律法规新内容到数据库!!!")
    get_new_data(choose_t=True, types_regulations_t=True)
    # 获取lar法律法规新内容的标题和url
    logging.info("[lar] 正在获取法律法规新内容的标题和url!!!")
    get_title_url(choose=False)
    # 获取lar法律法规到数据库
    logging.info("[lar] 正在获取法律法规新内容到数据库!!!")
    get_new_data(choose_t=True, types_regulations_t=False)
    logging.info("完毕!!!")


if __name__ == '__main__':
    main()
