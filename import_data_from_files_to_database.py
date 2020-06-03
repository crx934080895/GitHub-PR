import pymysql
import os
import re


class DatabaseImporter:
    config = {
        "address": "localhost",
        "user": "root",
        "password": "123456",
        "database_name": "github_tensorflow"
    }
    data_path = "./pr_data/"
    # 读取文件的标记，0表示读取全部，1表示只读取ok，2表示只读取fail
    flag = 0

    def __init___(self, flag):
        self.flag = flag
        # 打开数据库连接
        db = pymysql.connect(self.config["address"], self.config["user"], self.config["password"], self.config["database_name"])
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()

    def read_from_files(self):
        fail_files_path = self.data_path + "fail_pr_comment/"
        ok_files_path = self.data_path + "ok_pr_comment/"
        ok_file_dic = {}
        fail_file_dic = {}

        def read_ok_files(files_path):
            files_list = os.listdir(files_path)
            for file in files_list:
                result = {}
                f = open(files_path + file, "r", encoding="utf-8")
                words_chips = f.read().split("####################################################################")
                # 获取标题
                tittle = re.findall(r"tittle:.+\n",words_chips[0])[0].strip()
                result["tittle"] = tittle

                # 获取内容
                comment = words_chips[1].replace("\n", "")
                result["comment"] = comment

                # 获取时间
                submit_time = re.findall(r"submit_time:.*\n",words_chips[2])[0].strip().replace("submit_time:","")
                close_time = re.findall(r"close_time:.*\n",words_chips[2])[0].strip().replace("close_time:","")
                spent_time = re.findall(r"spent_time:.*\n",words_chips[2])[0].strip().replace("spent_time:","")
                result["submit_time"] = submit_time
                result["close_time"] = close_time
                result["spent_time"] = spent_time

                #更改.md文件的标记
                md_flag = re.findall(r"\d",words_chips[3])[0]
                result["md_flag"] = md_flag

                # 结果存入大字典
                ok_file_dic[file.replace(".txt","")] = result

        if self.flag == 0:
            read_ok_files(ok_files_path)


        if self.flag == 1:
            read_ok_files(ok_files_path)

        if self.flag == 2:








database_importer = DatabaseImporter()
pass