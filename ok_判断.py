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


# 获取PR通过耗时
@retrying.retry(wait_fixed=2000)
def get_time(pr_num):
    pr_page_html = get_html(project_pull_url + str(pr_num))
    pr_page_soup = BeautifulSoup(pr_page_html.text, "html5lib")
    # 获取通过时间
    pass_time_array = pr_page_soup.find("relative-time").attrs['datetime'].replace('T', '-').replace('Z', '')\
        .replace(':', '-').split('-')
    pass_time = datetime.datetime(int(pass_time_array[0]), int(pass_time_array[1]), int(pass_time_array[2]),
                                  int(pass_time_array[3]), int(pass_time_array[4]), int(pass_time_array[5]))

    # 获取提交时间
    submit_time_tag = pr_page_soup.find("h3", attrs={"class": "timeline-comment-header-text f5 text-normal"}).find("relative-time")
    submit_time_array = submit_time_tag.attrs['datetime'].replace('T', '-').replace('Z', '').replace(':', '-').split('-')
    submit_time = datetime.datetime(int(submit_time_array[0]), int(submit_time_array[1]), int(submit_time_array[2]),
                                    int(submit_time_array[3]), int(submit_time_array[4]), int(submit_time_array[5]))
    spent_time = (pass_time - submit_time)
    return spent_time


# 判断修改md文件,若修改了则返回1，反之返回0
@retrying.retry(wait_fixed=2000)
def judge_md(pr_num):
    # 更改md文件的标签
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


# 判断pr是否是重构优化，是则返回1，反之为0
@retrying.retry(wait_fixed=2000)
def judge_refactor(pr_num):
    # 获取pr页面
    pr_page_html = get_html(project_pull_url + str(pr_num))
    pr_page_soup = BeautifulSoup(pr_page_html.text, "html5lib")
    # pr标题内容
    pr_title = pr_page_soup.find("h1", attrs={"class": "gh-header-title"}).text.strip()
    # 如果标题含有“重构”等词汇则返回1
    if "Refactor" in pr_title or "refactor" in pr_title:
        return 1

    # pr内容获取
    pr_content = pr_page_soup.find("div", attrs={"class": "js-discussion js-socket-channel ml-6 pl-3"})
    # 如果内容含有“重构”等词汇则返回1
    if "Refactor" in pr_content.text or "refactor" in pr_content.text:
        return 1
    # 没有找到关键字，返回0
    return 0


# 判断pr是否是修补bug，若修补自己的bug则返回1，别人的返回2，无法判断返回3，不是修bug返回0
@retrying.retry(wait_fixed=2000)
def judge_fix_bug(pr_num):
    # bug判断标志
    flag = 0
    # 获取pr页面
    pr_page_html = get_html(project_pull_url + str(pr_num))
    pr_page_soup = BeautifulSoup(pr_page_html.text, "html5lib")
    pr_author = pr_page_soup.find("a", attrs={"class": "author link-gray-dark css-truncate-target width-fit"}).text

    # 判断标题含有判断修复Bug的关键词
    pr_title = pr_page_soup.find("h1", attrs={"class": "gh-header-title"}).text.strip()
    if "bug" in pr_title or "Bug" in pr_title or "fix" in pr_title or "Fix" in pr_title:
        flag = 3
    pr_content = pr_page_soup.find("div", attrs={"class": "js-discussion js-socket-channel ml-6 pl-3"})
    # 判断内容含有判断修复Bug的关键词
    if "bug" in pr_content.text or "Bug" in pr_content.text or "fix" in pr_content.text or "Fix" in pr_content.text:
        flag = 3

    # 判断是否存在issue
    issue_tags = pr_content.find_all("a", attrs={"class": "issue-link js-issue-link"})
    # 去除异常issue链接，在网页中，有些PR链接用的是issue的class标签
    for i in issue_tags:
        if "issue" not in i.attrs['href']:
            issue_tags.remove(i)
        else:
            continue

    if issue_tags.__len__() != 0:
        # 如果存在issue链接，那么去分析对应的issue信息
        for issue_tag in issue_tags:
            issue_url = issue_tag.attrs['href']
            issue_page_html = get_html(issue_url)
            issue_page_soup = BeautifulSoup(issue_page_html.text, "html5lib")

            # 判断issue里面是否有判断PR是修补Bug的关键词
            issue_title = issue_page_soup.find("span", attrs={"class": "js-issue-title"}).text.strip()
            if "bug" in issue_title or "Bug" in issue_title or "fix" in issue_title:
                flag = 3
            issue_content = issue_page_soup.find("div", attrs={"class": "js-discussion js-socket-channel ml-0 pl-0 ml-md-6 pl-md-3"})
            # 判断内容含有判断修复Bug的关键词
            if "bug" in issue_content.text or "Bug" in issue_content.text or "fix" in issue_content.text:
                flag = 3

            # 判断pr中出现的issue作者是否和pr作者相同 若相同则bug是自己发现的，不同则为其他人
            issue_author = issue_page_soup.find("a", attrs={"class": "author link-gray-dark css-truncate-target width-fit"}).text
            # 在判断作者名字相同之前，需要确定这个PR是修补Bug的
            if flag == 3:
                if issue_author == pr_author:
                    flag = 1
                else:
                    flag = 2
            else:
                continue

    # 判断是否存在commit
    commit_tags = pr_page_soup.find_all("a", attrs={"class": "commit-link"})
    if commit_tags.__len__() != 0:
        # 如果存在commit链接，那么去分析对应的commit信息
        for commit_tag in commit_tags:
            commit_url = commit_tag.attrs['href']
            commit_page_html = get_html(commit_url)
            commit_page_soup = BeautifulSoup(commit_page_html.text, "html5lib")
            # 判断commit描述中是否存在关键词
            commit_description = commit_page_soup.find("div", attrs={"class": "commit-desc"}).text.strip()
            if "bug" in commit_description or "Bug" in commit_description or "fix" in commit_description:
                flag = 3

            # 判断commit的作者和PR作者是否相同，但是commit的作者可能存在多个，需要逐个比对
            commit_authors = commit_page_soup.find_all("a", attrs={"class": "commit-author tooltipped tooltipped-s user-mention"})
            for commit_author in commit_authors:
                if flag == 3:
                    if commit_author.text == pr_author:
                        flag = 1
                    else:
                        flag = 2
                else:
                    continue
    return flag
