import logging
import json
from lark_utils.subscription_news import sub_add, sub_information, change_sub_information
from lark_utils.news_source import search_source,add_source,change_source,find_all_source
from lark_utils.push import push_lark, test_lark
from lark_utils.guide import guide
from lark_utils.push_news import push_news
from topic.topic_log import topic_log
from threading import Thread
from flask import Flask, request, jsonify
import requests
import time
import sched
import time
import threading

app = Flask(__name__)

# 配置日志
log_file = "./logging.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# 处理飞书事件的路由
@app.route('/lark/event', methods=['POST'])
def feishu_event():
    # Get JSON data from the request
    req_data = request.get_json()
    print(req_data)
    logging.info(f"Received event: {json.dumps(req_data, ensure_ascii=False)}")

    try:
        # Extract message content and user ID
        message_content = req_data['event']['message']['content']
        content_dict = json.loads(message_content)
        text_content = content_dict.get('text', '')
        user_id = req_data['event']['sender']['sender_id'].get('user_id', '')

        # Extract mentioned names
        mentions = req_data['event']['message'].get('mentions', [])
        thread_id = req_data['event']['message'].get('thread_id', "")
        chat_id = req_data['event']['message'].get('chat_id', "")
        names = [mention.get('name', '') for mention in mentions]

        # Handle specific events
        if "information source" in names:
            thread = Thread(target=handle_message, args=(text_content, user_id, thread_id, chat_id))
            thread.start()
            # handle_message(text_content, user_id,thread_id)
    except Exception as e:
        logging.info(f"Failed to extract content: {e}")

    # Respond to Feishu challenge for webhook verification
    if 'challenge' in req_data:
        return jsonify({'challenge': req_data['challenge']})

    return jsonify({"success": "true"})


def handle_message(text_content, user_id, thread_id, chat_id):
    """
    处理消息逻辑
    """

    content = text_content.split(' ')[-1]
    if '查看信息源' in content or '查看启动的信息源' in content or '查看关闭的信息源' in content:
        logging.info(content)
        news_source = find_all_source(content)
        for i in news_source:
            push_lark(i, chat_id)

    elif '添加信息源-' in content:
        logging.info("添加信息源")
        result = add_source(content)
        push_lark(result, chat_id)
    elif '搜索-' in content:
        logging.info("搜索信息源")
        result = search_source(content)
        push_lark(result, chat_id)

    elif '打开信息源-' in content:
        logging.info("打开信息源")
        result = change_source(1, content)
        push_lark(result, chat_id)

    elif '关闭信息源-' in content:
        logging.info("关闭信息源")
        result = change_source(0, content)
        push_lark(result, chat_id)

    elif '使用指南' in content:
        logging.info("使用指南")
        news_source = guide()
        push_lark(news_source, chat_id)

    elif '查看订阅内容' in content:
        result = sub_information(user_id)
        for i in result:
            push_lark(i, chat_id)

    elif '订阅-' in content:
        result = sub_add(content, user_id)
        push_lark(result, chat_id)

    elif '关闭订阅内容-' in content:
        result = change_sub_information(content, user_id, 0)
        push_lark(result, chat_id)

    elif '打开订阅内容-' in content:
        result = change_sub_information(content, user_id, 1)
        push_lark(result, chat_id)
    elif '结束记录' in content:
        result, x = topic_log(thread_id)
        test_lark(x)
    else:
        logging.info("无效命令")
        pass
    return 0






def schedule_task():
    scheduler.enter(3600, 1, push_news)  # 每隔1小时执行
    scheduler.enter(3600, 1, schedule_task)  # 注册下一个任务
# 启动 Flask 应用的函数
def run_flask_app():
    logging.info("Flask应用正在运行...")
    app.run(host="0.0.0.0", port=6339, debug=False)  # 将debug设为False以避免重启

# 启动调度任务的函数
def run_scheduler():
    logging.info("开始定时任务")
    scheduler.enter(0, 1, schedule_task)  # 立即启动任务
    scheduler.run()  # 开始运行调度器

if __name__ == '__main__':
    # 创建并启动线程来运行调度器
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # 在主线程运行 Flask 应用
    run_flask_app()
