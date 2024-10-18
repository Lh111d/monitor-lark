import json
import pytz
import datetime as dt
import requests
import config
import logging
from ai.ai_subscription import kongai
from db_utils.post_database import post_url
import ast
from ai import prompt
from lark_utils import push

log_file = "./logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_subscription():
    all_items = []
    sql_query = f"SELECT subscription from organization_information_source where organization_name = '{config.organization_name}';"
    response = post_url(config.db_id, sql_query)
    data = response.json()['data']
    try:
        for i in data['executed_result']['query_result']['rows']:
            for items in i:
                for item in items:
                    if item.get('status', '') == 1:
                        all_items.append(
                            [item.get('receive_id', ''), item.get('subscription_content', ''), item.get('status', ''),
                             item.get('subscription_type', '')])
    except Exception as e:
        all_items = []
    return all_items


# 推送新闻
def push_news():
    all_result = []

    organization_name = config.organization_name
    # 获取前一个小时的时间段
    gmt8 = pytz.timezone('Asia/Shanghai')
    now = dt.datetime.now(gmt8)
    start_time = now - dt.timedelta(hours=1)  # 过去1小时
    end_time = now
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

    print(start_time_str, end_time_str)
    source_names = get_source_name(organization_name)
    print(source_names)
    results = find_news(start_time_str, end_time_str)

    all_receive_id = get_subscription()

    for news_content in results:
        if news_content.get('source_name', '') in source_names:
            user_content = f"subscription information:\n{str(all_receive_id)}\nnews content:\ntitle:{news_content['title']}\nsummary:{news_content['summary']}\nkeywords:{news_content['keywords']}"
            select_users = kongai(prompt.filter_subscribers_prompt, user_content)
            try:
                select_users = ast.literal_eval(select_users)
            except Exception as e:
                select_users = []
            print(select_users)
            content = {
                "card": {
                    "elements": [],
                    "header": {}
                }
            }

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
                    "content": news_content.get('source_name', ''),
                    "tag": "plain_text"
                }
            }
            content["card"]["elements"].append(news_data0)
            content["card"]["elements"].append(news_data1)
            content["card"]["elements"].append(news_data2)
            print("开始推送")
            push_lark(content)

            if select_users:
                for user in select_users:
                    user_message = f"你的任务是{user[2]},我提供的信息information为\n{news_content['content']}"
                    # print(user_message)
                    result = kongai(prompt.ai_summary_prompt,user_message)
                    content = {
                            "elements": [],
                            "header": {}
                    }
                    news_data1 = {
                        "tag": "div",
                        "text": {
                            "content": result,
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

                    content["header"] = {
                        "title": {
                            "content": news_content.get('source_name', ''),
                            "tag": "plain_text"
                        }
                    }
                    content["elements"].append(news_data0)
                    content["elements"].append(news_data1)
                    content["elements"].append(news_data2)
                    print(user[0])
                    push.push_user_lark(content, user[0])

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
        # print(key, values)
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
                    i["cmetadata"]['content'] = i["content"]
                    result.append(i["cmetadata"])
            # print(">>>>>>>>>>>>>>>>>>>>>>result>", result)
            return result
        else:
            return []
    except Exception as e:
        print(f"Error request db: {e}")
        return []
