import json
import pytz
import datetime as dt
import requests
import config
import logging

log_file = "./logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# 推送新闻
def push_news():
    content = {
        "card": {
            "elements": [],
            "header": {}
        }
    }

    all_result = []

    organization_name = config.organization_name
    # 获取前一个小时的时间段
    gmt8 = pytz.timezone('Asia/Shanghai')
    date = dt.datetime.now(gmt8)
    now = dt.datetime.now(gmt8)
    start_time = now - dt.timedelta(hours=1)  # 过去1小时
    end_time = now
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

    source_names = get_source_name(organization_name)

    results = find_news(start_time_str, end_time_str)
    for news_content in results:
        if news_content.get('source_name','') in source_names:
            news_data1 = {
                "tag": "div",
                "text": {
                    "content": news_content['summary'],
                    "tag": "lark_md"
                }
            }

            news_data0 = {
                "tag": "div",
                "text": {
                    "content": f"**{news_content['title']}**",
                    "tag": "lark_md"
                }
            }

            news_data2 = {
                "actions": [{
                    "tag": "button",
                    "text": {
                        "content": f"更新时间 :{news_content['updated_at']}",
                        "tag": "lark_md"
                    },
                    "url": news_content['source'],
                    "type": "default",
                    "value": {}
                }],
                "tag": "action"
            }

            content["card"]["header"] = {
                "title": {
                    "content": news_content.get('source_name',''),
                    "tag": "plain_text"
                }
            }
            content["card"]["elements"].append(news_data0)
            content["card"]["elements"].append(news_data1)
            content["card"]["elements"].append(news_data2)
            push_lark(content)

    return all_result

# 推送lark
def push_lark(content):
    url = config.webhook_url
    params = {
        "msg_type": "interactive",
    }
    headers = {
        'Content-Type': 'application/json',
    }
    for key, values in content.items():
        # print("/////////////////////////////////////////////////////////")
        print(key, values)
        params[key] = values
    # print(params)
    try:
        response = requests.post(url, json=params, headers=headers, timeout=10)
        logging.info(f"push_news, {response.status_code}, {response.json()}")
    except Exception as e:
        logging.info(e)
    return 0

# 获取组织对应的订阅新闻网站
def get_source_name(organization_name):
    source_name = []
    url_db = 'https://data.dev.agione.ai/api/v1/data/operate'
    headers = {
        'api-key': config.db_api_key,
        'Content-Type': 'application/json'
    }
    data = {
        "db_id": config.db_id,
        "sql_query": f"SELECT sources from organization_information_source where organization_name = '{organization_name}'"
    }

    # 将数据转换为 JSON 格式
    json_data = json.dumps(data)

    # 发送 POST 请求
    response = requests.post(url_db, headers=headers, data=json_data)
    data = response.json()['data']
    # 打印响应结果
    for i in data['executed_result']['query_result']['rows']:
        for item in i[0]:
            if item['status'] == 1:
                source_name.append(item['name'])
    return source_name

# 根据时间查找数据库
def find_news(start_time, end_time):
    result = []
    try:
        BASE_URL = "https://data.dev.agione.ai/api/v1/data/general"

        headers = {
            'api-key': 'mc-n_KDyqNaDLJs6NOeoO-Y42rjtN_sJbV1kn7OqdBvIu0fMNxqrp1_P4f05Ns1a1EJ',
            'Content-Type': 'application/json'
        }
        params = {
            "model": "text-embedding-3-small",
            # 可选, 默认是text-embedding-3-small 目前只适配 text-embedding-3-small, text-embedding-ada-002, text-embedding-3-large
            "dimension": 1536,  # 可选, 默认1536
            "type": "Knowledge Collect - ALL_News",
            "metadata": json.dumps({"page": 0}),
            "start_time": start_time,
            "end_time": end_time,
            "skip": 0,  # 可选, 默认0
            "limit": 1000  # 可选, 默认10
        }
        # print(params)
        response = requests.get(BASE_URL, params=params, headers=headers)
        # print(f"Search Vectors Response: {response.status_code}, {response.json()}")
        if response.status_code == 200:
            for i in response.json():
                if i["cmetadata"].get("source_name", ""):
                    result.append(i["cmetadata"])
            print(">>>>>>>>>>>>>>>>>>>>>>result>", result)
            return result
        else:
            return []
    except Exception as e:
        print(f"Error request db: {e}")
        return []