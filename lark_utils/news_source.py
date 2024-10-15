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
    icon = random.choice(ICON_LIST)
    title_icon = random.choice(ICON_LIST)
    introduction_icon = random.choice(ICON_LIST)
    href_icon = random.choice(ICON_LIST)
    if "关闭" in content:
        sql_query = "SELECT * FROM information_source WHERE status = 0;"
    elif "启动" in content:
        sql_query = "SELECT * FROM information_source WHERE status = 1;"
    else:
        sql_query = "SELECT * FROM information_source;"

    response = post_url(config.db_id, sql_query)
    contents = []
    if response:
        rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        mid_index = len(rows) // 2
        segments = [rows[:mid_index], rows[mid_index:]]
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
    print("add_source>>>>>")
    x = content.split('-')
    name, url, category, status = x[1], x[2], x[3], x[4]
    print(">>>>>>>>>>>>>>>>>>>", name, url, category, status)
    sql_query1 = "SELECT name FROM information_source"
    response = post_url(config.db_id, sql_query1)
    if response:
        rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        flattened_list = [item for sublist in rows for item in sublist]
        found = name in flattened_list
        if not found:
            sql_query2 = f"INSERT INTO information_source (name,url,category,status) VALUES ('{name}', '{url}', '{category}', '{status}');"
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
    sql_query = f"UPDATE information_source SET status={status} where name='{name}';"
    response = post_url(config.db_id, sql_query)
    turn = "关闭" if status == 0 else "启动"
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
    if "," in search_name:
        search_name = search_name.split(",")
        all_name = '%'.join(search_name)
        sql_query = f"SELECT * FROM information_source WHERE category LIKE '%{all_name}%';"
    elif "=" in search_name:
        query = search_name.split("=")
        sql_query = f"SELECT * FROM information_source WHERE {query[0]}='{query[1]}';"

    else:
        sql_query = f"SELECT * FROM information_source WHERE category LIKE '%{search_name}%';"

    response = post_url(config.db_id, sql_query)

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
        if rows:
            for new in rows:
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
