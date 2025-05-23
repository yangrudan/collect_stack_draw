import requests
import json
import time

url = "http://127.0.0.1:9922/apis/pythonext/callstack"


headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("请求成功！")
        print("响应内容：")
        print(response.json())  
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print("响应内容：")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"请求过程中发生错误：{e}")
