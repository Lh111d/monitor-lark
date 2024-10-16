import json
import random
import config
from db_utils.post_database import post_url
import logging

ICON_LIST = ["🍼", "☕", "🥛", "🥃", "🍺", "🍨", "🍩", "🍪", "🍧", "🍦", "🍭", "🎂", "🍰", "🍫", "🥧", "🧁", "🍬", "🍮",
             "🍯", "🍵", "🍸", "🍹", "🧊", "🧃", "🧉", "🍣", "🍇", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏", "🍐",
             "🍑", "🍒", "🍓", "🥝", "🍅", "🥥", "🍡", "🍤", "🍥", "🍛", "🍿", "🍕", "🍔", "🌈", "🦄", "🐶", "🦊", "🦓",
             "🐷", "🐄", "🐼", "🦚", "🐳", "🚀", "🌌", "🌀", "❄", "🌊", "🪐", "🎃", "🎄", "🎆", "🏆", "⚽", "⚾", "🥎",
             "🏀", "🏐", "🏈", "🏉", "🎾", "🥏", "🎳", "🏓", "🏸", "🥊", "🔮", "🎲"]

# 配置日志
log_file = "./logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# 查找对应信息源
def find_all_source(content):
    all_items = []

    icon = random.choice(ICON_LIST)
    title_icon = random.choice(ICON_LIST)
    introduction_icon = random.choice(ICON_LIST)
    href_icon = random.choice(ICON_LIST)

    # 提取organization_name的订阅内容
    sql_query = f"SELECT sources from organization_information_source where organization_name = '{config.organization_name}'"
    response = post_url(config.db_id, sql_query)

    data = response.json()['data']

    if "关闭" in content:
        for i in data['executed_result']['query_result']['rows']:
            for items in i:
                for item in items:
                    if item.get('status', 2) == 0:
                        all_items.append(
                            [item.get('name', ''), item.get('url', ''), item.get('category', ''), item.get('status', '')])
    elif "启动" in content:
        for i in data['executed_result']['query_result']['rows']:
            for items in i:
                for item in items:
                    if item.get('status', 2) == 1:
                        all_items.append(
                            [item.get('name', ''), item.get('url', ''), item.get('category', ''),
                             item.get('status', '')])
    else:
        for i in data['executed_result']['query_result']['rows']:
            for items in i:
                for item in items:
                    all_items.append(
                        [item.get('name', ''), item.get('url', ''), item.get('category', ''),
                         item.get('status', '')])


    contents = []
    if response:
        mid_index = len(all_items) // 2
        segments = [all_items[:mid_index], all_items[mid_index:]]
        for segment in segments:
            content = {
                "elements": [{"tag": "hr"}],
                "header": {
                    "title": {
                        "content": f"{icon}信息源",
                        "tag": "plain_text"

                    }
                }
            }

            for new in segment:
                print(new[1])
                status = "关闭" if new[3] == 0 else "启动"

                title = {
                    "tag": "div",
                    "text": {"content": f"{title_icon}**{new[0]}**",
                             "tag": "lark_md"}
                }

                introduction = {"tag": "div",
                                "text": {"content": f"{introduction_icon}简介:{new[2]}\n{href_icon}链接:{new[1]}",
                                         "tag": "lark_md"}
                                }

                news_data2 = {
                    "actions": [{
                        "tag": "button",
                        "text": {
                            "content": f"状态 :{status}",
                            "tag": "lark_md"
                        },
                        "url": new[1],
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
                "content": "请求失败",
                "tag": "plain_text"
            }
            }
        }
        contents.append(content)
    return contents


# 添加信息源
def add_source(content):
    flattened_list = []


    print("add_source>>>>>")
    x = content.split('-')
    name, url, category, status = x[1], x[2], x[3], x[4]
    print(">>>>>>>>>>>>>>>>>>>", name, url, category, status)
    sql_query1 = "SELECT sources FROM organization_information_source"
    response = post_url(config.db_id, sql_query1)
    if response:
        rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        for i in rows:
            for items in i:
                all_sources = items
                for item in items:
                    flattened_list.append(item.get('name', ''))
        found = name in flattened_list
        if not found:
            all_sources.append({"name":name,"url":url,"category":category,"status":1})

            sql_query2 = f"UPDATE organization_information_source SET sources = {all_sources} WHERE organization_name = '{config.organization_name}';"
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
                    "content": "添加失败，数据库存在该信息源",
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


# 更改信息源状态
def change_source(status, content):
    name = content.split("-")[1]
    sql_query = f"SELECT sources from organization_information_source where organization_name = '{config.organization_name}';"
    response = post_url(config.db_id, sql_query)
    turn = "关闭" if status == 0 else "启动"
    sources = response.json()["data"]["executed_result"]["query_result"]["rows"][0][0]

    for source in sources:
        if source['name'] == name:
            source['status'] = status

    print(sources)

    sql_query2 = f"UPDATE organization_information_source SET sources = '{json.dumps(sources,ensure_ascii=False)}' WHERE organization_name = '{config.organization_name}';"
    response = post_url(config.db_id, sql_query2)
    print(response)
    if response:
        result = {
            "elements": [],
            "header": {"title": {
                "content": f"{turn}信息源-{name}成功",
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


# 搜索信息源
def search_source(user_content):
    icon = random.choice(ICON_LIST)
    title_icon = random.choice(ICON_LIST)
    introduction_icon = random.choice(ICON_LIST)
    href_icon = random.choice(ICON_LIST)
    content = {
        "elements": [],
        "header": {
            "title": {
                "content": "信息源",
                "tag": "plain_text"
            }
        }
    }
    search_name = user_content.split("-")[1]
    print(search_name)
    logging.info(search_name)

    sql_query = f"SELECT sources from organization_information_source where organization_name = '{config.organization_name}';"
    response = post_url(config.db_id, sql_query)


    if "," in search_name:
        search_name = search_name.split(",")

    else:
        search_name = [search_name]

    sources = response.json()["data"]["executed_result"]["query_result"]["rows"][0][0]
    matching_sources = [source for source in sources if all(term in source['category'] for term in search_name)]



    logging.info(response)
    if response:
        try:
            rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        except Exception as e:
            rows = []
        logging.info(rows)
        result = {
            "elements": [{"tag": "hr"}],
            "header": {
                "title": {
                    "content": f"{icon}信息源",
                    "tag": "plain_text"
                }
            }
        }
        if matching_sources:
            for new in matching_sources:
                status = "关闭" if new['status'] == 0 else "启动"

                title = {
                    "tag": "div",
                    "text": {"content": f"{title_icon}**{new['name']}**",
                             "tag": "lark_md"}
                }

                introduction = {"tag": "div",
                                "text": {"content": f"{introduction_icon}简介:{new['category']}\n{href_icon}链接:{new['url']}",
                                         "tag": "lark_md"}
                                }

                news_data2 = {
                    "actions": [{
                        "tag": "button",
                        "text": {
                            "content": f"状态 :{status}",
                            "tag": "lark_md"
                        },
                        "url": new['url'],
                        "type": "default",
                        "value": {}
                    }],
                    "tag": "action",
                }
                result["elements"].append(title)
                result["elements"].append(introduction)
                result["elements"].append(news_data2)
                result["elements"].append({"tag": "hr"})
        else:
            result = {
                "elements": [],
                "header": {"title": {
                    "content": "没有该种类信息源",
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
