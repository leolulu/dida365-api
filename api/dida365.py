import requests
import json

url = "https://api.dida365.com/api/v2/user/signon?wc=true&remember=true"

payload = json.dumps({
  "password": "226818Aa",
  "username": "348699103@qq.com"
})
headers = {
  'content-type': 'application/json',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
  'x-device': '{"platform":"web","os":"Windows 10","device":"Chrome 109.0.0.0","name":"","version":4411,"id":"63b0fb54363a786fba71cc80","channel":"website","campaign":"","websocket":""}',
}
session=requests.session()
response = session.request("POST", url, headers=headers, data=payload)

print(response.text)


r = session.get("https://api.dida365.com/api/v2/project/all/completed",headers=headers)

print(json.loads(r.content))