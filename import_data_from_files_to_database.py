import pymysql
import os


class DatabaseImporter:
    config = {
        "address": "localhost",
        "user": "root",
        "password": "123456",
        "database_name": "github_tensorflow"
    }
    files_path = "/pr_data/"
    # 读取文件的标记，0表示读取全部，1表示只读取ok，2表示只读取fail
    flag = 0

    def __init___(self,flag):
        self.flag = flag
        # 打开数据库连接
        db = pymysql.connect(self.config["address"], self.config["user"], self.config["password"], self.config["database_name"])
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()

    def read_from_files(self):
        files_path_list = []
        ok_file_dic = {}
        fail_file_dic = {}
        if self.flag == 0:
            files_path_list.append(self.files_path + "fail_pr_comment/")
            files_path_list.append(self.files_path + "ok_pr_comment/")
        if self.flag == 1:
            files_path_list.append(self.files_path + "ok_pr_comment/")
        if self.flag == 2:
            files_path_list.append(self.files_path + "fail_pr_comment/")

        for i in files_path_list:
            files_list = os.listdir(i)





database_importer = DatabaseImporter()
pass