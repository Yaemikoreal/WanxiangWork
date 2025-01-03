import requests
import time


def tongzhi(message):
    requests.get(
        'http://lawdoo.com:8048/api/inform?name=（替换为自己的名字）&key=asacwda5454wdadadadadw&message=' + message)  #名字改成自己的
    # requests.get(
    #     'http://lawdoo.com:8048/api/inform?name=黄晓兰&key=asacwda5454wdadadadadw&message=' + message)
    print('通知成功')


#生态专版
k = 0  #计算法规条数
nowtime = time.strftime("%Y-%m-%d", time.localtime())
if k == 10:
    message = '（替换为自己的名字）：监控了生态环境专版系统对应路径；监控时间：' + str(nowtime) + '；无更新'  #名字与单位改成自己对应的
else:
    message = '（替换为自己的名字）：监控了生态环境专版系统对应路径；监控时间：' + str(nowtime) + '；更新了' + str(
        k) + '条数据，已上传到ourdata，待打包更新'
tongzhi(message)
print(message)

#卫健专版
k = 0  #计算法规条数
nowtime = time.strftime("%Y-%m-%d", time.localtime())
if k == 0:
    message = '（替换为自己的名字）：监控了卫生健康专版系统对应路径；监控时间：' + str(nowtime) + '；无更新'  #名字与单位改成自己对应的
else:
    message = '（替换为自己的名字）：监控了卫生健康专版系统对应路径；监控时间：' + str(nowtime) + '；更新了' + str(
        k) + '条数据，已上传到ourdata，待打包更新'
tongzhi(message)
print(message)

#知产专版
k = 3  #计算法规条数
nowtime = time.strftime("%Y-%m-%d", time.localtime())
if k == 0:
    message = '（替换为自己的名字）：监控了生态环境专版系统对应路径；监控时间：' + str(nowtime) + '；无更新'  #名字与单位改成自己对应的
else:
    message = '（替换为自己的名字）：监控了生态环境专版系统对应路径；监控时间：' + str(nowtime) + '；更新了' + str(
        k) + '条数据，已上传到ourdata，待打包更新'
tongzhi(message)
print(message)
