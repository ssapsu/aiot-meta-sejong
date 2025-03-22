import requests
import json
import random

# conf.js 환경에 따른 기본 설정
CSE_HOST = "localhost"
CSE_PORT = "7579"
CSE_NAME = "Mobius"
AE_ID = "ae_test"
RESOURCE = "cnt_test2"

# oneM2M URI 구성: /{CSE}/{AE}/{CNT}
uri = f"/{CSE_NAME}/{AE_ID}/{RESOURCE}"
url = f"http://{CSE_HOST}:{CSE_PORT}{uri}"

# HTTP 헤더 수정: Content-Type에 ty=4 추가 (CIN 생성)
headers = {
    "Content-Type": "application/vnd.onem2m-res+json;ty=4",
    "Accept": "application/json",
    "X-M2M-Origin": AE_ID,
    "X-M2M-RI": str(random.randint(10000, 99999)),
}

# 전송할 데이터: oneM2M 표준에 따른 CIN 생성 payload
payload = {"m2m:cin": {"con": "Hello, this is a test message from Python HTTP POST"}}

print("POST URL:", url)
print("Payload:", json.dumps(payload))

response = requests.post(url, headers=headers, data=json.dumps(payload))
print("Status Code:", response.status_code)
print("Response Body:", response.text)
