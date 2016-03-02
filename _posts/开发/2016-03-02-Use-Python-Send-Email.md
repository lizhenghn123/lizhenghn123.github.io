---
layout: post

title: 使用Python发送邮件

category: 开发

tags: 开发 Python

keywords: 开发 技术 Python 发送邮件

description: 使用Python的smtplib和email两个模块来发送各种类型的邮件，比如文本邮件、带附件的邮件、带图片的邮件等

---

Python是一门很简单和强大的语言，在熟悉其他编程语言的基础上，可以很快的入门Python。Python本身内置了很多工具模块，远比C++方便的多（当然各自的适合场景不同）。

这里简单介绍下我使用python中email模块发送邮件的相关知识。

SMTP是发送邮件的协议，Python内置对SMTP的支持，可以发送纯文本邮件、HTML邮件以及带附件的邮件。python发送邮件主要使用到了smtplib和email两个模块，email负责构造邮件，smtplib负责发送邮件。

## 相关模块
### smtplib模块
	smtplib.SMTP()
	smtplib.SMTP([host[, port[, local_hostname[, timeout]]]])

SMTP类构造函数，表示与SMTP服务器之间的连接，通过这个连接可以向smtp服务器发送指令，执行相关操作（如：登陆、发送邮件）。所有参数都是可选的。参数意义如下：

     host：smtp服务器主机名
     port：smtp服务的端口，默认是25；如果在创建SMTP对象的时候提供了这两个参数，在初始化的时候会自动调用connect方法去连接服务器。

smtplib模块还提供了SMTP_SSL类和LMTP类，对它们的操作与SMTP基本一致。

smtplib.SMTP提供的方法：

     SMTP.set_debuglevel(level)：#设置是否为调试模式。默认为False，即非调试模式，表示不输出任何调试信息。
     SMTP.connect([host[, port]])：#连接到指定的smtp服务器。参数分别表示smpt主机和端口。注意: 也可以在host参数中指定端口号（如：smpt.yeah.net:25），这样就没必要给出port参数。
     SMTP.docmd(cmd[, argstring])：向smtp服务器发送指令。可选参数argstring表示指令的参数。
     SMTP.helo([hostname]) ：使用"helo"指令向服务器确认身份。相当于告诉smtp服务器“我是谁”。
     SMTP.has_extn(name)：判断指定名称在服务器邮件列表中是否存在。出于安全考虑，smtp服务器往往屏蔽了该指令。
     SMTP.verify(address) ：判断指定邮件地址是否在服务器中存在。出于安全考虑，smtp服务器往往屏蔽了该指令。
     SMTP.login(user, password) ：登陆到smtp服务器。现在几乎所有的smtp服务器，都必须在验证用户信息合法之后才允许发送邮件。
     SMTP.sendmail(from_addr, to_addrs, msg[, mail_options, rcpt_options]) ：发送邮件。这里要注意一下第三个参数，msg是字符串，表示邮件。我们知道邮件一般由标题，发信人，收件人，邮件内容，附件等构成，发送邮件的时候，要注意msg的格式。这个格式就是smtp协议中定义的格式。
     SMTP.quit() ：断开与smtp服务器的连接，相当于发送"quit"指令。

### email模块
emial模块用来处理邮件消息，包括MIME和其他基于RFC 2822 的消息文档。使用这些模块来定义邮件的内容，是非常简单的。其包括的类有（[点此查看更加详细的介绍](http://docs.python.org/library/email.mime.html)）：

    class email.mime.base.MIMEBase(_maintype, _subtype, **_params)：这是MIME的一个基类。一般不需要在使用时创建实例。其中_maintype是内容类型，如text或者image。_subtype是内容的minor type 类型，如plain或者gif。 **_params是一个字典，直接传递给Message.add_header()。

    class email.mime.multipart.MIMEMultipart([_subtype[, boundary[, _subparts[, _params]]]]：MIMEBase的一个子类，多个MIME对象的集合，_subtype默认值为mixed。boundary是MIMEMultipart的边界，默认边界是可数的。

    class email.mime.application.MIMEApplication(_data[, _subtype[, _encoder[, **_params]]])：MIMEMultipart的一个子类。

    class email.mime.audio. MIMEAudio(_audiodata[, _subtype[, _encoder[, **_params]]])： MIME音频对象

    class email.mime.image.MIMEImage(_imagedata[, _subtype[, _encoder[, **_params]]])：MIME二进制文件对象。

    class email.mime.message.MIMEMessage(_msg[, _subtype])：具体的一个message实例.

	class email.mime.text.MIMEText(_text[, _subtype[, _charset]])：MIME文本对象，其中_text是邮件内容，_subtype邮件类型，可以是text/plain（普通文本邮件），html/plain(html邮件),  _charset编码，可以是gb2312等等。

## 几个实例代码

### 发送普通文本邮件
	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	import smtplib
	from email.mime.text import MIMEText
	from email.Header import Header

	def sendMailText(title, content, sender, receiver, serverip, serverport, username, pwd):
	    
	    msg = MIMEText(content, _subtype="plain", _charset="utf-8")    # 设置正文为符合邮件格式的HTML内容
	    msg['Subject'] = Header(title, "utf-8")     # 设置邮件标题
	    msg['From'] = sender                        # 设置发件人
	    msg['To'] = receiver                        # 设置收件人
	    
	    s = smtplib.SMTP(serverip, serverport)      # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
	    #s.ehlo()
	    #s.starttls()
	    s.login(username, pwd)                      # 登陆邮箱
	    s.sendmail(sender, receiver, msg.as_string())  # 发送邮件
	
	if __name__ == "__main__":
	    
	    config = {
	    "from": "XXXXXXXXX@163.com",            # 发件人邮箱
	    "to": "YYYYYYYYYY@163.COM",             # 收件人邮箱
	    "serverip": "smtp.163.com",             # 发件服务器IP
	    "serverport":"25",                      # 发件服务器Port
	    "username": "XXXXXXXXX@163.com",        # 发件人用户名
	    "pwd": "AAAAAAAAAAAAAA"                 # 发件人密码
	    }
	    
	    title = "python send mail"
	    body = "<a href='http://cpper.info'>cpper</a>"
		
	    sendMailText(title, body, config['from'], config['to'], config['serverip'], config['serverport'], config['username'], config['pwd'])

### 发送Html格式邮件
与上面介绍的文本邮件基本一致，除了一点不同：  

	msg = MIMEText(content, _subtype="html", _charset="utf-8")

### 发送带附件的邮件
如果发送带附件的邮件，首先要创建MIMEMultipart()实例，然后构造附件，如果有多个附件，可依次构造，最后利用smtplib.smtp发送。

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
	                msg.attach(att)
	                # http://help.163.com/09/1224/17/5RAJ4LMH00753VB8.html 提示发送病毒或垃圾邮件 554, 'DT:SPM 163
	    else:
	        msg = MIMEText(content, _subtype="html", _charset="utf-8")    # 设置正文为符合邮件格式的HTML内容
	        
	    msg['Subject'] = Header(title, "gb2312")    # 设置邮件标题
	    msg['From'] = sender                        # 设置发件人
	    msg['To'] = receiver                        # 设置收件人

	    s = smtplib.SMTP(serverip, serverport)      # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
	    s.login(username, pwd)                      # 登陆邮箱
	    s.sendmail(sender, receiver, msg.as_string())  # 发送邮件

    attach = {}  # key : 要发送的文件，需要存在，否则读取不到：value ：自定义发送邮件中的文件名
    attach['sendEmail.py'] = '1.py'  
    attach['memset.cpp'] = '2.c'
    #attach['noexist.cpp'] = '3.cpp'
        
    sendMailWithAttachment(title, body, config['from'], config['to'], config['serverip'], config['serverport'], config['username'], config['pwd'], attach)

### 发送带图片的邮件

	def sendMailWithImage(title, content, sender, receiver, serverip, serverport, username, pwd, images = []):
	
	    imagesize = len(images)
	    if imagesize > 0 :
	        msg = MIMEMultipart()   #创建一个带附件的实例
	
	        for path in images:
	            print path
	            if os.path.exists(path):
	                image = MIMEImage(open(path,'rb').read())
	                name = path.split(os.sep)[-1]
	                image.add_header("Content-Disposition", "attachment", filename=name)
	                image.add_header('Content-ID', '<0>')
	                image.add_header('X-Attachment-Id', '0')	
	                # We reference the image in the IMG SRC attribute by the ID we give it below         
	                #msg.attach(MIMEText('<html><body><h1>hello</h1>' + '<p><img src="cid:0"></p>' + '</body></html>', 'html', 'utf-8'))	                
	                msg.attach(image)
	    else:
	        msg = MIMEText(content, _subtype="html", _charset="utf-8")    # 设置正文为符合邮件格式的HTML内容
	        
	    msg['Subject'] = Header(title, "gb2312")    # 设置邮件标题
	    msg['From'] = sender                        # 设置发件人
	    msg['To'] = receiver                        # 设置收件人

	    s = smtplib.SMTP(serverip, serverport)      # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
	    s.login(username, pwd)                      # 登陆邮箱
	    s.sendmail(sender, receiver, msg.as_string())  # 发送邮件

### 一个综合示例
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
	    s.login(username, pwd)                      # 登陆邮箱
	    s.sendmail(sender, receiver, msg.as_string())  # 发送邮件

	if __name__ == "__main__":
	
	    config = {
		    "from": "XXXXXXXXX@163.com",            # 发件人邮箱
		    "to": "YYYYYYYYYY@163.COM",             # 收件人邮箱
		    "serverip": "smtp.163.com",             # 发件服务器IP
		    "serverport":"25",                      # 发件服务器Port
		    "username": "XXXXXXXXX@163.com",        # 发件人用户名
		    "pwd": "AAAAAAAAAAAAAA"                 # 发件人密码
	    }
	    
	    title = "python send mail"
	    body = "<a href='http://cpper.info'>cpper</a>"
	
	    attach = {}  # key : 要发送的文件，需要存在，否则读取不到：value ：自定义发送邮件中的文件名
	    attach['sendEmail.py'] = '1.py'  
	    attach['memset.cpp'] = '2.c'
	    attach['noexist.cpp'] = '3.cpp'
	
	    images = {}
	    images['lizheng3.jpg'] = '1.jpg'
	
	    sendMail(title, body, config['from'], config['to'], config['serverip'], config['serverport'], config['username'], config['pwd'], attach, images)

## 代码下载
本文所有代码可以点此下载：[sendEmail.py](/public/download/sendEmail.py)。