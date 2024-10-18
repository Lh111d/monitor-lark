import logging
import json
from apscheduler.schedulers.background import BackgroundScheduler
from lark_utils.subscription_news import sub_add, sub_information, change_sub_information
from lark_utils.news_source import search_source,add_source,change_source,find_all_source
from lark_utils.push import push_lark, test_lark
from lark_utils.guide import guide
from lark_utils.push_news import push_news
from topic.topic_log import topic_log
from threading import Thread
from flask import Flask, request, jsonify
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



# 定义任务调度
def start_scheduler():
    scheduler = BackgroundScheduler()

    # 每小时的第10分钟执行一次任务
    scheduler.add_job(push_news, 'cron', minute=10)

    # 启动调度器
    scheduler.start()

    # push_news()

# 启动 Flask 应用的函数
def run_flask_app():
    logging.info("Flask应用正在运行...")
    app.run(host="0.0.0.0", port=6238, debug=False)  # 将debug设为False避免重复启动


# 多线程同时运行 Flask 和调度任务
if __name__ == '__main__':

    # 创建并启动 Flask 线程
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # 启动定时任务
    start_scheduler()

    # 捕捉退出事件，确保任务和线程正常退出
    try:
        # 让主线程保持运行，等待任务执行
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logging.info("程序正在退出...")
        flask_thread.join()  # 等待 Flask 线程结束