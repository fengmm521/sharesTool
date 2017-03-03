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

import IDManger

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



# a = [2,4,1,8,3,2,3,5,0,0]
# a.sort()
# print a
# a.remove(0)
# a.remove(0)
# print a

#INSERT INTO `shares_dat`.`selectshares` (`shareid`, `date`) VALUES (000001', '2017-03-02');
# outsrt = ''
# ids = IDManger.getAllIDs()
# for d in ids:
#     outsrt += "INSERT INTO `shares_dat`.`selectshares` (`shareid`, `date`) VALUES ('%s', '2017-03-02');\n"%(d)
# print outsrt

# strtmp = "`date`='%s', `count3000`='%d', `nowprice`='%.2f', `pp3000`='%.6f', `dp3000`='%.6f', `maxp3000`='%.2f', `minp3000`='%.2f', `between3000`='%d', `pp1000`='%.6f', `dp1000`='%.6f', `maxp1000`='%.2f', `minp1000`='%.2f', `between1000`='%d', `pp600`='%.6f', `dp600`='%.6f', `maxp600`='%.2f', `minp600`='%.2f', `between600`='%d', `pp300`='%.6f', `dp300`='%.6f', `maxp300`='%.2f', `minp300`='%.2f', `between300`='%d', `pp150`='%.6f', `dp150`='%.6f', `maxp150`='%.2f', `minp150`='%.2f', `between150`='%d' WHERE `shareid`='%s'"

# # a = strtmp.split(',')
# # print len(a)
# # for x in a:
#     print x
# import MySqlTool
# sqltool = MySqlTool.MySqlTool()
# dat = sqltool.getLastSelectTabData()
# print dat

a = '2017-03-04'
ds = a.split('-')
print int(ds[0])
print int(ds[1])
# outstr = ''
# for d in range(27):
#     outstr += "datas[%d],"%(d)
# print outstr
# urlstr = "http://quotes.money.163.com/service/chddata.html?code=1002752&start=20170220&end=20170228"
# req = urllib2.Request(urlstr)  
# # restr.add_header('Range', 'bytes=0-20')
# resque = urllib2.urlopen(req) 

# datatmp = resque.read()

# tmpxxx = datatmp.split('\n')
# aaa = tmpxxx[2].split(',')
# print aaa[0],aaa[1],aaa[3]
# cnstrtype = chardet.detect(datatmp)['encoding']

# print len(tmpxxx)
# print chardet.detect(datatmp)


# print cnstrtype
# print datatmp.decode(cnstrtype)
# utf8str =  datatmp.decode(cnstrtype).encode('utf-8')

# print utf8str

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

