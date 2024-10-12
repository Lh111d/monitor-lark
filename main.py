import logging
import json
import random
from threading import Thread
from flask import Flask, request, jsonify
import requests
import time
app = Flask(__name__)

# 配置日志
log_file = "./logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ICON_LIST = ["🍼", "☕", "🥛", "🥃", "🍺", "🍨", "🍩", "🍪", "🍧", "🍦", "🍭", "🎂", "🍰", "🍫", "🥧", "🧁", "🍬", "🍮",
             "🍯", "🍵", "🍸", "🍹", "🧊", "🧃", "🧉", "🍣", "🍇", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏", "🍐",
             "🍑", "🍒", "🍓", "🥝", "🍅", "🥥", "🍡", "🍤", "🍥", "🍛", "🍿", "🍕", "🍔", "🌈", "🦄", "🐶", "🦊", "🦓",
             "🐷", "🐄", "🐼", "🦚", "🐳", "🚀", "🌌", "🌀", "❄", "🌊", "🪐", "🎃", "🎄", "🎆", "🏆", "⚽", "⚾", "🥎",
             "🏀", "🏐", "🏈", "🏉", "🎾", "🥏", "🎳", "🏓", "🏸", "🥊", "🔮", "🎲"]


# 处理飞书事件的路由
@app.route('/lark/event', methods=['POST'])
def feishu_event():
    # Get JSON data from the request
    req_data = request.get_json()
    print(req_data)
    logging.info(f"Received event: {json.dumps(req_data,ensure_ascii=False)}")

    try:
        # Extract message content and user ID
        message_content = req_data['event']['message']['content']
        content_dict = json.loads(message_content)
        text_content = content_dict.get('text', '')
        user_id = req_data['event']['sender']['sender_id'].get('user_id', '')

        # Extract mentioned names
        mentions = req_data['event']['message'].get('mentions', [])
        thread_id = req_data['event']['message'].get('thread_id', "")
        names = [mention.get('name', '') for mention in mentions]

        # Handle specific events
        if "information source" in names:
            thread = Thread(target=handle_message, args=(text_content,user_id,thread_id))
            thread.start()
            # handle_message(text_content, user_id,thread_id)
    except Exception as e:
        logging.info(f"Failed to extract content: {e}")

    # Respond to Feishu challenge for webhook verification
    if 'challenge' in req_data:
        return jsonify({'challenge': req_data['challenge']})

    return jsonify({"success":"true"})



def handle_message(text_content,user_id,thread_id):
    """
    处理消息逻辑
    """
    content = text_content.split(' ')[-1]
    if '查看信息源' in content or '查看启动的信息源' in content or '查看关闭的信息源' in content:
        logging.info(content)
        news_source = find_all_source(content)
        for i in news_source:
            push_lark(i)

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

    elif '查看订阅内容' in content:
        result = sub_information(user_id)
        for i in result:
            push_lark(i)

    elif '订阅-' in content:
        result = sub_add(content,user_id)
        push_lark(result)
  
    elif '关闭订阅内容-' in content:
        result = change_sub_information(content,user_id,0)
        push_lark(result)
        
    elif '打开订阅内容-' in content:
        result = change_sub_information(content,user_id,1)
        push_lark(result)
    elif '结束记录' in content:
        result,x = topic_log(thread_id)
        test_lark(x)
    else:
        logging.info("无效命令")
        pass
    return 0

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


def topic_log(thread_id):
  try:
    # 定义请求URL
        url = "https://flow.service.agione.ai/api/flow/service/60329b93-66b3-49dc-80c5-f11dcc8dcbcd"
        headers = {
            "Content-Type": "application/json",
            "api-key": "fl-zhixingqidian2099"
        }
        data = {
            "project_id": "internal_knowledge-topic-2598617f",
            "thread_id":thread_id
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # 打印响应
        if response.status_code ==200:
            results_json = response.json()
            results = results_json.get('result',"")
            logging.info(f"topic_log,{results}")
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>results",results)
  except Exception as e:
      results = ""
      logging.info(f"topic_log,{results}")
  content = {
      "card": {
          "elements": [],
          "header": {
              "title": {
                  "content": "话题记录",
                  "tag": "plain_text"
              }
          }
      }
  }
  news_data0 = {"tag": "div",
                    "text": {
                        "content": results,
                        "tag": "lark_md",
                        }
                    }
  content["card"]["elements"] = [news_data0]
  return content,results


def sub_add(content,user_id):
    subscription_content = content.split("-")[2]
    subscription_type = content.split("-")[1]
    sql_query = f"INSERT INTO subscription_information (receive_id,subscription_content,status,subscription_type) VALUES ('{user_id}', '{subscription_type}', 1,'{subscription_content}');"
    response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643", sql_query)
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
                    "content": "添加失败",
                    "tag": "plain_text"
                }}
            }
        }
    return result

def sub_information(user_id):
    icon = random.choice(ICON_LIST)
    title_icon = random.choice(ICON_LIST)
    introduction_icon = random.choice(ICON_LIST)
    href_icon = random.choice(ICON_LIST)
    sql_query = f"SELECT * FROM subscription_information WHERE receive_id = '{user_id}';"
    response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643",sql_query)
    contents = []
    if response:
        rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        mid_index = len(rows) // 2
        segments = [rows[:mid_index], rows[mid_index:]]
        for segment in segments:
            content = {
                "card": {
                    "elements": [{"tag": "hr"}],
                    "header": {
                        "title": {
                            "content": f"{icon}订阅信息",
                            "tag": "plain_text"

                        }
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
                content["card"]["elements"].append(title)
                content["card"]["elements"].append(introduction)
                content["card"]["elements"].append(news_data2)
                content["card"]["elements"].append({"tag": "hr"})

            contents.append(content)
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
        contents.append(content)
    return contents

def change_sub_information(content,user_id,status):
    sub_content = content.split("-")[1]
    sql_query = f"UPDATE subscription_information SET status={status} where receive_id='{user_id}' and subscription_content = '{sub_content}';"
    response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643", sql_query)
    turn = "关闭" if status == 0 else "启动"
    if response:
        result = {
            "card": {
                "elements": [],
                "header": {"title": {
                    "content": f"{turn}订阅类型-{sub_content}成功",
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

def search_source(user_content):
    icon = random.choice(ICON_LIST)
    title_icon = random.choice(ICON_LIST)
    introduction_icon = random.choice(ICON_LIST)
    href_icon = random.choice(ICON_LIST)
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
        query = search_name.split("=")
        sql_query = f"SELECT * FROM information_source WHERE {query[0]}='{query[1]}';"
        print(search_name)
    else:
        sql_query = f"SELECT * FROM information_source WHERE category LIKE '%{search_name}%';"
        print(sql_query)

    response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643", sql_query)
    if response:
        rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        result = {
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
            result["card"]["elements"].append(title)
            result["card"]["elements"].append(introduction)
            result["card"]["elements"].append(news_data2)
            result["card"]["elements"].append({"tag": "hr"})
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
                  "text": {
                      "content": f"{title_icon}查看所有信息源请输入：(查看信息源)五个关键字即可查看.\n例如:**查看信息源**,**查看启动的信息源**,**查看关闭的信息源**",
                      "tag": "lark_md",
                      }
                  }
    news_data1 = {"tag": "div",
                  "text": {
                      "content": f"{title_icon}搜索信息源请输入：搜索-你想要查询的种类-相关信息源，将关键词用-包含即可.\n例如:**搜索-经济-相关信息源**\n例如:**搜索-经济,文化-相关信息源**\n例如:**搜索-name=量子位-相关信息源**",
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
    news_data4 = {"tag": "div",
                    "text": {
                        "content": f"{title_icon}查看订阅信息请输入：(查看订阅内容)六个关键字即可查看.\n例如:**查看订阅内容**",
                        "tag": "lark_md"}
                    }
    news_data5 = {"tag": "div",
                    "text": {
                        "content": f"{title_icon}添加订阅信息请输入：订阅-订阅类型-订阅内容，输入关键词前用-开头即可.\n例如:**订阅-web3,game-提取游戏玩法，游戏亮点，剧情设计，市场等**",
                        "tag": "lark_md"}
                    }

    news_data6 = {"tag": "div",
                  "text": {
                      "content": f"{title_icon}改变信息源状态请输入：关闭(打开)订阅内容-订阅内容，输入关键词前用-开头即可.\n例如:**打开订阅内容-新闻**",
                      "tag": "lark_md"}
                  }

    content["card"]["elements"] = [news_data0, news_data1, news_data2, news_data3, news_data4, news_data5, news_data6]
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
    print(">>>>>>>>>>>>>>>>>>>", name, url, category, status)
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
        sql_query = "SELECT * FROM information_source WHERE status = 0;"
    elif "启动" in content:
        sql_query = "SELECT * FROM information_source WHERE status = 1;"
    else:
        sql_query = "SELECT * FROM information_source;"

    response = post_url("76a6b495-0733-4a62-91c3-770bfd9c7643", sql_query)
    contents = []
    if response:
        rows = response.json()["data"]["executed_result"]["query_result"]["rows"]
        mid_index = len(rows) // 2
        segments = [rows[:mid_index], rows[mid_index:]]
        for segment in segments:
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
                content["card"]["elements"].append(title)
                content["card"]["elements"].append(introduction)
                content["card"]["elements"].append(news_data2)
                content["card"]["elements"].append({"tag": "hr"})

            contents.append(content)
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
        contents.append(content)
    return contents


def push_lark(content):
    urls = ['https://open.larksuite.com/open-apis/bot/v2/hook/c3ba0601-f8f6-4e5c-9de9-d578380772c5',['https://open.larksuite.com/open-apis/bot/v2/hook/eaa16517-4ef4-4065-aea1-0d65507f75ff']]
    params = {
        "msg_type": "interactive",
    }
    headers = {
        'Content-Type': 'application/json',
    }
    for key, values in content.items():
        params[key] = values
    for url in urls:
        response = requests.post(url, json=params, headers=headers)
        logging.info(f"{response.status_code}:{response.json()}")
    return 0


def test_lark(content):
    app_id = "cli_a62a0213e5b89009"
    app_secret = "4K8JtkGsQ04hWP6Z6R6s6e7IxmzhMvvD"
    url = 'https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal'
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    headers = {
        "Content-Type":"application/json; charset=utf-8"
    }
    response = requests.post(url, headers=headers, json=data)
    
    print(f"response >> {response.text}")

    my_json = response.json()
    tenant_access_token = my_json["tenant_access_token"]
    text = content.split("###")
    receive_ids = text[1].split(",")
    logging.info(f"receive_ids,{receive_ids}")
    for receive_id in receive_ids:
        url = "https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type=open_id"
        payload = json.dumps({
        	"content": json.dumps({"text":text[0]}),
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


if __name__ == '__main__':
    print(1111111111111111111111111111111111)
    app.run(host="0.0.0.0", port=6238, debug=True)
    # server = pywsgi.WSGIServer(('127.0.0.1', 6200), app)
    # server.serve_forever()

