import requests

import config


def kongai(sysytem_content,user_content):
    llm_route, model_name = config.model_name.split('/', 1)
    messages = [{
        "role": "system",
        "content": sysytem_content
    }, {
        "role": "user",
        "content": user_content
    }]

    # 添加用户消息
    llm_params = {
        "model": model_name or None,
        "temperature": float(config.temperature) or None,
        "max_tokens": int(config.max_tokens) or None,
        "messages": messages,
        "stream": False
    }
    # print(llm_params)
    headers = {
        "ai-api-key": config.ai_api_key,
        "project-id": config.project_id
    }
    # print(headers)

    url = f"https://gateway.agione.ai/{llm_route}/api/v1/chat"
    print(url)
    response = requests.post(url, json=llm_params, headers=headers)

    # 检查响应状态码
    if response.status_code != 200:
        # 如果状态码不是200，返回错误信息
        raise ValueError(f"Error: {response.status_code}, {response.text}")

    response_data = response.json()

    if response_data.get("choices"):
        first_choice = response_data["choices"][0]
        content = first_choice["message"]["content"]
        # print("llm",content)
        return content
    else:
        # 如果响应中没有choices，返回一个空
        return ""