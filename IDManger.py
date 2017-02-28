#!/usr/bin/env python
#-*- coding: utf-8 -*-
#可以通过此文件读取所有股票的ID和中文名，及所在版块信息
import os
import sys
import shutil
import pinyin
import time
import copy
import chardet  #中文编码判断
import xlrd


reload(sys)
sys.setdefaultencoding( "utf-8" )


# print pinyin.get('你好')

# print pinyin.get('你好', format="strip", delimiter=" ")

# print pinyin.get('你好', format="numerical")
#中文转拼音
def getStringName(hanyu):
    #pname = pinyin.get_initial(hanyu,delimiter='').upper()
    pname = pinyin.get(hanyu, format="strip", delimiter="").lower()
    return pname
#提交数据到MySQL数据库


#获取文件名
def getFileNameFromPath(path):
    fname = os.path.splitext(os.path.split(path)[1])[0]
    return fname

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
                        linetmp.append(sheet.cell(rownum,nnumber).value.encode('utf-8'))
                codedics[linetmp[0]] = linetmp
            print len(codedics)
    return codedics

def getAllIDs(isbackID = True):
    idstmp = []
    excelfile1 = 'xlsx/2016code1.xls'
    id1s = getAllCodeID(excelfile1)
    idkeys = id1s.keys()

    if isbackID:
        for d in idkeys:
            idstmp.append(d)
        return idstmp
    else:
        return id1s

#测试
if __name__ == '__main__':
    print getAllIDs()



# aaa = getStringName('中国')
# print aaa
        
