import os
import json
import requests
from bs4 import BeautifulSoup
import re
import jieba
from collections import Counter

# 伪装成 Mozilla, 绕过反爬虫
headers = {'user-agent': 'Mozilla/5.0', "cookie": ""}


# 下载所有 HTML 页面
def download_all_html():
    html_list = []
    for index in range(5):
        # 爬虫目标网址
        url = f"http://book.zongheng.com/store/c0/c0/b0/u0/p{index + 1}/v9/s9/t0/u0/i1/ALL.html"
        print("Climb URL: ", url)
        r = requests.get(url, headers=headers)
        # 将页面保存到 html_list 中返回
        html_list.append(r.text)
    return html_list


# 解析单个 HTML 页面, 获取其中所有的 <a> 标签内容
def parse_singe_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    a_list = soup.find_all("a")
    data_list = []
    for a in a_list:
        # 遍历列表中所有 <a> 标签, 获取 <a> 标签中的 title 和 href
        title = a.get_text()
        link = a["href"]
        # 将获取到的 <a> 标签下的 title 和 href 保存到 data_list 中返回
        data_list.append({"title": title, "link": link})
    print(data_list)
    return data_list


# 获取所有 <div class"bookintro"> 标签中的内容
def get_book_intro(html):
    BeautifulSoup(html, 'html.parser')
    # 用正则表达式获取页面中所有 <div class"bookintro"> 标签
    pattern = re.compile(r'<div class="bookintro">(.*?)</div>', re.S)
    a_tag_list = pattern.findall(html)
    print(a_tag_list)
    return a_tag_list


# 获取图片
def get_image(html):
    # 用正则表达式获取页面中所有 .jpg 图片
    pattern_jpg = re.compile(r'<img src="(.*?).jpg" alt="(.*?)">')
    jpg_list = pattern_jpg.findall(html)
    for image in jpg_list:
        # 遍历列表中所有 .jpg 图片链接
        print(image[0] + ".jpg" + "  ,  " + image[1] + ".jpg")
        r = requests.get(image[0] + ".jpg", headers=headers)
        # 保存 .jpg 图片
        save_image(r, "data\\image\\" + image[1] + ".jpg")

    # 用正则表达式获取页面中所有 .jpeg 图片
    pattern_jpeg = re.compile(r'<img src="(.*?).jpeg" alt="(.*?)">')
    jpeg_list = pattern_jpeg.findall(html)
    for image in jpeg_list:
        # 遍历列表中所有 .jpeg 图片链接
        print(image[0] + ".jpeg" + "  ,  " + image[1] + ".jpeg")
        r = requests.get(image[0] + ".jpeg")
        # 保存 .jpeg 图片
        save_image(r, "data\\image\\" + image[1] + ".jpeg")


# 保存文件
def write_data(data_list, file_name):
    # 将文本数据保存到文件中
    # 打开文件, 若没有则创建
    with open("data\\temp\\" + file_name, "w", encoding='UTF-8') as file:
        for data in data_list:
            file.write(json.dumps(data, ensure_ascii=False) + "\n")
    print('文件保存成功！')


# 保存图片
def save_image(r, file_path):
    # 打开文件，若没有则创建
    file = open(file_path, 'ab')
    # 写入数据
    file.write(r.content)
    print(file_path, '图片保存成功！')
    # 关闭文件
    file.close()


# 创建停用词列表
def create_stop_word_list(file):
    stop_word_list = [line.strip() for line in open(file, 'r', encoding='UTF-8').readlines()]
    return stop_word_list


# 对句子进行分词
def scrip_sentence(sentence):
    strip_sentence = jieba.cut(sentence.strip())
    # 加载停用词文件
    stop_word_list = create_stop_word_list('stop-words/Baidu Stop Words.txt')
    final_sentence = ''
    # 判断词语是否为停用词
    for word in strip_sentence:
        if word not in stop_word_list:
            if word != '\t':
                final_sentence += word
                final_sentence += " "
    return final_sentence


# 统计词语数量
def count_word(n):
    for i in range(1, n + 1):
        # 获取 intro 文件夹中所有文件
        source_file_dir = "data\\temp\\intro\\"
        file_name_list = os.listdir(source_file_dir)
        # 打开第 i 页的 "已经去除停用词的分词汇总" 文件, 如果没有则创建
        file = open("data\\total\\Page " + str(i) + " Script Word.txt", 'w', encoding="UTF-8")
        # 遍历文件
        for file_name in file_name_list:
            file_path = source_file_dir + '\\' + file_name
            # 遍历单个文件, 读取每一行
            for line in open(file_path, encoding="UTF-8", errors="ignore"):
                # 对句子进行分词
                script_line = scrip_sentence(line)
                try:
                    file.write(script_line)
                except UnicodeError:
                    continue
        # 关闭文件
        file.close()
        # 打开 "已经去除停用词的分词汇总" 文件
        with open("data\\total\\Page " + str(i) + " Script Word.txt", 'r', encoding="UTF-8") as fr:
            data = jieba.cut(fr.read().replace(' ', ''))
        data = dict(Counter(data))
        # 打开 "存储词频统计" 的文件
        with open("data\\total\\Page " + str(i) + " Word Count.txt", 'w', encoding="UTF-8") as fw:
            for k, v in data.items():
                fw.write('%s: %d\n' % (k, v))
    print("Climb end...")


# 创建存储结果数据的文件夹
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists("data\\image"):
    os.mkdir("data\\image")
if not os.path.exists("data\\total"):
    os.mkdir("data\\total")
if not os.path.exists("data\\temp"):
    os.mkdir("data\\temp")
if not os.path.exists("data\\temp\\a"):
    os.mkdir("data\\temp\\a")
if not os.path.exists("data\\temp\\intro"):
    os.mkdir("data\\temp\\intro")

# 获取 HTML 页面
_html_list = download_all_html()
_i = 0
for _html in _html_list:
    _data_list = []
    _data_list.extend(parse_singe_html(_html))
    _i = _i + 1
    # 存储 <a> 标签的 href 属性和 title 属性
    _file = "a\\Page " + str(_i) + " href and title.txt"
    write_data(_data_list, _file)

_i = 0
for _html in _html_list:
    _data_list = []
    _data_list.extend(get_book_intro(_html))
    _i = _i + 1
    # 存储 <div class="bookintro"> 标签的 href 属性
    _file = "intro\\Page" + str(_i) + " href.txt"
    write_data(_data_list, _file)

for _html in _html_list:
    get_image(_html)

# 开始统计, 参数: 指定统计多少页 HTML
count_word(5)
