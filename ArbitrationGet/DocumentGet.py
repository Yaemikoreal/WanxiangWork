import requests
from tqdm import tqdm
import os
from query import PublicFunction as pf

"""
该方法适用于获取绵阳仲裁委官网中的“文书下载”区域的文件内容
"""


class DocumentGet:
    def __init__(self):
        self.any_url = "http://www.myac.org.cn"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }

    def get_urls(self, soup):
        data_dt = {}
        try:
            soup = soup.find('div', id="channelContentBox")
            item_tags = soup.find_all('a', href=True, title=True)
            for tag in item_tags:
                title = tag['title']
                url = tag['href']
                data_dt[title] = url
            return data_dt
        except Exception as e:
            print(e)

    def get_post(self):
        data_lt = []
        # 获取到下载路径
        for it in range(3):
            get_url = f"http://www.myac.org.cn/index.asp?ChannelID=298&contentID=0&page={it + 1}"
            soup = pf.fetch_url(get_url, self.headers)
            data_dt = self.get_urls(soup)
            data_lt.append(data_dt)
        return data_lt

    def get_file(self, data_lt):
        download_dir = r"E:\JXdata\Python\wan\ArbitrationGet\文书下载"

        # 确保目录存在
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
                print(f"目录 {download_dir} 创建成功")
            except OSError as e:
                print(f"创建目录失败: {e}")
                return

        for it in data_lt:
            for key, value in it.items():
                new_url = self.any_url + value
                req = requests.get(new_url, self.headers)
                file_url = req.url
                file_req = requests.get(file_url, self.headers)
                try:
                    if file_req.status_code == 200:
                        # 获取文件总大小
                        total_size = int(file_req.headers.get('content-length', 0))
                        # 每次读取的块大小为1KB
                        block_size = 1024
                        # 初始化进度条
                        t = tqdm(total=total_size, unit='iB', unit_scale=True)
                        # 构建文件路径
                        file_path = os.path.join(download_dir, key + '.doc')
                        with open(file_path, "wb") as f:
                            for data in req.iter_content(block_size):
                                t.update(len(data))  # 更新进度条
                                f.write(data)
                        t.close()

                        if total_size != 0 and t.n != total_size:
                            print("ERROR, something went wrong")
                        print(f"该附件下载完毕 [{key}]")
                except Exception as e:
                    print(e)

    def calculate(self):
        data_lt = self.get_post()
        self.get_file(data_lt)


def main():
    obj = DocumentGet()
    obj.calculate()


if __name__ == '__main__':
    main()
