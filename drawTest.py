#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import urllib2
import json
import IDManger
import DateTool
import time
import numpy as np
import matplotlib.pyplot as plt
# plt.figure(1) # 创建图表1
# plt.figure(2) # 创建图表2
# ax1 = plt.subplot(211) # 在图表2中创建子图1
# ax2 = plt.subplot(212) # 在图表2中创建子图2
class DrawObj(object):
    """docstring for DrawObj"""
    def __init__(self):

        self.nowTID = ''

        self.outjpgpth = 'drawout'

        self.nowPrices = []
        self.timesDats = []

        self.todayPrice = 0

        self.dwarCount = 1000
    
    def getNetIDWithID(self,tid):
        outid = ''
        if tid[0] == '6':
            outid = '0' + tid
        elif tid[0] == '3' or tid[0] == '0':
            outid = '1' + tid
        return outid

    #从网络获取复权数据
    def getDrawDataFromNet(self,tid):
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
            for t in dicdat['times']:
                self.timesDats.append(t)
            self.drawWithPlt()
        except urllib2.URLError, e:  
            if isinstance(e.reason, socket.timeout):  
                print '获取数据错误:getShareFQDatFromNet1'
                raise MyException("There was an error: %r" % e)  
            else:  
                print '获取数据错误:getShareFQDatFromNet2'
                # reraise the original error  
                raise
    def drawWithPlt(self):
        drawdats = []
        starttime = ''
        endtime = ''
        if len(self.nowPrices) > self.dwarCount:
            drawdats = self.nowPrices[-self.dwarCount:]
            starttime = self.timesDats[-self.dwarCount]
            endtime = self.timesDats[-1]
        else:
            drawdats = self.nowPrices
            starttime = self.timesDats[0]
            endtime = self.timesDats[-1]
        xs = range(len(drawdats))
        ys = drawdats
        plt.figure() # 创建图表1
        plt.plot(xs, ys)

        #绘制标注
        xslen = len(drawdats)
        bzxx = [xs[0],xs[int(xslen*0.2)],xs[int(xslen*0.4)],xs[int(xslen*0.6)],xs[int(xslen*0.8)],xs[int(xslen-1)]]
        for bx in bzxx:
            plt.text(bx,drawdats[bx],self.timesDats[-self.dwarCount:][bx],color='red',fontsize=10)
        xlab = '%s~%s'%(DateTool.conventNumberToStrDate(int(starttime)),DateTool.conventNumberToStrDate(int(endtime)))
        tmpname = xlab
        showxlab = xlab + ',count=%d'%(xslen)
        title = '%s'%(self.nowTID)
        plt.xlabel(showxlab)  
        plt.ylabel("back fu quan")  
        plt.title(title) 
        #plt.show()
        dirname = 'out1000'
        if xslen > 800:
            dirname = 'out1000'
        elif xslen <=800 and xslen > 600:
            dirname = 'out800'
        elif xslen <=600 and xslen > 300:
            dirname = 'out600'
        elif xslen <=300 and xslen > 100:
            dirname = 'out300'
        elif xslen <=100:
            dirname = 'out100'
            
        fname = self.outjpgpth + os.sep + dirname + os.sep +'%s(%s).jpg'%(title,tmpname)
        plt.savefig(fname)

if __name__ == '__main__':  
    #SELECT * FROM shares_dat.`000001` ORDER BY id DESC limit 3000; #降序查寻某个数据的前3000项
    drawobj = DrawObj()
    allids = IDManger.getAllIDs()
    count = 0
    for i in allids:
        drawobj.getDrawDataFromNet(i)
        time.sleep(0.01)
        count += 1
        if count%10 == 0:
            print "tid=%s,dowoncount:%d"%(i,count)
    print '测试程序运行结束'

# for i in xrange(5):
#     plt.figure(1)  #❶ # 选择图表1
#     plt.plot(x, np.exp(i*x/3))
#     plt.sca(ax1)   #❷ # 选择图表2的子图1
#     plt.plot(x, np.sin(i*x))
#     plt.sca(ax2)  # 选择图表2的子图2
#     plt.plot(x, np.cos(i*x))
# plt.show()

