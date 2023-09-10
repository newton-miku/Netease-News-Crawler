import os
from time import sleep
import requests
from bs4 import BeautifulSoup
import openpyxl
import re


def scrape_news():
    """爬取新闻
    此函数调用后爬取网易新闻的新闻内容，返回一个新闻列表

    Returns:
        list: 新闻列表
    """
    urls = ['https://news.163.com/domestic/', 'https://news.163.com/world/', 'https://gov.163.com/',
            'https://tech.163.com/']
    news_data = []
    news_count = int(0)
    for url in urls:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            prefix = ['https://www.163.com/news/article/', 'https://www.163.com/dy/article/',
                      'https://www.163.com/tech/']

            for link in soup.find_all('a', href=True):
                href = link.get('href')
                title = link.get_text(strip=True)
                a_news = {'title': title, 'rtitle': None, 'link': href, 'date': None, 'time': None, 'author': None,
                          'type': None,
                          'tag': None, 'content': None}

                if href.startswith(prefix[0]):
                    a_news['type'] = '权威媒体'
                elif href.startswith(prefix[1]):
                    a_news['type'] = '自媒体'
                elif href.startswith(prefix[2]):
                    a_news['type'] = '网易科技'
                else:
                    continue

                if url == urls[0]:
                    a_news['tag'] = '国内'
                elif url == urls[1]:
                    a_news['tag'] = '国际'
                elif url == urls[2]:
                    a_news['tag'] = '政务'
                elif url == urls[3]:
                    a_news['tag'] = '科技'
                news_data.append(a_news)
                news_count += 1
                print("\r", end='')
                print(f"已采集新闻数量：{news_count}", flush=True, end="")
                # sleep(0.5)
        else:
            print(response.status_code, response.text)
    print()
    return news_data


def scrape_news_details(news_data):
    """爬取具体新闻
    此函数爬取具体新闻页面，更新到传入的新闻列表中

    Args:
        news_data (list): 新闻列表
    """
    news_count = int(0)
    ok_count = int(0)
    err_count = int(0)
    for news in news_data:
        url = news['link']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 在具体新闻页面中查找标题信息
            title_element = soup.find('h1', class_='post_title')
            if title_element:
                title = title_element.text.strip()
            else:
                title = "N/A"

            # 在具体新闻页面中查找时间和作者信息
            post_info = soup.find('div', class_='post_info')
            if post_info:
                # 使用正则表达式提取时间信息
                time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', post_info.text)
                if time_match:
                    time = time_match.group(0)
                    date, time = time.split()  # 分离日期和时间
                else:
                    time = "N/A"
                    date = "N/A"
                if url.startswith("https://www.163.com/tech/"):
                    author = '网易科技报道'
                else:
                    author_element = post_info.find('a', href=True)
                    if author_element:
                        author = author_element.text.strip()
                    else:
                        author = "N/A"
            # 提取文章内容
            content_element = soup.find('div', class_='post_body')
            if content_element:
                content = content_element.get_text(separator='\n')  # 获取所有段落内容并以换行分隔
            else:
                content = "N/A"
                print("无法获取具体内容")
            # 将获取到的信息添加到当前新闻字典中
            news['rtitle'] = title  # 实际标题
            news['date'] = date  # 添加日期字段
            news['time'] = time  # 添加时间字段
            news['author'] = author  # 发文账号
            news['content'] = content  # 具体内容
            # 保存文章内容到txt文件
            save_content_to_txt(news)
            ok_count += 1
        else:
            print(response.status_code, response.text)
            err_count += 1
        news_count += 1
        print("\r", end='')
        print(f"已处理新闻数量：{news_count},成功{ok_count}，失败{err_count}", flush=True, end="")
        sleep(0.1)


def save_to_excel(news_data, filename):
    """保存到Excel
    此函数将新闻列表保存到Excel文件中

    Args:
        news_data (list): 新闻列表
        filename (string): 文件名
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['外部标题', '标题', '链接', '日期', '时间', '作者', '媒体类别', '分类'])

    for news in news_data:
        ws.append(
            [news['title'], news['rtitle'], news['link'], news['date'], news['time'], news['author'], news['type'],
             news['tag']])

    wb.save(filename)


def clean_filename(filename):
    """移除文件名中的特殊字符

    Args:
        filename (string): 文件名

    Returns:
        string: 修改后的文件名
    """
    # 移除文件名中的特殊字符（部分字符在Windows下不可用于文件名）
    cleaned_filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    return cleaned_filename


def save_content_to_txt(news):
    """保存文章内容到txt文件
    此函数将文章内容保存到txt文件中

    Args:
        news (dict): 新闻字典
    """
    paths = []
    paths.append(f"新闻/{news['date']}/{news['tag']}")
    paths.append(f"媒体/{news['author']}/{news['date']}/{news['tag']}")
    # 构建文件路径并清理文件名
    cleaned_title = clean_filename(news['title'])
    for path in paths:
        os.makedirs(path, exist_ok=True)  # 创建目录，如果目录已存在则不会引发异常
        filename = f"{path}/{cleaned_title}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(news['content'])


if __name__ == "__main__":
    news_results = scrape_news()
    scrape_news_details(news_results)
    # print(news_results)
    save_to_excel(news_results, 'news_data.xlsx')
