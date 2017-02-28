#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import shutil
import chardet
import time
import xlrd
import IDManger
import MySqlTool
import urllib2
import json
import socket

class UpdataObj():
    """docstring for UpdataObj"""
    def __init__(self, mysqltool):
        self.lastNetDate = 20001010                               #最新行情更新时间
        self.lastUpdate = 20001010                                #数据库最新时间
        self.lastUpdateNetTime = 20001010                         #上次更新行情数据时间
        self.idDic = IDManger.getAllIDs(False)                    #所有股票数据ID,中文名以及所在行业名字典
        self.mysqltool = mysqltool                                #mysql操作对象

        self.sqldat = {}
        self.netdat = {}

        self.sqldatedic = {}

        self.SZDat = None

        self.initAllSQLType()
    #更新所有mysql最后的数据日期以及sqlID
    def initAllSQLType(self):
        for i in self.idDic.keys():
            outdat = self.getSqlLastData(i)
            if outdat:
                self.sqldat[outdat[2]] = [outdat[0],outdat[1]]
                sqldatetmp = self.conventStrDateToNumber(str(outdat[1]))
                self.sqldatedic[i] = sqldatetmp
            else:
                print 'initAllSQLTypeErro:%s'%(i)
            time.sleep(0.001)    #延时10毫秒进行下个数据请求
        todaynumdate = self.getNowNumberDate()
        print self.lastUpdate
        print todaynumdate
        datesx = list(self.sqldatedic.values())
        datesx.sort()
        mindate = datesx[0]
        self.lastUpdate = mindate                   #取得数据库中日期最早的一个数据日期
        if todaynumdate > self.lastUpdate:          #当当前日期比数据库晚一天以上时，获取当天股票网络数据
            self.updateAllNetDataToSQL()
            
    #当所有sql数据都比今天的日期早时，试着获取当天上证指数,以确定今天是否开盘，以及大盘最后更新日期,上证指数id：0000001
    #接口---http://api.money.126.net/data/feed/0000001%2cmoney.api
    def initSZNetData(self):
        try:  
            urlstr = "http://api.money.126.net/data/feed/0000001"+"%"+"2cmoney.api"
            print urlstr
            req = urllib2.Request(urlstr)  
            # restr.add_header('Range', 'bytes=0-20')
            resque = urllib2.urlopen(req) 
            datatmp = resque.read()
            outstr = datatmp[datatmp.find('{'):datatmp.rfind('}')+1]
            dicdat = json.loads(outstr)
            self.SZDat = dicdat.values()[0]
            nowNetDate = self.getDateFromNetDat(self.SZDat['time'])
            self.lastNetDate = self.conventStrDateToNumber(str(nowNetDate))         #获取当前最新行情时间
            print '当前最新行情时间:',self.lastNetDate
        except urllib2.URLError, e:  
            if isinstance(e.reason, socket.timeout):  
                raise MyException("There was an error: %r" % e)  
            else:  
                # reraise the original error  
                raise
    def setLastUpdate(self):
        datesx = list(self.sqldatedic.values())
        datesx.sort()
        self.lastUpdate = datesx[0]
    #获取所有网络股票数据
    def updateAllNetDataToSQL(self):
        self.initSZNetData()    #获取当前最新行情日期
        todaynumdate = self.getNowNumberDate()
        if self.lastNetDate > self.lastUpdate:    #如果网络数据比数据库新,则下载最新数据
            print '查看是否有新数据'
            if todaynumdate > self.lastNetDate:     #如果网络数据为昨天以前数据,则直接下载,比如星期六和星期天直接下载上周数据
                self.updateNetDataWithDate(self.lastUpdate,self.lastNetDate)
            elif todaynumdate == self.lastNetDate and self.getNowHour() >= 18:  #如果网络数据为今天数据，则看当前时间是否在下午6点以后
                self.updateNetDataWithDate(self.lastUpdate,self.lastNetDate)
            else:
                self.lastUpdateNetTime = todaynumdate

    def updateNetDataWithDate(self,startdate,enddate):     #通过开始日期与结束日期获取行情数据
        if enddate - startdate  == 1:    #使用直接http请求当前最新json数据,并存入数据库
            self.updateAllIDDataForToday(enddate)
        else:                            #时间大于1天，则请求多天的csv数据,并存入数据库
            erros = self.updateAllNetDataWithDate(startdate, enddate)
            if erros:
                print '更新数据错误:'
                print erros

    #csv行数据得到可用数据
    def getPriceList(self,datlines):
        prices = []
        for l in datlines:
            if len(l) < 2:  #删除最后个空行
                continue
            dtmps = l.split(',')
            dtmps[2] = 'cnName'
            prices.append(dtmps)
        tmp = list(reversed(prices))
        return tmp[:-1]
    def updateAllNetDataWithDate(self,startdate,enddate):
        erroids = []
        for d in self.idDic.keys():
            if self.sqldatedic[d] >= enddate:
                print '%s已经是最新数据'%(d)
                continue
            tidcsvdats = self.getNetDataWithDate(self.sqldatedic[d], enddate, d)
            csvdats = self.getPriceList(tidcsvdats)[1:] #删除第一行的开始日期时间,以防止与服务器重复
            sqlback = self.mysqltool.addCSVDataToSql(d, csvdats,self.idDic[d][1],self.sqldat)
            if sqlback > 100:
                print sqlback
                print 'erro ID:' + str(d)
                erroids.append(d)
                continue
            self.sqldatedic[d] = enddate
            print str(d) + '编号股票所有数据据更新完成'
        print '更新当天数据完成'
        self.setLastUpdate()
        self.lastUpdateNetTime = self.getNowNumberDate()
        self.lastNetDate = enddate
        return erroids

    def getNetDataWithDate(self,startdate, enddate,codeid):
        try:  
            urlstr = ""
            if codeid[0] == '6':
                #http://quotes.money.163.com/service/chddata.html?code=1000001&start=20170220&end=20170222
                urlstr = "http://quotes.money.163.com/service/chddata.html?code=0"+ codeid +"&start="+ str(startdate) +"&end=" + str(enddate)
            elif codeid[0] == '3' or codeid[0] == '0':
                urlstr = "http://quotes.money.163.com/service/chddata.html?code=1"+ codeid +"&start="+ str(startdate) +"&end=" + str(enddate)
            print urlstr
            req = urllib2.Request(urlstr)  
            # restr.add_header('Range', 'bytes=0-20')
            resque = urllib2.urlopen(req) 
            datatmp = resque.read()
            # cnstrtype = chardet.detect(datatmp)['encoding']
            # utf8str =  datatmp.decode(cnstrtype).encode('utf-8')
            utf8str = datatmp.replace('\r','')
            utf8dats = utf8str.split('\n')
            return utf8dats
        except urllib2.URLError, e:  
            if isinstance(e.reason, socket.timeout):  
                raise MyException("There was an error: %r" % e)  
            else:  
                # reraise the original error  
                raise

    def conventNumberToStrDate(self,number):
        dtmp = number%100
        mtmp = (number/100)%100
        ytmp = number/10000
        outstr = ''
        mstrtmp = ''
        if mtmp > 9:
            mstrtmp = str(mtmp)
        else:
            mstrtmp = '0' + str(mtmp)
        dstrtmp = ''
        if dtmp > 9:
            dstrtmp = str(dtmp)
        else:
            dstrtmp = '0' + str(dtmp)
        outstr = str(ytmp) + '-' + mstrtmp + '-' + dstrtmp
        return outstr

    def conventStrDateToNumber(self,strdate):
        strtmps = strdate.split('-')
        numtmp = int(strtmps[0])*10000 + int(strtmps[1])*100 + int(strtmps[2])
        return numtmp

    def getNowNumberDate(self):                                   #获取当前更新时间
        loctim = time.localtime()
        #time.struct_time(tm_year=2015, tm_mon=8, tm_mday=2, tm_hour=12, tm_min=16, tm_sec=47, tm_wday=6, tm_yday=214, tm_isdst=0)

        strdate = int(loctim.tm_year)*10000 + int(loctim.tm_mon)*100 + int(loctim.tm_mday)
        return strdate

    def getNowHour(self):
        loctim = time.localtime()
        return int(loctim.tm_hour)

    def getNowStrDate(self):
        loctim = time.localtime()
        #time.struct_time(tm_year=2015, tm_mon=8, tm_mday=2, tm_hour=12, tm_min=16, tm_sec=47, tm_wday=6, tm_yday=214, tm_isdst=0)
        numdattmp = self.getNowNumberDate()
        strtmp = self.conventNumberToStrDate(numdattmp)
        return strtmp

    #获取列表数组
    def getDateListWithNumber(self,number):
        dtmp = number%100
        mtmp = (number/100)%100
        ytmp = number/10000
        outlist = [ytmp,mtmp,dtmp]
        return outlist

    #获取列表样式日期
    def getDateListWithStr(self,strdate):
        numtmp = self.conventStrDateToNumber(strdate)
        return self.getDateListWithNumber(numtmp)

    #获取数据库最后一定数量的数据,tid为股票数据,使用sql运程访问
    def getSqlLastData(self,tid,tcount = 1):
        outdat = self.mysqltool.getTabDataWithCount(tid,tcount)
        #(4145L, datetime.date(2017, 2, 20), u'000001', u'\u5e73\u5b89\u94f6\u884c', 9.56, 9.58, 9.4, 9.4, 0.0, 9.39, 0.17, 1.8104, 0.5312, 8987L, 85571.0, 16414913L, 16173614L, 0L)
        return outdat

    def getNetIDWithID(self,tid):
        outid = ''
        if tid[0] == '6':
            outid = '0' + tid
        elif tid[0] == '3' or tid[0] == '0':
            outid = '1' + tid
        return outid

    def get20Lists(self,cids,splitcount = 30):
        if len(cids) > splitcount:
            return cids[:splitcount],cids[splitcount:]

    #更新当天所有股票数据的json格式，并存入数据库
    def updateAllIDDataForToday(self,enddate):
        outdic = self.getNetDatas(self.idDic.keys())
        scsdat,fclosed = updataobjtmp.conventOutDicToCSVTypeDat(outdic)
        laststrdate = self.conventNumberToStrDate(self.lastUpdate)
        sqlback = mysqltool.addOneLineTab(scsdat, self.idDic,fclosed,laststrdate)
        if sqlback < 100:
            print '更新当天数据完成'
            self.lastUpdate = enddate
            self.lastUpdateNetTime = self.getNowNumberDate()
            self.lastNetDate = enddate
        else:
            print '更新当天数据出错'
            
    def getNetDatas(self,ids):
        nids = []
        for td in ids:
            nids.append(self.getNetIDWithID(td))
        maxcount = 30   #每次请求30支股票，多的分多次每2秒请求一次
        outdic = {}
        cmdnids = []
        if len(nids) > maxcount:  #多个id同时请求时，一次请求20个
            tmpcount = len(nids)
            tmpendlist = nids
            while tmpcount > maxcount:
                listst,tmpendlist = self.get20Lists(tmpendlist,maxcount)
                cmdnids.append(listst)
                tmpcount = len(tmpendlist)
                if tmpcount <= maxcount:
                    cmdnids.append(tmpendlist)
        elif len(nids) == 1:
            return self.getNetData(ids[0])
        else:
            strnid = ''
            for nd in nids:
                strnid += nd + '%'+'2c'
            cmdnids.append(strnid)

        for cid in cmdnids:
            try:  
                urlstr = "http://api.money.126.net/data/feed/%smoney.api"%(cid)
                print urlstr
                req = urllib2.Request(urlstr)  
                # restr.add_header('Range', 'bytes=0-20')
                resque = urllib2.urlopen(req) 
                datatmp = resque.read()
                outstr = datatmp[datatmp.find('{'):datatmp.rfind('}')+1]
                dicdat = json.loads(outstr)
                # outdic[codeid] = dicdat.values()[0]
                for dkey in dicdat.keys():
                    outdic[dkey[1:]] = dicdat[dkey]
            except urllib2.URLError, e:  
                if isinstance(e.reason, socket.timeout):  
                    raise MyException("There was an error: %r" % e)  
                else:  
                    # reraise the original error  
                    raise
            time.sleep(2) #等2秒再请求第二次
        return outdic

    def getNetData(self,codeid):                               #获取网络数据,使用http接口获取
#     （新浪和腾讯用sh、sz来区分上证和深证，网易用0和1来区分）
# http://api.money.126.net/data/feed/0601398%2cmoney.api
# 二、多个股票实时查询
# http://api.money.126.net/data/feed/0601398%2c1000001%2c1000881%2cmoney.api
        try:  
            outdic = {}
            urlstr = ""
            print codeid
            if codeid[0] == '6':
                #http://api.money.126.net/data/feed/0601398%2cmoney.api #每次取一个股票的数据
                urlstr = "http://api.money.126.net/data/feed/0%s%%2cmoney.api"%(codeid)
            elif codeid[0] == '3' or codeid[0] == '0':
                urlstr = "http://api.money.126.net/data/feed/1%s%%2cmoney.api"%(codeid)
            print urlstr
            req = urllib2.Request(urlstr)  
            # restr.add_header('Range', 'bytes=0-20')
            resque = urllib2.urlopen(req) 
            datatmp = resque.read()
            outstr = datatmp[datatmp.find('{'):datatmp.rfind('}')+1]
            dicdat = json.loads(outstr.encode('utf-8'))
            outdic[codeid] = dicdat.values()[0]
            return outdic
        except urllib2.URLError, e:  
            if isinstance(e.reason, socket.timeout):  
                raise MyException("There was an error: %r" % e)  
            else:  
                # reraise the original error  
                raise


    def inputNewDateToSql(self,newdata):                    #将新数据插入数据库
        pass

    def inputNewDatesToSql(self,newdatas):                  #将一组新数据插入数据库
        for d in newdatas:
            self.inputNewDateToSql(d)
    def getDateFromNetDat(self,datstr):
        tmp1 = datstr.split(' ')
        tmp2 = tmp1[0].split('/')
        outstr = tmp2[0] + '-' + tmp2[1] + '-' + tmp2[2]
        return outstr
    def conventOutDicToCSVTypeDat(self,dicdat):             #将网络请求返回数据转为要存入数据库的数据
        outtmp = {}
        for k in dicdat.keys():
            datetmp = self.getDateFromNetDat(dicdat[k]['time'])
            #日期 股票代码    名称  收盘价 最高价 最低价 开盘价 前收盘         涨跌额     涨跌幅     换手率     成交量     成交金额    总市值 流通市值    成交笔数
            #time k          k.   price high. low.   open. yestclose    updown     percent   0        volume     turnover.  0     0.         0
            outtmp[k] = "'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'"%(str(datetmp),k,self.idDic[k][1],str(dicdat[k]['price']),str(dicdat[k]['high']),str(dicdat[k]['low']),str(dicdat[k]['open']),str(dicdat[k]['yestclose']),str(dicdat[k]['updown']),str(dicdat[k]['percent']),str(int(dicdat[k]['volume'])/10000),str(int(dicdat[k]['turnover'])/10000))
        return outtmp,str(dicdat[k]['yestclose'])

#测试
if __name__ == '__main__':
    mysqltool = MySqlTool.MySqlTool()
    updataobjtmp = UpdataObj(mysqltool)
    print '数据更新完成'
    while True:
        time.sleep(3600)    #延时1小时
        updataobjtmp.setLastUpdate()
        updataobjtmp.updateAllNetDataToSQL()

#计算相差天数
# import datetime
# d1 = datetime.datetime(2005, 2, 16)
# d2 = datetime.datetime(2004, 12, 31)
# (d1 - d2).days



