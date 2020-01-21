# -- coding: utf-8 --
import requests
from bs4 import BeautifulSoup


#参数是PR编号
def get_detail_html(num):
    url = "https://github.com/tensorflow/tensorflow/pull/"+str(num)
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }
    try:
        r = requests.get(url, timeout=15, headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r
    except:
        print("PR编号:" + str(num) + "获取失败")


def pass_classify(ok_num):
    for num in ok_num.keys():
        #获取某个PR详情页面的内容
        try:
            # 重试标志
            attempts = 0
            success = False

            while attempts < 3 and not success:
                try:
                    print("PR编号" + str(num) + "开始获取")
                    pr_page = get_detail_html(num)
                    pr_page_soup = BeautifulSoup(pr_page.text, "html5lib")
                    success = True
                except:
                    attempts += 1
                    if attempts == 3:
                        break
        except:
            print("PR编号:" + str(num) + "获取失败")
            continue

