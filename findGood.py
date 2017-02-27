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
#将所有Excel文件转为xml文件
reload(sys)
sys.setdefaultencoding( "utf-8" )

dbDir = "db"
outDir = 'out'

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

def getAllCSVFile():
	cvsfiles = []
	tmpcvs = getAllExtFile(dbDir,'.csv')
	for d in tmpcvs:
		tmpph = dbDir + d[0]
		cvsfiles.append(tmpph)
	return cvsfiles

#获取文件名
def getFileNameFromPath(path):
	fname = os.path.splitext(os.path.split(path)[1])[0]
	return fname

#获取价格数据
def getPriceList(datlines):
	prices = []
	for l in datlines:
		dtmps = l.split(',')
		prices.append(dtmps[3:11])
	tmp = list(reversed(prices))
	return tmp[:-1]

#数组求平均值
def average(dats):
	count = float(len(dats))
	for x in dats:
		if x == 0:
			count -= 1
	ave = sum(dats)/count
	return ave

#数据平均法去杂波,取近5天数据的平均值作为当天的值，不完整数据在后边
def getAvDatas(dats,day):
	count = len(dats)
	tmpdats = []
	for n in range(count):
		tmpd = 0.0
		if n <= count - day:
			tmpd = average(dats[n:n+day])
		else:
			tmpd = average(dats[n:])
		tmpdats.append(tmpd)
	return tmpdats

#数据平均法去杂波,取近5天数据的平均值作为当天的值，不完整数据在前边
def getAvDatasFront(dats,day):
	count = len(dats)
	tmpdats = []
	for n in range(count):
		if n >= day:
			tmpd = average(dats[n-day:n])
			tmpdats.append(tmpd)
	return tmpdats

#获取数组中数值最小点位置
def getMinPrice(dats):
	count = len(dats)
	maxdat = max(dats)
	mindat = min(dats)
	xielv = []
	if maxdat == mindat:
		return []
	for n in range(count):
		if n > 0:
			tmpd = dats[n] - dats[n-1]
			point = (dats[n]-mindat)/(maxdat-mindat)
			xielv.append([float(n)/count,point,dats[n],tmpd])
	outs = []
	for x in range(len(xielv)):
		if x > 0 and xielv[x-1][3] < 0 and xielv[x][3] >= 0:
			outs.append(xielv[x])
	return outs

#开盘价与收盘价取均值，即(开盘价+收盘价)/2
def oneDayData(dats):
	tmp = -1.0
	if dats and dats[3] > 0 and dats[0] > 0:
		tmp = (float(dats[0]) + float(dats[3]))/2.0
	if tmp > 0:
		return tmp
	return -1.0;

#收盘价	最高价	最低价	开盘价	前收盘	涨跌额	涨跌幅	换手率
#反回日数据的开盘价与收盘价的中间值列表
def AnalysisData(path):
	f = open(path,'r')
	datlines = f.readlines()
	f.close()
	prices = getPriceList(datlines)
	avprices = []
	for p in prices:
		avprices.append(oneDayData(p))
	return avprices

#找出价格已达最低股票
def findGoodItemlastCount(counts):
	ids = getAllCSVFile()
	dics = {}
	for xc in counts:
		dics[xc] = []
	for d in ids:
		dats = AnalysisData(d)
		tmpid = getFileNameFromPath(d)
		for c in counts:
			tmpdic = []
			fcount = -c
			if fcount == 0:
				if len(dats) <= 900:
					continue
				avdats = getAvDatasFront(dats, 5)
				xielvs = getMinPrice(avdats)
				if xielvs:
					tmpdic = [tmpid] + xielvs[-1] 
			else:
				if len(dats) < 3*c:
					continue
				avdats = getAvDatasFront(dats[fcount:], 5)
				xielvs = getMinPrice(avdats)
				if xielvs:
					tmpdic = [tmpid] + xielvs[-1]
			if tmpdic:
				dics[c].append(tmpdic)

	return dics

def printLinesList(dats):
	for d in dats:
		print d


def saveListToFileWithLines(dats,path):
	outstr = path + '\n'
	for d in dats:
		outstr += str(d) + '\n'
	f = open(path,'w')
	f.write(outstr)
	f.close()

def findItemWithDat(datdics,maxNumber = 0.98,minDatp = 0.05):
	finds = []
	dattmps = []
	for d in datdics:
		if d[3] > 0:
			dattmps.append(d)
	numlist = list(dattmps)
	numlist.sort(key=lambda x:x[1],reverse=True) 
	numlisttmp = []
	for num in numlist:
		if num[1] > maxNumber and num[2] <= minDatp:
			numlisttmp.append(num)
	mindatlist = list(dattmps)
	mindatlist.sort(key=lambda x:x[2]) 
	mindattmp = []
	for mind in mindatlist:
		if mind[1] > maxNumber and mind[2] <= minDatp:
			mindattmp.append(mind)
	return numlisttmp,mindattmp
def main():
	if os.path.exists(outDir):
		shutil.rmtree(outDir)#删除目录下所有文件
	os.mkdir(outDir)
	countlist = [0,600,150]
	items = findGoodItemlastCount(countlist)
	for k in items.keys():
		if k == 0 or k > 1000:
			numlist,mindatlist = findItemWithDat(items[k],0.99,0.01)
			saveListToFileWithLines(numlist, outDir + os.sep + str(k) + '_numlist.logdat')
			saveListToFileWithLines(mindatlist, outDir + os.sep + str(k) + '_mindats.logdat')
		elif k > 0 and k <= 600:
			numlist,mindatlist = findItemWithDat(items[k],0.98,0.02)
			saveListToFileWithLines(numlist, outDir + os.sep + str(k) + '_numlist.logdat')
			saveListToFileWithLines(mindatlist, outDir + os.sep + str(k) + '_mindats.logdat')
		elif k > 600 and k <= 1000:
			numlist,mindatlist = findItemWithDat(items[k],0.985,0.015)
			saveListToFileWithLines(numlist, outDir + os.sep + str(k) + '_numlist.logdat')
			saveListToFileWithLines(mindatlist, outDir + os.sep + str(k) + '_mindats.logdat')
	print '分析数据完成'
if __name__ == '__main__':  
	main()
