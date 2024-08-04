使用监控群
[图片]
将该机器人添加进去即可

推送机器人
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
将代码里面的url更改成对应的webhook即可

Flask服务监控事件
if name == '__main__':
    app.run(host="0.0.0.0", port=6300, debug=True)
    
对应修改端口号


使用方法
完成上面两步，@information source 机器人 输入使用指南 即可告知：
查看所有信息源请输入：(查看信息源)五个关键字即可查看. 例如：查看信息源
搜索信息源请输入：搜索-你想要查询的种类-相关信息源，将关键词用-包含即可.例如搜索-经济-相关信息源
添加信息源请输入：添加信息源-name-url-category-status，输入关键词前用-开头即可.例如添加信息源-name-url-category-status
改变信息源状态请输入：关闭(打开)信息源-name，输入关键词前用-开头即可.例如：打开信息源-量子位

