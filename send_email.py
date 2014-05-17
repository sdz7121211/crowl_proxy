#-*- encoding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class email(object):

    def __init__(self,
            smtp_address="smtp.exmail.qq.com",
            smtp_user="dazhuang@37degree.com",
            smtp_pwd="dz.*"):
        self.msg = MIMEMultipart()
        self.smtp_address = smtp_address
        self.smtp_user = smtp_user
        self.smtp_pwd = smtp_pwd

    def set_to(self, to="670108918@qq.com"):
        self.msg["to"] = to

    def set_from(self, from_="dazhuang@37degree.com"):
        self.msg["from"] = from_

    def set_subject(self, subject=""):
        self.msg["subject"] = subject

    def add_attachment(self, path):
        filename = path.split("/")[-1]
        attachment = MIMEText(open(path, "rb").read(), "base64", "gb2312")
        attachment["Content-Type"] = "application/octet-straem"
        attachment["Content-Disposition"] = "attachment; filename='%s'"%filename
        self.msg.attach(attachment)

    def send(self):
        self.server = smtplib.SMTP()
        self.server.connect(self.smtp_address)
        self.server.login(self.smtp_user, self.smtp_pwd)
        self.server.sendmail(self.msg["from"],
                self.msg["to"],
                self.msg.as_string())
        self.server.quit()


if __name__ == "__main__":
    import os
    print os.getcwd()
    obj = email()
    obj.set_to("670108918@qq.com")
    obj.set_from("dazhuang@37degree.com")
    obj.set_subject(u"测试")
    obj.add_attachment(os.getcwd()+"/xiecheng.csv")
    obj.send()

