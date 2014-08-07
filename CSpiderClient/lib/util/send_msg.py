#!/usr/bin/env python
#coding=UTF8
'''
    Created on 2013-11-12
    @author: devin
    @desc:  发送邮件 
'''

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE,formatdate
from email import encoders


QQ_MAIL_SERVER = {'name': 'smtp.qq.com', "user": "send_msg@qq.com", "pwd": "send_msg"}
N126_MAIL_SERVER = {'name': 'smtp.126.com', "user": "send_msg@126.com", "pwd": "Sogou2016"}

def send_mail(server, fro, to, subject, text, files = []):
    '''
        server为邮件服务器相关信息，类型为dict，需要包括name、user、pwd
        fro为发件人地址
        to为收件人地址，类型为list
        subject为邮件标题
        text为邮件正文
        files为邮件附件
    '''
    assert type(server) == dict
    assert type(to) == list
    assert type(files) == list

    msg = MIMEMultipart()
    msg['From'] = fro
    msg['Subject'] = subject
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg.attach(MIMEText(text))

    for file in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(file, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
        msg.attach(part)

    smtp = smtplib.SMTP(server['name'])
    smtp.login(server['user'], server['pwd'])
    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 1:
        print "Usage: %s " %sys.argv[0]
        sys.exit()

    send_mail(N126_MAIL_SERVER, 'send_msg@126.com', ['send_msg@qq.com'], "test", "测试")

