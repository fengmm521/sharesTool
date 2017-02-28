#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import shutil
import chardet
import time
import xlrd
import datetime
import urllib2

dbDir = 'db'
# f = open(dbDir + os.sep + '300208.csv','r')
# strtmp = f.readlines()
# f.close()

# oneline = strtmp[0]

# cntype = chardet.detect(strtmp[0])['encoding']

# onetmp = oneline.decode(cntype).encode('utf-8')


# f = open('chtypetest.logdat','w')
# f.write(onetmp)
# f.close()

# print chardet.detect(strtmp[0])
# print chardet.detect(onetmp)

def conventStrTOUtf8(oldstr):
    cnstrtype = chardet.detect(oldstr)['encoding']
    utf8str =  oldstr.decode(cnstrtype).encode('utf-8')
    return utf8str
#读取股票中文名
#将EXCEL表转换为json文件
def getAllCodeID(fullfilename):
    codedics = {}
    wb = xlrd.open_workbook(fullfilename)  
    for sheetName in wb.sheet_names():
        if sheetName=="Sheet1":
            nclows = 0
            sheet = wb.sheet_by_name(sheetName)
            print sheet.ncols
            for i in range(0,sheet.ncols):            
                if sheet.cell(2,i).value=='':
                ##print sheet.nrows,',',sheet.ncols,',',len(sheet.cell(2,sheet.ncols-1).value)
                    nclows=i
                    break
                else:
                    nclows=sheet.ncols
            print '表格列数='+ str(nclows)
            for rownum in range(1,sheet.nrows):
                linetmp = []
                for nnumber in range(3):#只取三列，股票编号,股票名,股票行业
                    if nnumber > 0:#中文转为utf8
                        linetmp.append(sheet.cell(rownum,nnumber).value.encode('utf-8'))
                    else:
                        linetmp.append(sheet.cell(rownum,nnumber).value)
                codedics[linetmp[0]] = linetmp
            print len(codedics)
    return codedics


# a = [2,4,1,8,3,2,3,5]
# a.sort()
# print a

urlstr = "http://quotes.money.163.com/service/chddata.html?code=1002752&start=20170220&end=20170228"
req = urllib2.Request(urlstr)  
# restr.add_header('Range', 'bytes=0-20')
resque = urllib2.urlopen(req) 

datatmp = resque.read()

tmpxxx = datatmp.split('\n')
aaa = tmpxxx[2].split(',')
print aaa[0],aaa[1],aaa[3]
cnstrtype = chardet.detect(datatmp)['encoding']

print len(tmpxxx)
print chardet.detect(datatmp)


print cnstrtype
print datatmp.decode(cnstrtype)
utf8str =  datatmp.decode(cnstrtype).encode('utf-8')

print utf8str

# f = open('000001tmp.csv','w')
# f.write(datatmp)
# print len(datatmp)
# f.close()
# print datatmp

# strtmp = '1234567829'
# print strtmp.find('2')
# def get20Lists(cids):
#     if len(cids) > 5:
#         return cids[:5],cids[5:]
# # print strtmp.rfind('2')
# nids = range(17)
# cmdnids = []
# if len(nids) > 5:
#     tmpcount = len(nids)
#     tmpendlist = nids
#     while tmpcount > 5:
#         listst,tmpendlist = get20Lists(tmpendlist)
#         cmdnids.append(listst)
#         tmpcount = len(tmpendlist)
#         if tmpcount <= 5:
#             cmdnids.append(tmpendlist)

# print cmdnids

# outstr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# print datetime.datetime.now()

