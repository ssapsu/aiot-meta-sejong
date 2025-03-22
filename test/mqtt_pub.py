import paho.mqtt.client as mqtt
import json
import random
import configparser
# 직접 변수에 설정 값을 할당 (ini 파일 미사용)
IOTPLATFORM_IP = "localhost"
IOTPLATFORM_HTTP_PORT = "7579"
IOTPLATFORM_MQTT_PORT = "1883"
IOTPLATFORM_URL_HTTP = (
    "http://{}:{}"  # 템플릿: 첫번째 {}에는 IP, 두번째 {}에는 HTTP 포트가 들어갑니다.
)
IOTPLATFORM_URL_MQTT = "mqtt://{}/{}?ct=json"  # 템플릿: 첫번째 {}에는 IP, 두번째 {}에는 MQTT 토픽이 들어갑니다.

# 예시 사용:
http_url = IOTPLATFORM_URL_HTTP.format(IOTPLATFORM_IP, IOTPLATFORM_HTTP_PORT)
mqtt_url = IOTPLATFORM_URL_MQTT.format(IOTPLATFORM_IP, "ae_test_cnt_test2")

print("HTTP URL:", http_url)
print("MQTT URL:", mqtt_url)


# sub(subscription) 생성 함수
def crt_sub(URI, AE_ID, resourceName):
    rand = str(int(random.random() * 100000))
    crt_sub = {
        "to": URI,
        "fr": AE_ID,
        "op": 1,
        "ty": 23,  # Subscription 타입
        "rqi": rand,  # 요청 ID (랜덤)
        "pc": {
            "m2m:sub": {
                "rn": resourceName,  # 구독 리소스 이름 (SUB명, 여기서 topic과 동일하게 설정)
                "enc": {
                    "net": [3]
                },  # net: 알림 전달 네트워크 조건 (예: 3은 CREATE 이벤트)
                # nu: 알림 URI. 예를 들어, resourceName이 topic이라면
                # "mqtt://{IOTPLATFORM_IP}/{topic}?ct=json" 형태로 설정합니다.
                "nu": [IOTPLATFORM_URL_MQTT.format(IOTPLATFORM_IP, resourceName)],
            }
        },
    }
    return crt_sub


# 구독 리소스 생성 MQTT 발행 함수
def publish_subscription(URI, AE_ID, resourceName):
    client = mqtt.Client()

    # MQTT 연결
    client.connect(IOTPLATFORM_IP, int(IOTPLATFORM_MQTT_PORT))

    # 구독 생성 요청 페이로드 작성
    payload = json.dumps(crt_sub(URI, AE_ID, resourceName))

    # MQTT 요청 토픽 구성 (oneM2M 표준)
    topic = "/oneM2M/req/" + AE_ID + "/Mobius2/json"

    # MQTT로 요청 발행
    client.publish(topic, payload)
    client.disconnect()

    print("Subscription creation request sent:")
    print("Topic:", topic)
    print("Payload:", payload)


if __name__ == "__main__":
    # 예시: URI는 /Mobius/{AE}/{CNT} 형태
    URI = (
        "/Mobius/ae_test/cnt_test2"  # AE가 'ae_test'이고, 컨테이너가 'cnt_test1'인 경우
    )
    AE_ID = "ae_test"
    resourceName = "ae_test_cnt_test2"  # 구독 리소스 이름, 보통 nu 값에 사용되는 토픽 이름과 동일하게 구성
    publish_subscription(URI, AE_ID, resourceName)
