# -*- coding:utf-8 -*-
'''
@Author: nEwt0n_m1ku
@contact: cto@ddxnb.cn
@Time: 2023/09/11 0011 14:22
@version: 1.0
'''
import ui as ui
from spider import scrape_news, scrape_news_details, save_to_excel  # 导入爬虫程序
import os

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        #避免flask在debug模式下运行两次爬虫
        news_results = scrape_news()
        scrape_news_details(news_results)
        save_to_excel(news_results, 'news_data.xlsx')
    ui.app.run(debug=True)
