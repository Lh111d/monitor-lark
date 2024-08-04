import logging
import json
import random
from flask import Flask, request, jsonify
import requests
from gevent import pywsgi
app = Flask(__name__)

# 配置日志
log_file = "./log/logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


ICON_LIST = ["🍼", "☕", "🥛", "🥃", "🍺", "🍨", "🍩", "🍪", "🍧", "🍦", "🍭", "🎂", "🍰", "🍫", "🥧", "🧁", "🍬", "🍮",
             "🍯", "🍵", "🍸", "🍹", "🧊", "🧃", "🧉", "🍣", "🍇", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏", "🍐",
             "🍑", "🍒", "🍓", "🥝", "🍅", "🥥", "🍡", "🍤", "🍥", "🍛", "🍿", "🍕", "🍔", "🌈", "🦄", "🐶", "🦊", "🦓",
             "🐷", "🐄", "🐼", "🦚", "🐳", "🚀", "🌌", "🌀", "❄", "🌊", "🪐", "🎃", "🎄", "🎆", "🏆", "⚽", "⚾", "🥎",
             "🏀", "🏐", "🏈", "🏉", "🎾", "🥏", "🎳", "🏓", "🏸", "🥊", "🔮", "🎲"]
# 处理飞书事件的路由
@app.route('/feishu/event', methods=['POST'])
def feishu_event():
    req_data = request.get_json()
    print(req_data)
    logging.info(f"Received event: {json.dumps(req_data)}")
    # 提取 content
    try:
        message_content = req_data['event']['message']['content']
        content_dict = json.loads(message_content)
        text_content = content_dict.get('text', '')

        # 提取 name
        mentions = req_data['event']['message'].get('mentions', [])
        names = [mention.get('name', '') for mention in mentions]
        # 处理 im.message.receive_v1 事件
        if "information source" in names:
            handle_message(text_content)
    except Exception as e:
        logging.info(f"提取content失败: {e}")

    if 'challenge' in req_data:
        return jsonify({'challenge': req_data['challenge']})
    return jsonify()


def handle_message(text_content):
    """
    处理消息逻辑
    """
    content = text_content.split(' ')[-1]
    if '查看信息源' in content or '查看启动的信息源' in content or '查看关闭的信息源' in content:
        logging.info(content)
        news_source = find_all_source(content)
        push_lark(news_source)

    elif '添加信息源-' in content:
        logging.info("添加信息源")
        result = add_source(content)
        push_lark(result)
    elif '搜索-' in content:
        logging.info("搜索信息源")
        result = search_source(content)
        push_lark(result)

    elif '打开信息源-' in content:
        logging.info("打开信息源")
        result = change_source(1, content)
        push_lark(result)

    elif '关闭信息源-' in content:
        logging.info("关闭信息源")
        result = change_source(0, content)
        push_lark(result)

    elif '使用指南' in content:
        logging.info("使用指南")
        news_source = guide()
        push_lark(news_source)



    else:
        logging.info("无效命令")
        pass


# 数据库请求
def post_url(db_id, sql_query):
    url = 'https://data.dev.agione.ai/api/v1/data/operate'
    headers = {
        'api-key': 'mc-FgnKamL9MvsvLhK1PRyrzNJu8mg-r108p7_1ezq1PDjo-rMiN7eH3ofq-p6LDMBr',
        'Content-Type': 'application/json'
    }
    data = {
        "db_id": db_id,
        "sql_query": sql_query
    }

    # 将数据转换为 JSON 格式
    json_data = json.dumps(data)

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json_data)
    if response.status_code == 200:
        return response
    else:
        logging.info(f"{response.status_code},{response.json()}")
        return 0

def search_source(user_content):
    content = {
        "card": {
            "elements": [],
            "header": {
                "title": {
                    "content": "信息源",
                    "tag": "plain_text"
                }
            }
        }
    }
    search_name = user_content.split("-")[1]
    print(search_name)
    if "," in search_name:
        search_name = search_name.split(",")
        all_name = '%'.join(search_name)
        sql_query = f"SELECT * FROM information_source WHERE category LIKE '%{all_name}%';"
    elif "=" in search_name:
        sql_query = f"SELECT * FROM information_source WHERE {search_name};"
    else:
        sql_query = f"SELECT * FROM information_source WHERE category LIKE '%{search_name}%';"
        print(sql_query)

    response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643", sql_query)
    if response:
        rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        if rows:
            for new in rows:
                status = "关闭" if new[3] == 0 else "启动"

                news_data0 = {"tag": "div",
                              "text": {"content": f"名称：{new[0]} ；种类：{new[2]} ；链接：{new[1]}",
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
                    "tag": "action"
                }

                content["card"]["elements"].append(news_data0)
                content["card"]["elements"].append(news_data2)
            return content
        else:
            result = {
                "card": {
                    "elements": [],
                    "header": {"title": {
                        "content": "没有该种类信息源",
                        "tag": "plain_text"
                    }}
                }
            }
    else:
        result = {
            "card": {
                "elements": [],
                "header": {"title": {
                    "content": "请求失败",
                    "tag": "plain_text"
                }}
            }
        }
    return result


def guide():
    title_icon = random.choice(ICON_LIST)
    content = {
        "card": {
            "elements": [],
            "header": {
                "title": {
                    "content": "使用指南",
                    "tag": "plain_text"
                }
            }
        }
    }
    news_data0 = {"tag": "div",
                  "text": {"content": f"{title_icon}查看所有信息源请输入：(查看信息源)五个关键字即可查看.\n例如:**查看信息源**",
                           "tag": "lark_md",
                           }
                  }
    news_data1 = {"tag": "div",
                  "text": {
                      "content": f"{title_icon}搜索信息源请输入：搜索-你想要查询的种类-相关信息源，将关键词用-包含即可.\n例如:**搜索-经济-相关信息源**",
                      "tag": "lark_md"}
                  }

    news_data2 = {"tag": "div",
                  "text": {
                      "content": f"{title_icon}添加信息源请输入：添加信息源-name-url-category-status，输入关键词前用-开头即可.\n例如:**添加信息源-name-url-category-status**",
                      "tag": "lark_md"}
                  }
    news_data3 = {"tag": "div",
                  "text": {
                      "content": f"{title_icon}改变信息源状态请输入：关闭(打开)信息源-name，输入关键词前用-开头即可.\n例如:**打开信息源-量子位**",
                      "tag": "lark_md"}
                  }

    content["card"]["elements"] = [news_data0, news_data1, news_data2, news_data3]
    return content


def change_source(status, content):
    name = content.split("-")[1]
    sql_query = f"UPDATE information_source SET status={status} where name='{name}';"
    response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643", sql_query)
    turn = "关闭" if status == 0 else "启动"
    if response:
        result = {
            "card": {
                "elements": [],
                "header": {"title": {
                    "content": f"{turn}信息源-{name}成功",
                    "tag": "plain_text"
                }}
            }
        }

    else:
        result = {
            "card": {
                "elements": [],
                "header": {"title": {
                    "content": "请求失败",
                    "tag": "plain_text"
                }}
            }
        }
    return result


def add_source(content):
    print("add_source>>>>>")
    x = content.split('-')
    name, url, category, status = x[1], x[2], x[3], x[4]
    print(">>>>>>>>>>>>>>>>>>>",name, url, category, status)
    sql_query1 = "SELECT name FROM information_source"
    response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643", sql_query1)
    if response:
        rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        flattened_list = [item for sublist in rows for item in sublist]
        found = name in flattened_list
        if not found:
            sql_query2 = f"INSERT INTO information_source (name,url,category,status) VALUES ('{name}', '{url}', '{category}', '{status}');"
            response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643", sql_query2)
            if response:
                result = {
                    "card": {
                        "elements": [],
                        "header": {"title": {
                            "content": "添加成功",
                            "tag": "plain_text"
                        }}
                    }
                }

        else:
            result = {
                "card": {
                    "elements": [],
                    "header": {"title": {
                        "content": "添加失败，数据库存在该信息源",
                        "tag": "plain_text"
                    }}
                }
            }
    else:
        result = {
            "card": {
                "elements": [],
                "header": {"title": {
                    "content": "请求失败",
                    "tag": "plain_text"
                }}
            }
        }

    return result


def find_all_source(content):
    icon = random.choice(ICON_LIST)
    title_icon = random.choice(ICON_LIST)
    introduction_icon = random.choice(ICON_LIST)
    href_icon = random.choice(ICON_LIST)
    if "关闭" in content:
        sql_query = "SELECT * FROM information_source WHERE status = 0"
    elif "启动" in content:
        sql_query = "SELECT * FROM information_source WHERE status = 1"
    else:
        sql_query = "SELECT * FROM information_source"

    response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643", sql_query)
    if response:
        rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        content = {
            "card": {
                "elements": [{"tag": "hr"}],
                "header": {
                    "title": {
                        "content": f"{icon}信息源",
                        "tag": "plain_text"

                    }
                }
            }
        }
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
            content["card"]["elements"].append(title)
            content["card"]["elements"].append(introduction)
            content["card"]["elements"].append(news_data2)
            content["card"]["elements"].append({"tag": "hr"})
    else:
        content = {
            "card": {
                "elements": [],
                "header": {"title": {
                    "content": "请求失败",
                    "tag": "plain_text"
                }}
            }
        }
    return content


def push_lark(content):
    url = 'https://open.larksuite.com/open-apis/bot/v2/hook/c3ba0601-f8f6-4e5c-9de9-d578380772c5'
    params = {
        "msg_type": "interactive",
    }
    headers = {
        'Content-Type': 'application/json',
    }
    for key, values in content.items():
        params[key] = values
    response = requests.post(url, json=params, headers=headers)
    logging.info(f"{response.status_code}:{response.json()}")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6200, debug=True)
    # server = pywsgi.WSGIServer(('127.0.0.1', 6200), app)
    # server.serve_forever()


