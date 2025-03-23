#!/usr/bin/env python
import configparser
import requests
import json
import random
import time
import paho.mqtt.client as mqtt

# 1. 설정 파일 읽기
config = configparser.ConfigParser()
config.read("config.ini")

IOTPLATFORM_IP = config.get("IOT", "IOTPLATFORM_IP")
IOTPLATFORM_HTTP_PORT = config.get("IOT", "IOTPLATFORM_HTTP_PORT")
IOTPLATFORM_MQTT_PORT = config.get("IOT", "IOTPLATFORM_MQTT_PORT")

AE_NAME = config.get("oneM2M", "AE_NAME")
API_ID = config.get("oneM2M", "API_ID")
# 컨테이너 이름은 쉼표로 구분 (예: meta_human, meta_robot, meta_vehicle)
containers = [name.strip() for name in config.get("oneM2M", "containers").split(",")]

# URL 템플릿 구성
HTTP_URL = f"http://{IOTPLATFORM_IP}:{IOTPLATFORM_HTTP_PORT}"
IOTPLATFORM_URL_MQTT = "mqtt://{}/{}?ct=json"  # 템플릿: 첫번째 {}에는 IP, 두번째 {}에는 MQTT 토픽(구독 리소스 이름)

print("HTTP URL:", HTTP_URL)
# (참고: 예시 MQTT URL 출력)
if containers:
    example_topic = f"{AE_NAME}_{containers[0]}"
    print("예시 MQTT URL:", IOTPLATFORM_URL_MQTT.format(IOTPLATFORM_IP, example_topic))


# 서비스 기동 대기 (실제 환경에서는 healthcheck 등으로 대기)
def wait_for_services():
    print("서비스들이 준비될 때까지 대기중...")
    time.sleep(10)
    print("대기 완료.")


# AE 조회/생성 함수
def query_ae():
    url = f"{HTTP_URL}/Mobius/{AE_NAME}?rcn=1"
    headers = {
        "Accept": "application/json",
        "X-M2M-RI": "queryAE123",
        "X-M2M-Origin": "S",
    }
    print(f"AE [{AE_NAME}] 조회 중...")
    try:
        response = requests.get(url, headers=headers)
        print("AE 조회 응답:", response.text)
        return response.status_code == 200
    except Exception as e:
        print("AE 조회 실패:", e)
        return False


def create_ae():
    url = f"{HTTP_URL}/Mobius"
    payload = {
        "m2m:ae": {"rn": AE_NAME, "api": API_ID, "lbl": ["key1", "key2"], "rr": True}
    }
    headers = {
        "X-M2M-RI": "createAE123",
        "X-M2M-Origin": "S",
        "Content-Type": "application/json;ty=2",
    }
    print(f"AE [{AE_NAME}] 생성 요청 중...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print("AE 생성 응답:", response.text)
    except Exception as e:
        print("AE 생성 실패:", e)


# 컨테이너 조회/생성 함수
def query_container(container_name):
    url = f"{HTTP_URL}/Mobius/{AE_NAME}/{container_name}?rcn=1"
    headers = {
        "Accept": "application/json",
        "X-M2M-RI": f"queryCNT_{container_name}",
        "X-M2M-Origin": "S",
    }
    print(f"컨테이너 [{container_name}] 조회 중...")
    try:
        response = requests.get(url, headers=headers)
        print("컨테이너 조회 응답:", response.text)
        return response.status_code == 200
    except Exception as e:
        print(f"컨테이너 [{container_name}] 조회 실패:", e)
        return False


def create_container(container_name):
    url = f"{HTTP_URL}/Mobius/{AE_NAME}"
    payload = {"m2m:cnt": {"rn": container_name, "lbl": ["API"]}}
    headers = {
        "Accept": "application/json",
        "X-M2M-RI": f"createCNT_{container_name}",
        "X-M2M-Origin": "S",
        "Content-Type": "application/json; ty=3",
    }
    print(f"컨테이너 [{container_name}] 생성 요청 중...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print("컨테이너 생성 응답:", response.text)
    except Exception as e:
        print(f"컨테이너 [{container_name}] 생성 실패:", e)


# --- 여기부터는 사용자가 보내주신 작동 코드(구독 생성 부분)를 반영 ---
def crt_sub(URI, AE_ID, resourceName):
    rand = str(int(random.random() * 100000))
    crt_sub_payload = {
        "to": URI,
        "fr": AE_ID,
        "op": 1,
        "ty": 23,  # Subscription 타입
        "rqi": rand,  # 요청 ID (랜덤)
        "pc": {
            "m2m:sub": {
                "rn": resourceName,  # 구독 리소스 이름 (토픽 이름과 동일하게 구성)
                "enc": {"net": [3]},
                # nu: 알림 URI. 예: mqtt://localhost/ae_test_cnt_test2?ct=json
                "nu": [IOTPLATFORM_URL_MQTT.format(IOTPLATFORM_IP, resourceName)],
            }
        },
    }
    return crt_sub_payload


def publish_subscription(URI, AE_ID, resourceName):
    client = mqtt.Client()
    # MQTT 연결
    client.connect(IOTPLATFORM_IP, int(IOTPLATFORM_MQTT_PORT))
    # 구독 생성 요청 페이로드 작성
    payload = json.dumps(crt_sub(URI, AE_ID, resourceName))
    # MQTT 요청 토픽 (oneM2M 표준)
    topic = f"/oneM2M/req/{AE_ID}/Mobius2/json"
    client.publish(topic, payload)
    client.disconnect()
    print("Subscription creation request sent:")
    print("Topic:", topic)
    print("Payload:", payload)


# --- 여기까지가 사용자가 보내주신 구독 생성 코드 부분 ---


# 메인 플로우
if __name__ == "__main__":
    wait_for_services()

    # 1. AE 존재 여부 확인 → 없으면 생성
    if not query_ae():
        create_ae()
    else:
        print(f"AE [{AE_NAME}]가 이미 존재합니다.")

    # 2. 각 컨테이너에 대해 조회 → 없으면 생성 후 구독 생성 요청 발행
    for container in containers:
        if not query_container(container):
            create_container(container)
        else:
            print(f"컨테이너 [{container}]가 이미 존재합니다.")

        # 구독 요청 발행
        # URI는 /Mobius/{AE}/{컨테이너} 형태로 구성
        URI = f"/Mobius/{AE_NAME}/{container}"
        AE_ID = AE_NAME
        # 구독 리소스 이름은 AE와 컨테이너 이름을 조합 (예: ae_test_meta_human)
        resourceName = f"{AE_NAME}_{container}"
        publish_subscription(URI, AE_ID, resourceName)
