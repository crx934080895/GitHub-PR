# -- coding: utf-8 --

import requests
from bs4 import BeautifulSoup
import retrying


def get_html(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }
    try:
        r = requests.get(url, timeout=15, headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r
    except:
        print(url + '网页获取失败')


class FailAnalyse:
    project_url = "https://github.com/tensorflow/tensorflow/"

    @retrying.retry(wait_fixed=2000)
    def get_fail_pr_comment(self):
        fail_file = open(".fail_list.txt", "r", encoding="utf-8")
        lines = fail_file.readlines()
        for line in lines:
            pr_number = line.strip()
            pr_page = get_html(self.project_url+"pull/"+pr_number)
            pr_page_soup = BeautifulSoup(pr_page.text, "html5lib")
            comment_file = open("./fail_pr_comment/" + pr_number + ".txt", "w", encoding="utf-8")
            try:
                # 根据关闭的标签来获取关闭者的评论
                close_comment = pr_page_soup.find("div", attrs={"class": "TimelineItem-badge text-white bg-red"}).parent.parent.\
                    find_previous_sibling().find("div", attrs={"class": "edit-comment-hide js-edit-comment-hide"}).text.strip()
            except:
                comment_file.write("No comment")
                comment_file.close()
                continue
            comment_file.write(close_comment)
            comment_file.close()
        fail_file.close()


fail_analyse = FailAnalyse()
fail_analyse.get_fail_pr_comment()