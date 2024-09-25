# coding:utf-8
import random
import time
from datetime import datetime
import re


import hashlib
def md5_num(title, faburiqi):
    m = hashlib.md5()
    string = str(title) + str(faburiqi)
    m.update(string.encode('utf-8'))
    return m.hexdigest()

num=md5_num("李希在二十届中央纪委三次全会上的工作报告","2024.01.08")
print(num)


