import json

from db_utils.post_database import post_url
import random
import config



ICON_LIST = ["🍼", "☕", "🥛", "🥃", "🍺", "🍨", "🍩", "🍪", "🍧", "🍦", "🍭", "🎂", "🍰", "🍫", "🥧", "🧁", "🍬", "🍮",
             "🍯", "🍵", "🍸", "🍹", "🧊", "🧃", "🧉", "🍣", "🍇", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏", "🍐",
             "🍑", "🍒", "🍓", "🥝", "🍅", "🥥", "🍡", "🍤", "🍥", "🍛", "🍿", "🍕", "🍔", "🌈", "🦄", "🐶", "🦊", "🦓",
             "🐷", "🐄", "🐼", "🦚", "🐳", "🚀", "🌌", "🌀", "❄", "🌊", "🪐", "🎃", "🎄", "🎆", "🏆", "⚽", "⚾", "🥎",
             "🏀", "🏐", "🏈", "🏉", "🎾", "🥏", "🎳", "🏓", "🏸", "🥊", "🔮", "🎲"]

# 修改订阅状态
def change_sub_information(content, user_id, status):
    sub_content = content.split("-")[1]
    sql_query = f"SELECT subscription from organization_information_source where organization_name = '{config.organization_name}';"
    response = post_url(config.db_id, sql_query)

    subscriptions = response.json()["data"]["executed_result"]["query_result"]["rows"][0][0]

    for subscription in subscriptions:
        if subscription['subscription_content'] == sub_content and subscription['receive_id'] == user_id:
            subscription['status'] = status

    print(subscriptions)

    sql_query2 = f"UPDATE organization_information_source SET subscription = '{json.dumps(subscriptions, ensure_ascii=False)}' WHERE organization_name = '{config.organization_name}';"
    response = post_url(config.db_id, sql_query2)


    turn = "关闭" if status == 0 else "启动"
    if response:
        result = {
                "elements": [],
                "header": {"title": {
                    "content": f"{turn}订阅类型-{sub_content}成功",
                    "tag": "plain_text"
                }
            }
        }

    else:
        result = {
                "elements": [],
                "header": {"title": {
                    "content": "请求失败",
                    "tag": "plain_text"
                }
            }
        }
    return result




# 添加订阅内容
def sub_add(content, user_id):
    flattened_list = []

    subscription_content = content.split("-")[2]
    subscription_type = content.split("-")[1]

    sql_query1 = "SELECT subscription FROM organization_information_source"
    response = post_url(config.db_id, sql_query1)

    found = False

    if response:
        try:
            rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
            for i in rows:
                for items in i:
                    all_sources = items
                    for item in items:
                        if item.get("subscription_content", "") == subscription_content and item.get("subscription_type",
                                                                                                     "") == subscription_type:
                            found = True
        except Exception as e:
            all_sources = []



        if not found:
            all_sources.append({"receive_id": user_id, "subscription_content": subscription_content, "status": 1, "subscription_type": subscription_type})

            print(all_sources)
            sql_query2 = f"UPDATE organization_information_source SET subscription = '{json.dumps(all_sources,ensure_ascii=False)}' WHERE organization_name = '{config.organization_name}';"
            response = post_url(config.db_id, sql_query2)
            if response:
                result = {
                        "elements": [],
                        "header": {"title": {
                            "content": "添加成功",
                            "tag": "plain_text"
                        }
                    }
                }

        else:
            result = {
                    "elements": [],
                    "header": {"title": {
                        "content": "已存在该订阅内容",
                        "tag": "plain_text"
                    }
                }
            }
    return result


# 查看订阅内容
def sub_information(user_id):
    all_items = []

    icon = random.choice(ICON_LIST)
    title_icon = random.choice(ICON_LIST)
    introduction_icon = random.choice(ICON_LIST)
    href_icon = random.choice(ICON_LIST)


    sql_query = f"SELECT subscription from organization_information_source where organization_name = '{config.organization_name}';"
    response = post_url(config.db_id, sql_query)
    data = response.json()['data']
    try:
        for i in data['executed_result']['query_result']['rows']:
            for items in i:
                for item in items:
                    if item.get('receive_id', '') == user_id:
                        all_items.append(
                            [item.get('receive_id', ''), item.get('subscription_type', ''), item.get('status', ''),
                             item.get('subscription_content', '')])
    except Exception as e:
        all_items = []

    contents = []

    print("查看订阅内容",all_items)
    if all_items:
        if len(all_items) > 4 :
            mid_index = len(all_items) // 2
            segments = [all_items[:mid_index], all_items[mid_index:]]
        else:
            segments = [all_items]

        for segment in segments:
            content = {
                    "elements": [{"tag": "hr"}],
                    "header": {
                        "title": {
                            "content": f"{icon}订阅信息",
                            "tag": "plain_text"
                    }
                }
            }
            for new in segment:
                status = "关闭" if new[2] == 0 else "启动"

                title = {
                    "tag": "div",
                    "text": {"content": f"{title_icon}**{new[0]}**",
                             "tag": "lark_md"}
                }

                introduction = {"tag": "div",
                                "text": {"content": f"{introduction_icon}订阅类型:{new[1]}\n{href_icon}订阅内容:{new[3]}",
                                         "tag": "lark_md"}
                                }

                news_data2 = {
                    "actions": [{
                        "tag": "button",
                        "text": {
                            "content": f"状态 :{status}",
                            "tag": "lark_md"
                        },
                        "type": "default",
                        "value": {}
                    }],
                    "tag": "action",
                }
                content["elements"].append(title)
                content["elements"].append(introduction)
                content["elements"].append(news_data2)
                content["elements"].append({"tag": "hr"})

            contents.append(content)
    else:
        content = {
                "elements": [],
                "header": {"title": {
                    "content": "该用户暂未订阅任何内容",
                    "tag": "plain_text"
                }
            }
        }
        contents.append(content)
    return contents
