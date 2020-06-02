# -- coding: utf-8 --

import requests
from bs4 import BeautifulSoup
import retrying
import datetime


project_pull_url = "https://github.com/tensorflow/tensorflow/pull/"


def get_html(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }
    r = requests.get(url, timeout=15, headers=headers)
    r.raise_for_status()
    r.encoding = 'utf-8'
    return r


# 判断修改md文件,若修改了则返回1，反之返回0
@retrying.retry(wait_fixed=2000)
def judge_md(pr_num):
    # 更改md文件的标记
    flag = 0
    # 获取commit详情页地址
    commit_page_html = get_html(project_pull_url+str(pr_num)+"/commits")
    commit_page_soup = BeautifulSoup(commit_page_html.text, "html5lib")
    commit_tag = commit_page_soup.find_all("a", attrs={"class": "sha btn btn-outline BtnGroup-item"})
    if commit_tag==None:
        return 0

    # commit详情页面分析
    for i in commit_tag:
        commit_detail_url = "https://github.com" + i.attrs["href"]
        commit_detail_page = get_html(commit_detail_url)
        commit_detail_soup = BeautifulSoup(commit_detail_page.text, "html5lib")
        file_info_div = commit_detail_soup.find("div", attrs={"class": "file-info flex-auto"})
        changed_file_name = file_info_div.find_all("a", attrs={"class": "link-gray-dark"})
        for j in changed_file_name:
            if ".md" in j.text:
                flag = 1

    if flag != 0:
        return 1
    else:
        return 0


# 判断修改示例文件,若修改了则返回1，反之返回0
@retrying.retry(wait_fixed=2000)
def judge_example(pr_num):
    keywords = ["example", "Example"]
    flag = 0
    # 获取PR页面
    pr_page_html = get_html(project_pull_url + str(pr_num))
    pr_page_soup = BeautifulSoup(pr_page_html.text, "html5lib")
    # PR标题
    pr_title = pr_page_soup.find("h1", attrs={"class": "gh-header-title"}).text.strip()
    for keyword in keywords:
        if keyword in pr_title:
            flag = 1

    # PR内容获取
    pr_content = pr_page_soup.find("div", attrs={"class": "edit-comment-hide js-edit-comment-hide"}).text.strip()
    for keyword in keywords:
        if keyword in pr_content:
            flag = 1

    return flag


@retrying.retry(wait_fixed=2000)
def judge_similar_pr(pr_num):
    keywords = ["same", "duplicate", "similar"]
    flag = 0
    # 获取PR页面
    pr_page_html = get_html(project_pull_url + str(pr_num))
    pr_page_soup = BeautifulSoup(pr_page_html.text, "html5lib")

    # 获取关闭时的评论内容
    close_content = pr_page_soup.find("div", attrs={"class": "TimelineItem-badge text-white bg-red"}).parent.parent.\
        find_previous_sibling().find("div", attrs={"class": "edit-comment-hide js-edit-comment-hide"}).text.strip()
    for keyword in keywords:
        if keyword in close_content:
            flag = 1
            break

    return flag
