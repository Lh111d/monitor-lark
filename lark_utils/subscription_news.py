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
    sql_query = f"UPDATE subscription_information SET status={status} where receive_id='{user_id}' and subscription_content = '{sub_content}';"
    response = post_url(config.db_id, sql_query)
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
    subscription_content = content.split("-")[2]
    subscription_type = content.split("-")[1]
    sql_query = f"INSERT INTO subscription_information (receive_id,subscription_content,status,subscription_type) VALUES ('{user_id}', '{subscription_type}', 1,'{subscription_content}');"
    response = post_url(config.db_id, sql_query)
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
                    "content": "添加失败",
                    "tag": "plain_text"
                }
            }
        }
    return result


# 查看订阅内容
def sub_information(user_id):
    icon = random.choice(ICON_LIST)
    title_icon = random.choice(ICON_LIST)
    introduction_icon = random.choice(ICON_LIST)
    href_icon = random.choice(ICON_LIST)
    sql_query = f"SELECT * FROM subscription_information WHERE receive_id = '{user_id}';"
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
                    "content": "请求失败",
                    "tag": "plain_text"
                }
            }
        }
        contents.append(content)
    return contents
