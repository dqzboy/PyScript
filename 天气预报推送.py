import requests
import json
import datetime

# 获取当前日期
today = datetime.date.today().strftime("%Y-%m-%d")

# 输入城市名称（拼音）
city = input("请输入城市名称（拼音）:")

# 从API获取天气信息
response = requests.get(f"https://tianqiapi.com/free/day?appid=你的API密钥&appsecret=你的API密钥&city={city}&date={today}")

# 转换JSON格式
weather_info = json.loads(response.text)

# 提取需要的信息
date = weather_info["date"]
week = weather_info["week"]
wea = weather_info["wea"]
tem = weather_info["tem"]
win = weather_info["win"]
air = weather_info["air"]
humidity = weather_info["humidity"]

# 构建消息体
message = f"今天是{date} {week}，{city}天气为{wea}，温度为{tem}℃，风向是{win}，空气质量为{air}，湿度为{humidity}%。"

# 发送消息到企业微信机器人
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的Webhook Key"
data = {
    "msgtype": "text",
    "text": {
        "content": message
    }
}
response = requests.post(url=webhook_url, data=json.dumps(data))
print(response.text)
