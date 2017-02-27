#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import time
import datetime
import shutil 
import xlrd
import urllib2

updateDir = 'updatedate'

def getNowDate():
    loctim = time.localtime()
    #time.struct_time(tm_year=2015, tm_mon=8, tm_mday=2, tm_hour=12, tm_min=16, tm_sec=47, tm_wday=6, tm_yday=214, tm_isdst=0)
    strdate = [int(loctim.tm_year),int(loctim.tm_mon),int(loctim.tm_mday)]
    return strdate
def getTime():
    loctim = time.localtime()
    return int(loctim.tm_hour)

def datetime2timestamp(dt, convert_to_utc=False):
    ''' Converts a datetime object to UNIX timestamp in milliseconds. '''
    if isinstance(dt, datetime.datetime):
        if convert_to_utc: # 是否转化为UTC时间
            dt = dt + datetime.timedelta(hours=-8) # 中国默认时区
        timestamp = datetime.timedelta.total_seconds(dt - datetime.datetime(1970,1,1))
        return long(timestamp)
    return dt

def getDataStartEndDate():
    f = open('dateConfig.conf','r')
    dat = f.read()
    f.close()
    startdate = [0,0,0]
    enddate = [0,0,0]
    tmpdat = dat.split(',')

    starttmp = tmpdat[0].split('-')
    startdate[0] = int(starttmp[0])
    startdate[1] = int(starttmp[1])
    startdate[2] = int(starttmp[2])

    endtmp = tmpdat[1].split('-')
    enddate[0] = int(endtmp[0])
    enddate[1] = int(endtmp[1])
    enddate[2] = int(endtmp[2])

    # print tmpdat[0]
    # time1 = datetime.datetime.strptime(tmpdat[0],'%Y-%m-%d')
    # print time1
    # print datetime2timestamp(time1)

    return startdate,enddate

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
        enddateDir = updateDir + os.sep + enddate
        f = open(enddateDir + os.sep + codeid+'.csv','w')
        f.write(datatmp)
        print len(datatmp)
        f.close()
    except urllib2.URLError, e:  
        if isinstance(e.reason, socket.timeout):  
            raise MyException("There was an error: %r" % e)  
        else:  
            # reraise the original error  
            raise

def getstrDate(dats):
    outstr = str(dats[0])
    if dats[1] > 9:
        outstr += str(dats[1])
    else:
        outstr += '0' + str(dats[1])
    if dats[2] > 9:
        outstr += str(dats[2])
    else:
        outstr += '0' + str(dats[2])
    return outstr

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

def updateAllData(startdate,enddate):
    excelfile1 = 'xlsx/2016code1.xls'
    # excelfile2 = 'xlsx/2016code2.xlsx'
    id1s = getAllCodeID(excelfile1)
    idkeys = id1s.keys()
    idkeys.sort()
    sdate = startdate
    edate = enddate
    enddateDir = updateDir + os.sep + enddate
    if not os.path.exists(updateDir):
        os.mkdir(updateDir)
    if os.path.exists(enddateDir):
        shutil.rmtree(enddateDir)
    os.mkdir(enddateDir)
    for t in idkeys:
        fname = enddateDir + os.sep + t + '.csv'
        if not os.path.exists(fname):
            downDBFunc(t,sdate,edate)
            time.sleep(1)

def getUpdateDate():
    sedates = getDataStartEndDate()#([2000, 1, 1], [2017, 2, 20])
    ndate = getNowDate()

    startdate = sedates[1]
    enddate = ndate

    if startdate[0] == enddate[0] and startdate[1] == enddate[1] and startdate[2] == enddate[2]:
        return
    else:
        startstr = getstrDate(startdate)
        endstr = getstrDate(enddate)
        updateAllData(startstr, endstr)


def main():
    getUpdateDate()
    print '数据已更新为最新'
if __name__ == '__main__':  
    main()