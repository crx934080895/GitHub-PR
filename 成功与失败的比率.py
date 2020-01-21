# -- coding: utf-8 --

import requests
from bs4 import BeautifulSoup
import pylab as plt
from matplotlib import font_manager
#import numpy as np


def get_pr_html(url, page):
    url = url+'&page='+str(page)
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }
    try:
        r = requests.get(url, timeout=15, headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r
    except:
        print('网页获取失败')


# 项目的PR链接
project_url_list = "https://github.com/tensorflow/tensorflow/pulls?q=is%3Apr+is%3Aclosed"

# 通过的PR编号列表
ok_num = []
# 未通过的PR编号列表
fail_num = []
# 未识别的PR编号列表
unknown_num = []
# 成功与失败的比率字典
ok_rate_dic = {}


# 访问PR标签页面
for num in range(100, 0, -1):

    try:
        # 重试标志
        attempts = 0
        success = False

        while attempts < 3 and not success:
            try:
                print("第"+str(attempts+1)+"次"+"页码:"+str(num)+"开始获取")
                # 请求页面，参数2是页码
                PR_page = get_pr_html(project_url_list, num)
                PR_page_soup = BeautifulSoup(PR_page.text, "html5lib")
                #PR列表区域标签
                PR_div = PR_page_soup.find("div", attrs={"class": "js-navigation-container js-active-navigation-container"})
                #PR列表
                PR_list = PR_div.contents
                success = True
            except:
                attempts += 1
                if attempts == 3:
                    break
    except:
        print("页码:"+str(num)+"获取失败")
        continue

    #清理PR_list列表多余项
    for i in PR_list:
        if type(i) != "Tag":
            PR_list.remove(i)

    # 遍历PR列表（第一次分类，根据是否通过分类）
    for PR in PR_list:
        url_num = PR.find("div",attrs={"class": "float-left col-8 lh-condensed p-2"}).contents[1].attrs["href"].split("/")[-1]
        # 判断是通过的
        if PR.find("svg",attrs={"class": "octicon octicon-git-merge merged"})!=None:
            ok_num[url_num] = str(0)
            continue
        # 判断是失败的
        if PR.find("svg",attrs={"class": "octicon octicon-git-pull-request closed"})!=None:
            fail_num[url_num] = str(0)
            continue
        unknown_num[url_num] = str(0)

    print("页码:" + str(num) + "获取结束")

    ok_quantity = ok_num.__len__()
    fail_quantity = fail_num.__len__()
    ok_rate_dic[num] = ok_quantity/(fail_quantity+ok_quantity)

#字体路径
my_font = font_manager.FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc")
# x与y的值列表
x = list(ok_rate_dic.keys())
x.reverse()
y = list(ok_rate_dic.values())
# 设置长度
fig = plt.figure(figsize=(100, 8), dpi=200)
plt.xlabel("页码", fontproperties=my_font)
plt.ylabel("通过占比率", fontproperties=my_font)
plt.title("从项目开始时的通过比率", fontproperties=my_font)
plt.plot(x, y)
plt.savefig("filename.png")
plt.show()
