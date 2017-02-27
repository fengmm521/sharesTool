#!/usr/bin/env python
#-*- coding: utf-8 -*-
import codecs
import os,sys
import xlrd
import time
import urllib2
import socket  
import shutil 
#将所有Excel文件转为xml文件
reload(sys)
sys.setdefaultencoding( "utf-8" )
dbDir = "db"
txtCoding = 'utf-8'

class MyException(Exception):  
        pass 

def cur_file_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

#获取父目录
def GetParentPath(strPath):
    if not strPath:
        return None;
    lsPath = os.path.split(strPath);
    if lsPath[1]:
        return lsPath[0];
    lsPath = os.path.split(lsPath[0]);
    return lsPath[0];

#获取所有界面的json文件列表
def getAllExtFile(path,fromatx = ".txt"):
    jsondir = path
    jsonfilelist = []
    for root, _dirs, files in os.walk(jsondir):
        for filex in files:          
            #print filex
            name,text = os.path.splitext(filex)
            if cmp(text,fromatx) == 0:
                jsonArr = []
                rootdir = path
                dirx = root[len(rootdir):]
                pathName = dirx +os.sep + filex
                jsonArr.append(pathName)
                (newPath,_name) = os.path.split(pathName)
                jsonArr.append(newPath)
                jsonArr.append(name)
                jsonfilelist.append(jsonArr)
    return jsonfilelist

def downDBFunc(codeid,startdate,enddate):
    try:  
        urlstr = ""
        print codeid
        if codeid[0] == '6':
            #http://quotes.money.163.com/service/chddata.html?code=1000001&start=20170220&end=20170222
            urlstr = "http://quotes.money.163.com/service/chddata.html?code=0"+ codeid +"&start="+ startdate +"&end=" + enddate
        elif codeid[0] == '3' or codeid[0] == '0':
            urlstr = "http://quotes.money.163.com/service/chddata.html?code=1"+ codeid +"&start="+ startdate +"&end=" + enddate
        print urlstr
        req = urllib2.Request(urlstr)  
        # restr.add_header('Range', 'bytes=0-20')
        resque = urllib2.urlopen(req) 
        datatmp = resque.read()
        f = open(dbDir + os.sep + codeid+'.csv','w')
        f.write(datatmp)
        print len(datatmp)
        f.close()
    except urllib2.URLError, e:  
        if isinstance(e.reason, socket.timeout):  
            raise MyException("There was an error: %r" % e)  
        else:  
            # reraise the original error  
            raise
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
                    linetmp.append(sheet.cell(rownum,nnumber).value)
                codedics[linetmp[0]] = linetmp
            print len(codedics)
    return codedics
def main():
    excelfile1 = 'xlsx/2016code1.xls'
    # excelfile2 = 'xlsx/2016code2.xlsx'
    id1s = getAllCodeID(excelfile1)
    idkeys = id1s.keys()
    idkeys.sort()
    sdate = '20000101'
    edate = '20170220'
    #shutil.rmtree(dbDir)#删除目录下所有文件
    for t in idkeys:
        fname = dbDir + os.sep + t + '.csv'
        if not os.path.exists(fname):
            downDBFunc(t,sdate,edate)
            time.sleep(10)
if __name__ == '__main__':  
    main()
