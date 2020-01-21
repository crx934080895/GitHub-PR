# -- coding: utf-8 --

# 浏览器控制脚本库
import requests
from bs4 import BeautifulSoup
import retrying


class PR_STRUCT:
    url = ""
    tag = []
    content = ""
    commit_url = ""
    issue_url = ""


@retry(wait_fixed=3000)
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
ok_num = {}
# 未通过的PR编号列表
fail_num = {}
# 未识别的PR编号列表
unknown_num = {}


# 访问PR标签页面
for num in range(1, 5):

    try:
        # 重试标志
        attempts = 0
        success = False

        while attempts < 3 and not success:
            try:
                print("第" + str(attempts + 1) + "次" + "页码:" + str(num) + "开始获取")
                # 请求页面，参数2是页码
                PR_page = get_pr_html(project_url_list, num)
                PR_page_soup = BeautifulSoup(PR_page.text, "html5lib")
                # PR列表区域标签
                PR_div = PR_page_soup.find("div",
                                           attrs={"class": "js-navigation-container js-active-navigation-container"})
                # PR列表
                PR_list = PR_div.contents
                success = True
            except:
                attempts += 1
                if attempts == 3:
                    break
    except:
        print("页码:" + str(num) + "获取失败")
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

pass
