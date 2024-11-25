import json
import pandas as pd
from datetime import datetime
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO
import requests
import numpy as np
import io
import json
from io import BytesIO
import pdfplumber


def extract_text_from_pdf(pdf_url):
    """从 PDF URL 中提取文本和表格信息"""
    text = ""
    try:
        response = requests.get(pdf_url)
        # print(response.text)
        response.raise_for_status()  # 检查请求是否成功
    except requests.RequestException as e:
        print(f"Error fetching PDF: {e}")
        return []

    pdf_stream = BytesIO(response.content)

    with pdfplumber.open(pdf_stream) as pdf:
        for page_number, page in enumerate(pdf.pages):
            content = page.extract_text()
            content = content.replace("\n", " ").strip() if content else ""
            content = content.replace("None", "空")
            text+=f"page:{page_number}:\n{content}\n"
    return text

def insert_db(item):
    db_url = "https://data.dev.agione.ai/api/v1/data/operate"
    db_api_key = "mc-RukrJPgw4y6hYnWAMiPIZ0DZ5NndmZvdchYon0ss2tD8kBd3cRiwRtM14TkFtFrx"
    db_id = "76a6b495-0733-4a62-91c3-770bfd9c7643"

    headers = {
        "api-key": db_api_key,
        "Content-Type": "application/json"
    }

    sql_query = f"INSERT INTO industry_report (title,content,up_time) VALUES ('{item['title']}','{item['content']}','{item['up_time']}');"

    print(">>>sql_query", sql_query)

    data = {
        "db_id": db_id,
        "sql_query": sql_query
    }

    response = requests.post(db_url, headers=headers, data=json.dumps(data, indent=4))

    # Check the status code
    result = ""
    print(">>>status_code: ", response.status_code)
    print(item['title'])
    # print(">>>response_json: ", response.json())
    if response.status_code == 200:
        print("Request successful")
        response_json = response.json()
    else:
        print("Request failed with status code:", response.status_code)
        result = ""

    return result



def extract_tables_from_page(pdf_stream, page_number):
    """从 PDF 数据流中提取表格信息"""
    table_texts = ""
    with pdfplumber.open(pdf_stream) as pdf:
        page = pdf.pages[page_number]
        tables = page.extract_tables()
        # print(tables)
        if tables:
            table_texts += json.dumps(tables, ensure_ascii=False)
    return table_texts


def pdf_content(pdf_url):
    if not pdf_url.lower().endswith('.pdf'):
        result = ""
    else:
        result = extract_text_from_pdf(pdf_url)
        result = json.dumps(result, ensure_ascii=False)
    return result









def get_report(url):
    report = []
    response = requests.get(url)
    response.raise_for_status()  # 确保请求成功

    # 将响应内容转换为 StringIO 对象，以便 pandas 可以读取
    csv_data = StringIO(response.text)

    # 使用 pandas 读取 CSV 数据
    df = pd.read_csv(csv_data)

    first_column = df.iloc[:, 0].astype(str)  # 第一列
    time_column = df.iloc[:, 2].astype(str)  # 第一列
    fifth_column = df.iloc[:, 4].astype(str)  # 第五列

    # 输出结果
    for first, fifth, up_time in zip(first_column, fifth_column, time_column):
        report.append({"title": first, "pdf_path": fifth, "time": up_time})
    print("all_report", report)
    return report

def process_item(item):
    """Process each item by analyzing its PDF and returning the title and content."""
    # try:
    content = pdf_content(item['pdf_path'])
    result = {"title": item['title'], "content": content,"up_time":item['time']}
    # except Exception as e:
    # print(e)
    # content = ""
    # result = {}

    return result





all_report = []
urls = ["https://github.com/manymore13/report/raw/f05f742be280e70c44db49514b77325aeb178271/eastmoney/%E4%BA%92%E8%81%94%E7%BD%91%E6%9C%8D%E5%8A%A1.csv","https://github.com/manymore13/report/raw/f05f742be280e70c44db49514b77325aeb178271/eastmoney/%E8%BD%AF%E4%BB%B6%E5%BC%80%E5%8F%91.csv"]

for url in urls:
    report = get_report(url)
    all_report.extend(report)

print(all_report)


all_content = []

with ThreadPoolExecutor(max_workers=20) as executor:
    # Submit tasks to the executor
    futures = {executor.submit(process_item, item): item for item in all_report[1:]}

    # Collect results as they are completed
    for future in as_completed(futures):
        try:
            all_content.append(future.result())
        except Exception as e:
            print(f"Error processing item: {e}")

for report in all_content:
    insert_db(report)

