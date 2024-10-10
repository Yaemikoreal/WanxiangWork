import requests


def test_ip(proxy):
    try:
        response = requests.get('https://www.example.com', proxies=proxy, timeout=5)
        print("代理生效!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"{proxy} 代理已失效!")
        return False


if __name__ == '__main__':
    proxy = "http://183.159.204.186:10344"
    test_ip(proxy)
