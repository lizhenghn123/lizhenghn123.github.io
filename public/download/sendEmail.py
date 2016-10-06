# -*- coding: utf-8 -*-
import os
import smtplib
from email.Header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

#### 常用邮箱发件服务器及端口
# 邮箱	发件服务器	非SSL协议端口	SSL协议端口
# 163	smtp.163.com	25	        465/587
# gmail	smtp.gmail.com	-	        465
# qq	smtp.qq.com	    25	        465/587


# 发送纯文本邮件
def sendMailText(title, content, sender, receiver, serverip, serverport, username, pwd):
    
    msg = MIMEText(content, _subtype="html", _charset="utf-8")    # 设置正文为符合邮件格式的HTML内容
    msg['Subject'] = Header(title, "utf-8")     # 设置邮件标题
    msg['From'] = sender                        # 设置发件人
    msg['To'] = receiver                        # 设置收件人
    #msg['To'] = ";".join(receiver)             # 多个收件人
    
    s = smtplib.SMTP(serverip, serverport)      # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
    #s.ehlo()
    #s.starttls()
    s.login(username, pwd)                      # 登陆邮箱
    s.sendmail(sender, receiver, msg.as_string())  # 发送邮件

# 发送带附件的邮件
def sendMailWithAttachment(title, content, sender, receiver, serverip, serverport, username, pwd, attach = {}):

    attachsize = len(attach)
    if attachsize > 0 :
        print 'send attach'
        msg = MIMEMultipart()   #创建一个带附件的实例

        for path, name in attach.items():
            print path, name
            if os.path.exists(path):
                att = MIMEText(open(path, 'rb').read(), 'base64', 'gb2312')   #构造附件
                att["Content-Type"] = 'application/octet-stream'
                att["Content-Disposition"] = 'attachment; filename="' + name + '"'
                print att["Content-Disposition"]
                msg.attach(att)
                # http://help.163.com/09/1224/17/5RAJ4LMH00753VB8.html 提示发送病毒或垃圾邮件 554, 'DT:SPM 163
    else:
        print 'send none'
        msg = MIMEText(content, _subtype="html", _charset="utf-8")    # 设置正文为符合邮件格式的HTML内容
        
    msg['Subject'] = Header(title, "gb2312")    # 设置邮件标题
    msg['From'] = sender                        # 设置发件人
    msg['To'] = receiver                        # 设置收件人

    #return    
    s = smtplib.SMTP(serverip, serverport)      # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
    #s.ehlo()
    #s.starttls()
    s.login(username, pwd)                      # 登陆邮箱
    s.sendmail(sender, receiver, msg.as_string())  # 发送邮件

# 发送带图片附件的邮件
def sendMailWithImage(title, content, sender, receiver, serverip, serverport, username, pwd, images = {}):

    imagesize = len(images)
    if imagesize > 0 :
        print 'send attach'
        msg = MIMEMultipart()   #创建一个带附件的实例

        for path, name in images.items():
            print path, name
            if os.path.exists(path):
                image = MIMEImage(open(path,'rb').read())
                #image = MIMEImage(open(path,'rb').read(), _subtype="jpg")
                image.add_header("Content-Disposition", "attachment", filename=name)
                #image.add_header('Content-ID','<image1>')
                #image.add_header("Content-ID", "")
                image.add_header('Content-ID', '<0>')
                image.add_header('X-Attachment-Id', '0')

                # We reference the image in the IMG SRC attribute by the ID we give it below         
                #msg.attach(MIMEText('<html><body><h1>hello</h1>' + '<p><img src="cid:0"></p>' + '</body></html>', 'html', 'utf-8'))
                
                msg.attach(image)
    else:
        print 'send none'
        msg = MIMEText(content, _subtype="html", _charset="utf-8")    # 设置正文为符合邮件格式的HTML内容
        
    msg['Subject'] = Header(title, "gb2312")    # 设置邮件标题
    msg['From'] = sender                        # 设置发件人
    msg['To'] = receiver                        # 设置收件人

    #return    
    s = smtplib.SMTP(serverip, serverport)      # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
    #s.ehlo()
    #s.starttls()
    s.login(username, pwd)                      # 登陆邮箱
    s.sendmail(sender, receiver, msg.as_string())  # 发送邮件


# 发送含有各种元素的邮件
def sendMail(title, content, sender, receiver, serverip, serverport, username, pwd, attach = {}, images = {}):
    
    msg = MIMEMultipart()
    msg['Subject'] = Header(title, "utf-8")     # 设置邮件标题
    msg['From'] = sender                        # 设置发件人
    msg['To'] = receiver                        # 设置收件人
    #msg['To'] = ";".join(receiver)             # 多个收件人

    attachsize = len(attach)
    if attachsize > 0 :
        print 'send attach'
        for path, name in attach.items():
            3print path, name
            if os.path.exists(path):
                att = MIMEText(open(path, 'rb').read(), 'base64', 'gb2312')   #构造附件
                att["Content-Type"] = 'application/octet-stream'
                att["Content-Disposition"] = 'attachment; filename="' + name + '"'
                print att["Content-Disposition"]
                msg.attach(att)

    imagesize = len(images)
    if imagesize > 0 :
        for path, name in images.items():
            #print path, name
            if os.path.exists(path):
                image = MIMEImage(open(path,'rb').read())
                #image = MIMEImage(open(path,'rb').read(), _subtype="jpg")
                image.add_header("Content-Disposition", "attachment", filename=name)
                image.add_header('Content-ID', '<0>')
                image.add_header('X-Attachment-Id', '0')

                msg.attach(image)
                
    s = smtplib.SMTP(serverip, serverport)      # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
    #s.ehlo()
    #s.starttls()
    s.login(username, pwd)                      # 登陆邮箱
    s.sendmail(sender, receiver, msg.as_string())  # 发送邮件
    
if __name__ == "__main__":
    
    config = {
    "from": "XXXXXXXXX@163.com",            # 发件人邮箱
    "to": "YYYYYYYYY@qq.com",               # 收件人邮箱
    "serverip": "smtp.163.com",             # 发件服务器IP
    "serverport":"25",                      # 发件服务器Port
    "username": "XXXXXXXXX",                # 发件人用户名
    "pwd": "zzzzzzzzzzzzzz"                 # 发件人密码
    }
    
    title = "python send mail"
    body = "<a href='http://cpper.info'>cpper</a>"

    # 测试发送文本邮件
    #sendMailText(title, body, config['from'], config['to'], config['serverip'], config['serverport'], config['username'], config['pwd'])

    attach = {}  # key : 要发送的文件，需要存在，否则读取不到：value ：自定义发送邮件中的文件名
    attach['sendEmail.py'] = '1.py'  
    attach['memset.cpp'] = '2.c'
    attach['noexist.cpp'] = '3.cpp'

    # 测试发送带附件邮件
    #sendMailWithAttachment(title, body, config['from'], config['to'], config['serverip'], config['serverport'], config['username'], config['pwd'], attach)

    # 测试发送带图片邮件
    images = {}
    images['test.jpg'] = '1.jpg'
    #sendMailWithImage(title, body, config['from'], config['to'], config['serverip'], config['serverport'], config['username'], config['pwd'], images)

    # 测试发送带各种元素邮件
    sendMail(title, body, config['from'], config['to'], config['serverip'], config['serverport'], config['username'], config['pwd'], attach, images)













    