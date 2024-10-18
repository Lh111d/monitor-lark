from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging

# 定义任务
def push_news():
    print("定时任务执行")
    logging.info("定时任务 push_news 执行")

# 启动调度器
def start_scheduler():
    scheduler = BackgroundScheduler()

    # 每30秒执行一次任务
    scheduler.add_job(push_news, 'interval', seconds=30)

    # 启动调度器
    scheduler.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_scheduler()

    # 让主线程继续运行
    try:
        while True:
            time.sleep(60)  # 每60秒检查一次任务
    except (KeyboardInterrupt, SystemExit):
        pass
