import logging
import json
import time

import requests
import config

# 配置日志
log_file = "./logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# lark获取tenant_access_token
def get_tenant_access_token():
    app_id = config.app_id
    app_secret = config.app_secret
    url = 'https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal'
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    response = requests.post(url, headers=headers, json=data)

    print(f"response >> {response.text}")
    try:
        my_json = response.json()
        tenant_access_token = my_json["tenant_access_token"]
    except Exception as e:
        logging.error(e)
        tenant_access_token = None
    return tenant_access_token


# lark推送
def push_lark(content, receive_id):
    content = json.dumps(content, ensure_ascii=False)
    tenant_access_token = None
    max_retry = config.max_retry
    num = 0
    while not tenant_access_token and num < max_retry:
        tenant_access_token = get_tenant_access_token()
        num += 1
    receive_id_type = "chat_id"
    url = "https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type={}".format(receive_id_type)
    params = {
        "receive_id": receive_id,
        "content": content,
        "msg_type": "interactive"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant_access_token}',
    }
    # for key, values in content.items():
    #     params[key] = values
    # for url in urls:
    response = requests.post(url=url, headers=headers, json=params)
    logging.info(f"{response.status_code}:{response.json()}")
    return 0

def push_user_lark(content, receive_id):
    content = json.dumps(content, ensure_ascii=False)
    tenant_access_token = None
    max_retry = config.max_retry
    num = 0
    while not tenant_access_token and num < max_retry:
        tenant_access_token = get_tenant_access_token()
        num += 1
    receive_id_type = "user_id"
    url = "https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type={}".format(receive_id_type)
    params = {
        "receive_id": receive_id,
        "content": content,
        "msg_type": "interactive"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant_access_token}',
    }
    # for key, values in content.items():
    #     params[key] = values
    # for url in urls:
    response = requests.post(url=url, headers=headers, json=params)
    logging.info(f"{response.status_code}:{response.json()}")
    return 0

def test_lark(content):
    tenant_access_token = None
    max_retry = config.max_retry
    num = 0
    while not tenant_access_token and num < max_retry:
        tenant_access_token = get_tenant_access_token()
        num += 1

    text = content.split("###")
    receive_ids = text[1].split(",")
    logging.info(f"receive_ids,{receive_ids}")
    for receive_id in receive_ids:
        url = "https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type=open_id"
        payload = json.dumps({
            "content": json.dumps({"text": text[0]}),
            "msg_type": "text",
            "receive_id": receive_id
        })
        logging.info(f"payload,{payload}")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {tenant_access_token}"
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        time.sleep(2)
        logging.info(f"test_lark,{response}")
        print(response.text)
    return 0
    # url = 'https://open.larksuite.com/open-apis/bot/v2/hook/8cda7ae5-3ae6-48e5-b741-44f6b21c6e0f'
    # params = {
    #     "msg_type": "interactive",
    # }
    # headers = {
    #     'Content-Type': 'application/json',
    # }
    # for key, values in content.items():
    #     params[key] = values
    # response = requests.post(url, json=params, headers=headers)
    # logging.info(f"{response.status_code}:{response.json()}")
    # return 0
