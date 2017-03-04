#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-02-22 09:44:42
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import datetime  
import email  
import smtplib  
import os  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  

import DateTool
  
class MyEmail:  
    def __init__(self):  
        self.confilepth = 'mail.conf'
        self.user = ""  
        self.passwd = ""  
        self.to_list = []  
        self.cc_list = []  
        self.tag = None  
        self.doc = None  
        self.initAccount()
    def initAccount(self):
        f = open('mail.conf')
        tmps = f.readlines()
        f.close()
        self.user = tmps[0]
        self.passwd = tmps[1]
        if len(tmps) > 2:
            self.to_list = tmps[2].split(',')
        if len(tmps) > 3:
            self.cc_list = tmps[3].split(',')
    def send(self,ttag,ttext):  
        ''''' 
        发送邮件 
        '''  
        self.tag = ttag
        try:  
            server = smtplib.SMTP_SSL("smtp.exmail.qq.com",port=465)  
            server.login(self.user,self.passwd)  
            server.sendmail(self.user, self.to_list, self.get_attach(ttext))  
            server.close()  
            print "send email successful"  
        except Exception,e:  
            ortstr = conventStrTOUtf8(str(e))
            print ortstr
            print "send email failed"  
    def get_attach(self,ttext):  
        ''''' 
        构造邮件内容 
        '''  
        attach = MIMEMultipart()  
        #添加邮件内容  
        txt = MIMEText(ttext)  
        attach.attach(txt)  
        if self.tag is not None:  
            #主题,最上面的一行  
            attach["Subject"] = self.tag  
        if self.user is not None:  
            #显示在发件人  
            attach["From"] = "Mage<%s>"%self.user  
        if self.to_list:  
            #收件人列表  
            attach["To"] = ";".join(self.to_list)  
        if self.cc_list:  
            #抄送列表  
            attach["Cc"] = ";".join(self.cc_list)  
        if self.doc:  
            pass
            #估计任何文件都可以用base64，比如rar等  
            #文件名汉字用gbk编码代替  
            # name = os.path.basename(self.doc).encode("gbk")  
            # f = open(self.doc,"rb")  
            # doc = MIMEText('填写邮件内容','plain','utf-8')
            # doc["Content-Type"] = 'application/octet-stream'  
            # doc["Content-Disposition"] = 'attachment; filename="'+name+'"'  
            # attach.attach(doc)  
            # f.close()  
        return attach.as_string()  

if __name__=="__main__":  
    my = MyEmail()  
    datetmp = DateTool.getNowStrDate()
    tag = "%s股票推荐"%(datetmp)  
    my.send(tag,'发送邮件测试')  

