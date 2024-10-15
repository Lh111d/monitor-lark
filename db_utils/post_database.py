import logging
import requests
import json
import config


log_file = "./logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# 根据sql语句操作数据库
def post_url(db_id, sql_query):
    url = 'https://data.dev.agione.ai/api/v1/data/operate'
    headers = {
        'api-key': config.db_api_key,
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