topic_uuid = "60329b93-66b3-49dc-80c5-f11dcc8dcbcd"
max_retry = 3
organization_name = "Questnx"
db_api_key = 'mc-FgnKamL9MvsvLhK1PRyrzNJu8mg-r108p7_1ezq1PDjo-rMiN7eH3ofq-p6LDMBr'
db_id = "76a6b495-0733-4a62-91c3-770bfd9c7643"
model_name = "openai/gpt-4o-mini"
temperature = "0.3"
max_tokens = "4096"
ai_api_key = 'as-IZ0I0qkGBbIm7owj8z5Z_Q'
project_id = "monitor_news_os213jxs"





import requests
import json
import logging
# 配置日志
log_file = "./logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
url_db = 'https://data.dev.agione.ai/api/v1/data/operate'
headers = {
    'api-key': db_api_key,
    'Content-Type': 'application/json'
}
data = {
    "db_id": db_id,
    "sql_query": f"SELECT app_id,app_secret,webhook_url from organization_information_source where organization_name = '{organization_name}'"
}

# 将数据转换为 JSON 格式
json_data = json.dumps(data)

# 发送 POST 请求
response = requests.post(url_db, headers=headers, data=json_data)
data = response.json()['data']
# 打印响应结果
for i in data['executed_result']['query_result']['rows']:
    app_id = i[0]
    app_secret = i[1]
    webhook_url = i[2]







