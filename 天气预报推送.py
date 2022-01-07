import requests
import re
import urllib.request
import json
import sys
import os
import time
import time,datetime
holiday_info = {}
CUR_YEAR = '2022'  #定义年份
##这里字符集改为了gbk
headers = {'Content-Type': 'application/json;charset=gbk'}
webhook = "企业微信机器人webhook"
url = "https://tianqi.moji.com/weather/china/shanghai/minhang-district" 
par = '(<meta name="description" content=")(.*?)(">)'
opener = urllib.request.build_opener()
urllib.request.install_opener(opener)
html = urllib.request.urlopen(url).read().decode("utf-8")
data = re.search(par,html).group(2)
def msg(text):
    message= {
     "msgtype": "text",
        "text": {
            "content": text,
            "mentioned_list":["@all"]
        }
    }
    print(requests.post(webhook,json.dumps(message),headers=headers).content)
def init_holiday_info():
    global holiday_info
    rep = requests.get('http://tool.bitefu.net/jiari/?d=' + CUR_YEAR)
    info_txt = rep.content.decode()
    holiday_info =  json.loads(info_txt)

def check_if_is_work_day():
    day_info = time.strftime("%m%d",time.localtime(time.time()))
    print(day_info)
    if day_info in holiday_info[CUR_YEAR]:
        return False
    week = datetime.datetime.now().weekday()
    if 0 <= week and 4 >= week:
        msg(data)   #调用期企业微信推送内容
    return False

if __name__ == "__main__":
     init_holiday_info()
     check_if_is_work_day()
