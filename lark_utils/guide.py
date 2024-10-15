import random


ICON_LIST = ["🍼", "☕", "🥛", "🥃", "🍺", "🍨", "🍩", "🍪", "🍧", "🍦", "🍭", "🎂", "🍰", "🍫", "🥧", "🧁", "🍬", "🍮",
             "🍯", "🍵", "🍸", "🍹", "🧊", "🧃", "🧉", "🍣", "🍇", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏", "🍐",
             "🍑", "🍒", "🍓", "🥝", "🍅", "🥥", "🍡", "🍤", "🍥", "🍛", "🍿", "🍕", "🍔", "🌈", "🦄", "🐶", "🦊", "🦓",
             "🐷", "🐄", "🐼", "🦚", "🐳", "🚀", "🌌", "🌀", "❄", "🌊", "🪐", "🎃", "🎄", "🎆", "🏆", "⚽", "⚾", "🥎",
             "🏀", "🏐", "🏈", "🏉", "🎾", "🥏", "🎳", "🏓", "🏸", "🥊", "🔮", "🎲"]


def guide():
    title_icon = random.choice(ICON_LIST)
    content = {
            "elements": [],
            "header": {
                "title": {
                    "content": "使用指南",
                    "tag": "plain_text"
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

    content["elements"] = [news_data0, news_data1, news_data2, news_data3, news_data4, news_data5, news_data6]
    return content
