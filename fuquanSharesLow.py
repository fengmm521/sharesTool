#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-02-22 09:44:42
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import codecs
import sys
import xlrd
import time
import urllib2
import socket  
import shutil 
import IDManger
import MySqlTool
import json
import DateTool
import mailTool

#将所有Excel文件转为xml文件
reload(sys)
sys.setdefaultencoding( "utf-8" )

#后复权数据下载接口
#http://img1.money.126.net/data/hs/klinederc/day/times/1002095.json


class SharesFQSelectObj():
    """docstring for SharesSelectObj"""
    def __init__(self, mysqltool):
        self.sqltool = mysqltool                        #用于向数据库请求和保存数据
        self.allIDs = IDManger.getAllIDs()              #所有股票ID

        self.mailtool = mailTool.MyEmail()

        #将要保存到数据库的最终结果
        self.count3000 = 0
        self.selOutDic = {}             #找出的3000日价位推存股票，找出的3000日距推存股票{pp:[],dp:[]},pp,dp分别满足要求的10支股票
        self.nowPrices = []             #当前股票价格
        self.sharesStartDate = ''       #股票发行日期
        self.sharesDataEndDay = ''      #股票当前前复权数据日期

        #当前正在分析的股票数据
        self.nowTID = ''                #当前正在分析的股票代码
        self.nowdic = {}                #当前分析数据字典,按日期保存的当日价格
        self.fqNowprice = 0.0           #当前不复权最近成交价格

        self.min3000 = 0                #当前分析股票的3000日历史最少值
        self.max3000 = 0                #当前分析股票的3000日历史最大值
        self.nowLowNumber = 0           #当前分析股票的最近最小值在3000日数据数组中的编号

        #今天分析的所有股票数据结果                              #[距离今天的时间比,价格最低值比,最近的最低价,最近最低价离今天的日子]
        self.today3000s = {}            #今日分析的所有股票3000日数据结果,分别是,距离今天的时间比,价格最低值比,最近的最低价,价格改变率,最近最低价离今天的日子
        self.today1000s = {}                                #今日分析的所有股票1000日数据结果
        self.today600s = {}                                 #   ...
        self.today300s = {}                                 #   ...
        self.today150s = {}                                 #   ...
        self.todayPrice = 0.0                               #今天的股票价格

        self.confilePth = 'select.conf'
        self.conf3000 = []
        self.conf1000 = []
        self.conf600 = []
        self.conf300 = []
        self.conf150 = []

        self.lastUpdate = ''            #服务器最新分析数据日期
        self.lastSelectDate = 20000101  #获取服务器推荐保存数据

    def setTodayPrice(self,price):
        self.todayPrice = price

    def initConf(self):
        f = open(self.confilePth,'r')
        tmplines = f.readlines()
        f.close()
        #读取的第0行为数据说明
        self.conf3000 = tmplines[1].split(',')[1:]      #[3000,0.001,0.01],为数据选择设置
        self.conf1000 = tmplines[2].split(',')[1:]
        self.conf600 = tmplines[3].split(',')[1:]
        self.conf300 = tmplines[4].split(',')[1:]
        self.conf150 = tmplines[5].split(',')[1:]

    #从数据库中查找最近一次的分析日期,如果最近的分析日期在昨天，则开始新的分析,否则把读取到的数据存入变量,复权数据库名:fuquaneverydayshare
    # def getLastDatFromSql(self):
    #     self.lastUpdate = DateTool.getNowStrDate()
    #     dat = self.sqltool.getLastSelectTabData()
    #     if dat:
    #         self.lastSelectDate = DateTool.conventStrDateToNumber(str(dat[0][1]))
    #         numLastUpdate = DateTool.conventStrDateToNumber(self.lastUpdate)
    #         if numLastUpdate > self.lastSelectDate:
    #             self.startTodayAnalyse()
    #     else:
    #         self.startTodayAnalyse()
    #         self.lastSelectDate = DateTool.conventStrDateToNumber(self.lastUpdate)


    def getStringForMail(self,dats):
        #['300336', 0.008841732979664015, 0.000278009452321373, 17.191666666666666, 0.019999999999999574, 10, 89.11166666666666, 17.171666666666667]
        outstr = dats[0] + ',%.6f'%(dats[1]) + ',%.6f'%(dats[2]) + ',%d'%(dats[5]) + ',%.2f'%(dats[3]) + ',(%.2f,%.2f)'%(dats[7],dats[6])
        return outstr

    #发送推荐股票邮件
    def getEmailWithFQDataStr(self):
        sendtext = '-------前复权数据分析结果---------\n'
        sendtext += '复权3000日推存:\n股票代码,时间比率,价格比率,低价日距,当前价,(历史最低,历史最高)\n'
        for x3000 in self.selOutDic[3000]:
            sendtext += self.getStringForMail(x3000) + '\n'
        sendtext += '\n复权1000日推存:\n股票代码,时间比率,价格比率,低价日距,当前价,(历史最低,历史最高)\n'
        for x1000 in self.selOutDic[1000]:
            sendtext += self.getStringForMail(x1000) + '\n'
        sendtext += '\n复权600日推荐:\n股票代码,时间比率,价格比率,低价日距,当前价,(历史最低,历史最高)\n'
        for x600 in self.selOutDic[600]:
            sendtext += self.getStringForMail(x600) + '\n\n'
        sendtext += '\n复权300日推荐:\n股票代码,时间比率,价格比率,低价日距,当前价,(历史最低,历史最高)\n'
        for x300 in self.selOutDic[300]:
            sendtext += self.getStringForMail(x300) + '\n'
        sendtext += '\n复权150日推荐:\n股票代码,时间比率,价格比率,低价日距,当前价,(历史最低,历史最高)\n'
        for x150 in self.selOutDic[150]:
            sendtext += self.getStringForMail(x150) + '\n'
        sendtext += '\n-------------------------------\n'
        return sendtext

    # #开始分析数据
    # def startTodayAnalyse(self):
    #     self.lastUpdate = DateTool.getNowStrDate()
    #     for d in self.allIDs:
    #         self.analyOneShares(d)
    #         time.sleep(0.001)
    #     self.getAllRecommendDat()
        #self.sendEmailToUser()

    #析分某支股票数据
    def analyOneShares(self,tid):
        if self.lastUpdate == '':
            self.lastUpdate = DateTool.getNowStrDate()
        self.getShareFQDatFromNet(tid)      #取出一支股票数据
        self.analyseShareDat()              #分析刚取出的股票数据
        return tid

    def getNetIDWithID(self,tid):
        outid = ''
        if tid[0] == '6':
            outid = '0' + tid
        elif tid[0] == '3' or tid[0] == '0':
            outid = '1' + tid
        return outid
    #从网络获取复权数据
    def getShareFQDatFromNet(self,tid):
        #后复权数据下载接口
        #http://img1.money.126.net/data/hs/klinederc/day/times/1002095.json
        self.nowTID = tid
        try:  
            cid = self.getNetIDWithID(tid)
            urlstr = "http://img1.money.126.net/data/hs/klinederc/day/times/%s.json"%(cid)
            # print urlstr
            req = urllib2.Request(urlstr)  
            # restr.add_header('Range', 'bytes=0-20')
            resque = urllib2.urlopen(req) 
            datatmp = resque.read()
            #{"symbol":"002095","closes":[62.8,60.0,66.0,175.69],"times":["20061215","20061218","20170303"],"name":"\u751f \u610f \u5b9d"}
            dicdat = json.loads(datatmp)
            # outdic[codeid] = dicdat.values()[0]
            dotx = 1.0
            if self.todayPrice != 0:
                dotx = self.todayPrice / dicdat['closes'][-1]
            self.nowPrices = []
            for d in dicdat['closes']:
                tmpd = d * dotx
                self.nowPrices.append(tmpd)
            # self.nowPrices = dicdat['closes']
            # self.nowPrices.append(self.todayPrice)
            self.sharesStartDate = dicdat['times'][0]
            self.sharesDataEndDay = dicdat['times'][-1]
        except urllib2.URLError, e:  
            if isinstance(e.reason, socket.timeout):  
                print '获取数据错误:getShareFQDatFromNet1'
                raise MyException("There was an error: %r" % e)  

            else:  
                print '获取数据错误:getShareFQDatFromNet2'
                # reraise the original error  
                raise
                
    #分析数据,得出分析结果并保存
    def analyseShareDat(self):
        dattmps = self.nowPrices
        self.count3000 = len(self.nowPrices)
        # self.todayPrice = dattmps[-1]
        #数据取向后的3平均值以取掉杂波
        avedats = dattmps #self.getAvDatas(dattmps, 2)           #将数据2天取一个平均值,得到一个数的数组
        xielvs3000 = self.getMinPrice(avedats)
        if not xielvs3000:
            print 'xielvs3000 empty'
            return
        self.today3000s[self.nowTID] = xielvs3000[-1]
        if self.count3000 >= 1000:
            xielvs1000 = self.getMinPrice(avedats[-1000:])
            if xielvs1000:
                self.today1000s[self.nowTID] = xielvs1000[-1]
            else:
                self.today1000s[self.nowTID] = xielvs3000[-1]
            xielvs600 = self.getMinPrice(avedats[-600:])
            if xielvs600:
                self.today600s[self.nowTID] = xielvs600[-1]
            else:
                self.today600s[self.nowTID] = xielvs3000[-1]
            xielvs300 = self.getMinPrice(avedats[-300:])
            if xielvs300:
                self.today300s[self.nowTID] = xielvs300[-1]
            else:
                self.today300s[self.nowTID] = xielvs3000[-1]
            xielvs150 = self.getMinPrice(avedats[-150:])
            if xielvs150:
                self.today150s[self.nowTID] = xielvs150[-1]
            else:
                self.today150s[self.nowTID] = xielvs3000[-1]
        else:
            self.today1000s[self.nowTID] = xielvs3000[-1]
            if self.count3000 >= 600:
                xielvs600 = self.getMinPrice(avedats[-600:])
                if xielvs600:
                    self.today600s[self.nowTID] = xielvs600[-1]
                else:
                    self.today600s[self.nowTID] = xielvs3000[-1]
                xielvs300 = self.getMinPrice(avedats[-300:])
                if xielvs300:
                    self.today300s[self.nowTID] = xielvs300[-1]
                else:
                    self.today300s[self.nowTID] = xielvs3000[-1]
                xielvs150 = self.getMinPrice(avedats[-150:])
                if xielvs150:
                    self.today150s[self.nowTID] = xielvs150[-1]
                else:
                    self.today150s[self.nowTID] = xielvs3000[-1]
            else:
                self.today600s[self.nowTID] = xielvs3000[-1]
                if self.count3000 >= 300:
                    xielvs300 = self.getMinPrice(avedats[-300:])
                    if xielvs300:
                        self.today300s[self.nowTID] = xielvs300[-1]
                    else:
                        self.today300s[self.nowTID] = xielvs3000[-1]
                    xielvs150 = self.getMinPrice(avedats[-150:])
                    if xielvs150:
                        self.today150s[self.nowTID] = xielvs150[-1]
                    else:
                        self.today150s[self.nowTID] = xielvs3000[-1]
                else:
                    self.today300s[self.nowTID] = xielvs3000[-1]
                    if self.count3000 >= 150:
                        xielvs150 = self.getMinPrice(avedats[-150:])
                        if xielvs150:
                            self.today150s[self.nowTID] = xielvs150[-1]
                        else:
                            self.today150s[self.nowTID] = xielvs3000[-1]
                    else:
                        self.today150s[self.nowTID] = xielvs3000[-1]
        self.saveOneShareResultToSql(self.nowTID)
    #从析数据中取出前满足要求的10支股票
    def getAllRecommendDat(self):
        ls3000 = []
        ls1000 = []
        ls600 = []
        ls300 = []
        ls150 = []
        for idtmp in self.today3000s.keys():
            ls3000.append([idtmp] + self.today3000s[idtmp])
        for idtmp in self.today1000s.keys():
            ls1000.append([idtmp] + self.today1000s[idtmp])
        for idtmp in self.today600s.keys():
            ls600.append([idtmp] + self.today600s[idtmp])
        for idtmp in self.today300s.keys():
            ls300.append([idtmp] + self.today300s[idtmp])
        for idtmp in self.today150s.keys():
            ls150.append([idtmp] + self.today150s[idtmp])

        #self.initConf()    #通过文件初始化分类参数,目前没有运行
        self.selOutDic = {}
        self.selOutDic[3000] = self.findItemWithDat(ls3000)
        self.selOutDic[1000] = self.findItemWithDat(ls1000)
        self.selOutDic[600] = self.findItemWithDat(ls600)
        self.selOutDic[300] = self.findItemWithDat(ls300)
        self.selOutDic[150] = self.findItemWithDat(ls150)
        self.saveAllAnalyseResultToSql()
    #保存当天分析结果的推荐股票数据存入数据库
    def saveAllAnalyseResultToSql(self):
        self.sqltool.saveTodayFQAnalyseShareToSql(self.lastUpdate, self.selOutDic)

    #找出想要的数据,只取10支当前价格最低的10支股票
    def findItemWithDat(self,datas):
        #日期排序
        # datelist = list(datas)
        # datelist.sort(key=lambda x:x[1])  #从小到大
        # datelisttmp = []
        # for num in datelist:
        #   if num[1] < maxDate and num[2] <= minPrice:
        #       datelisttmp.append(num)
        #价格排序
        pricelist = list(datas)
        pricelist.sort(key=lambda x:x[2]) 
        # dotp = 10000.0
        # co = 0
        # for p in range(len(pricelist)):
        #     tmp = pricelist[p]
        #     if tmp[5] <= 3:
        #         co += 1
        #     if co > 9:
        #         dotp = pricelist[p]
        #         break

        priceListtmp = []
        for mind in pricelist:
            if mind[2] < 0.1 and mind[5] < 3:
                priceListtmp.append(mind)
        return priceListtmp

    #保存分析的一支股票今天数据存入数据存
    def saveOneShareResultToSql(self,tid):
        datatmps = []
        datatmps.append(self.count3000);    #count3000
        datatmps.append(self.todayPrice);   #nowprice
        datatmps.append(self.today3000s[tid][1]);   #pp3000
        datatmps.append(self.today3000s[tid][0]);   #dp3000
        datatmps.append(self.today3000s[tid][5]);   #maxp3000
        datatmps.append(self.today3000s[tid][6]);   #minp3000
        datatmps.append(self.today3000s[tid][4]);   #between3000
        datatmps.append(self.today1000s[tid][1]);   #pp1000
        datatmps.append(self.today1000s[tid][0]);   #dp1000
        datatmps.append(self.today1000s[tid][5]);   #maxp1000
        datatmps.append(self.today1000s[tid][6]);   #minp1000
        datatmps.append(self.today1000s[tid][4]);   #between1000
        datatmps.append(self.today600s[tid][1]);    #pp600
        datatmps.append(self.today600s[tid][0]);    #dp600
        datatmps.append(self.today600s[tid][5]);    #maxp600
        datatmps.append(self.today600s[tid][6]);    #minp600
        datatmps.append(self.today600s[tid][4]);    #between600
        datatmps.append(self.today300s[tid][1]);    #pp300
        datatmps.append(self.today300s[tid][0]);    #dp300
        datatmps.append(self.today300s[tid][5]);    #maxp300
        datatmps.append(self.today300s[tid][6]);    #minp300
        datatmps.append(self.today300s[tid][4]);    #between300
        datatmps.append(self.today150s[tid][1]);    #pp150
        datatmps.append(self.today150s[tid][0]);    #dp150
        datatmps.append(self.today150s[tid][5]);    #maxp150
        datatmps.append(self.today150s[tid][6]);    #minp150
        datatmps.append(self.today150s[tid][4]);    #between150
        backsql = self.sqltool.updateOneShareAnalyseFQDataToSql(tid, self.lastUpdate, datatmps)
        if backsql > 100:
            print '更新股票%s分析数据到数据库出错%d'%(tid,backsql)
        # else:
            #print '更新分析%s数据到数据库完成'%(tid)
    


#数据分析工具方法
    #数组数据求平均值
    def average(self,dats):
        count = float(len(dats))
        for x in dats:
            if x == 0:
                count -= 1
        if count <= 0:
            return 0
        ave = sum(dats)/count
        return ave

    #数据平均法去杂波,取近day天数据的平均值作为当天的值，不完整数据在后边,目前默认设置为3天数据取平均值
    def getAvDatas(self,dats,day):
        count = len(dats)
        tmpdats = []
        for n in range(count):
            tmpd = 0.0
            if n <= count - day:
                tmpd = self.average(dats[n:n+day])
            else:
                tmpd = self.average(dats[n:])
            tmpdats.append(tmpd)
        return tmpdats

    #数据平均法去杂波,取近day天数据的平均值作为当天的值，不完整数据在前边,目前默认设置为3天数据取平均值
    def getAvDatasFront(self,dats,day):
        count = len(dats)
        tmpdats = []
        for n in range(count):
            if n >= day:
                tmpd = average(dats[n-day:n])
                tmpdats.append(tmpd)
        return tmpdats

    #获取数组中数值最小点位置
    def getMinPrice(self,dats):
        count = len(dats)
        dattmps = []
        zoredats = []                   #数值为0的所有数据编号
        for d in range(count):
            tmpd = dats[d]
            if tmpd > 0:    
                dattmps.append(tmpd)
            else:
                zoredats.append(d)
        if not dattmps:
            return []
        maxdat = max(dattmps)
        mindat = min(dattmps)
        xielv = []
        if maxdat == mindat:
            return []
        outs = []
        
        for n in range(len(dattmps)):
            if n > 0:
                tmpd = dattmps[n] - dattmps[n-1]
                point = (dattmps[n]-mindat)/(maxdat-mindat)
                if zoredats:
                    counttmp = 0
                    for z in zoredats:
                        if n >= z:
                            counttmp += 1
                    xielv.append([float(count - n - counttmp)/count,point,dattmps[n],tmpd,count - n - counttmp,maxdat,mindat])
                else:
                    #分别是,距离今天的时间比，价格最低值比，最近的最低价，最近最低价离今天的日子
                    xielv.append([float(count - n)/count,point,dattmps[n],tmpd,count - n,maxdat,mindat])
        
        for x in range(len(xielv)):
            if x > 0 and xielv[x-1][3] < 0 and xielv[x][3] >= 0:
                outs.append(xielv[x])
        return outs

if __name__ == '__main__':  
    #SELECT * FROM shares_dat.`000001` ORDER BY id DESC limit 3000; #降序查寻某个数据的前3000项
    mysqltool = MySqlTool.MySqlTool()
    selectfqobj = SharesFQSelectObj(mysqltool)
    selectfqobj.analyOneShares('300490')
    print '测试程序运行结束'

#创建用于保存数据分析表
# CREATE TABLE `shares_dat`.`selectshares` (
#   `shareid` VARCHAR(45) NOT NULL,
#   `date` DATE NOT NULL DEFAULT '2017-03-03',
#   `count3000` INT NULL DEFAULT 0,
#   `nowprice` FLOAT NULL DEFAULT 0.0,
#   `pp3000` DOUBLE NULL DEFAULT 1.0,
#   `dp3000` DOUBLE NULL DEFAULT 1.0,
#   `maxp3000` FLOAT NULL DEFAULT 0.0,
#   `minp3000` FLOAT NULL DEFAULT 0.0,
#   `between3000` INT NULL DEFAULT 3000,
#   `pp1000` DOUBLE NULL DEFAULT 0.0,
#   `dp1000` DOUBLE NULL DEFAULT 0.0,
#   `maxp1000` FLOAT NULL DEFAULT 0.0,
#   `minp1000` FLOAT NULL DEFAULT 0.0,
#   `between1000` INT NULL DEFAULT 1000,
#   `pp600` DOUBLE NULL DEFAULT 0.0,
#   `dp600` DOUBLE NULL DEFAULT 0.0,
#   `maxp600` FLOAT NULL DEFAULT 0.0,
#   `minp600` FLOAT NULL DEFAULT 0.0,
#   `between600` INT NULL DEFAULT 600,
#   `pp150` DOUBLE NULL DEFAULT 0.0,
#   `dp150` DOUBLE NULL DEFAULT 0.0,
#   `maxp150` FLOAT NULL DEFAULT 0.0,
#   `minp150` FLOAT NULL DEFAULT 0.0,
#   `between150` INT NULL DEFAULT 150,
#   PRIMARY KEY (`shareid`),
#   UNIQUE INDEX `shareid_UNIQUE` (`shareid` ASC));

#保存每日推荐的数据
# CREATE TABLE `shares_dat`.`everydayshare` (
#   `id` INT NOT NULL AUTO_INCREMENT COMMENT '方便统计的数据库ID',
#   `date` DATE NOT NULL COMMENT '推荐日期',
#   `sharetext` TEXT(65000) NULL DEFAULT NULL COMMENT '用来保存每日推荐股票的3000,1000,600,300,150等股票id和参考数据',
#   PRIMARY KEY (`id`, `date`),
#   UNIQUE INDEX `id_UNIQUE` (`id` ASC),
#   UNIQUE INDEX `date_UNIQUE` (`date` ASC));

