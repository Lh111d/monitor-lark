import logging
import json
import requests

import config

# 配置日志
log_file = "./logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def topic_log(thread_id):
    try:
        # 定义请求URL
        url = "https://flow.service.agione.ai/api/flow/service/{}".format(config.topic_uuid)
        headers = {
            "Content-Type": "application/json",
            "api-key": "fl-zhixingqidian2099"
        }
        data = {
            "project_id": "internal_knowledge-topic-2598617f",
            "thread_id": thread_id
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # 打印响应
        if response.status_code == 200:
            results_json = response.json()
            results = results_json.get('result', "")
            logging.info(f"topic_log,{results}")
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>results",results)
    except Exception as e:
        results = ""
        logging.info(f"topic_log,{results}")
    content = {
            "elements": [],
            "header": {
                "title": {
                    "content": "话题记录",
                    "tag": "plain_text"
                }
            }
        }
    news_data0 = {"tag": "div",
                  "text": {
                      "content": results,
                      "tag": "lark_md",
                  }
                  }
    content["elements"] = [news_data0]
    return content, results