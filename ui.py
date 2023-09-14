# -*- coding:utf-8 -*-
'''
@Author: nEwt0n_m1ku
@contact: cto@ddxnb.cn
@Time: 2023/09/11 0011 09:32
@version: 1.0
'''
from flask import Flask, render_template, request, jsonify
import openpyxl

app = Flask(__name__)


# 解析Excel文件并将数据存储在一个列表中
def parse_excel(filename):
    news_data = []
    wb = openpyxl.load_workbook(filename)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        news_data.append({
            'external_title': row[0],
            'title': row[1],
            'link': row[2],
            'date_and_time': f"{row[3]} {row[4]}",  # 整合日期和时间
            'author': row[5],
            'type': row[6],
            'tag': row[7]
        })
    return news_data


@app.route('/')
def show_news():
    # 从Excel文件中解析新闻数据
    news_data = parse_excel('news_data.xlsx')
    return render_template('index.html', news_data=news_data)


@app.route('/sort_news', methods=['POST'])
def sort_news():
    column_index = int(request.form['columnIndex'])
    news_data = [...]  # 获取你的新闻数据

    # 根据列索引对新闻数据进行排序
    if column_index == 0:
        news_data.sort(key=lambda x: x['title'].lower())
    elif column_index == 1:
        news_data.sort(key=lambda x: x['link'].lower())
    elif column_index == 2:
        news_data.sort(key=lambda x: x['date_and_time'])  # 日期和时间降序排序
    elif column_index == 3:
        news_data.sort(key=lambda x: x['author'].lower())
    elif column_index == 4:
        news_data.sort(key=lambda x: x['type'].lower())
    elif column_index == 5:
        news_data.sort(key=lambda x: x['tag'].lower())

    # 将排序后的数据以JSON响应返回
    return jsonify(news_data)


if __name__ == "__main__":
    app.run(debug=True)
