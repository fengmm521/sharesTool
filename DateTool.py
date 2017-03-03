#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import time

#日期转换工具
def conventNumberToStrDate(number):
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

def conventStrDateToNumber(strdate):
    strtmps = strdate.split('-')
    numtmp = int(strtmps[0])*10000 + int(strtmps[1])*100 + int(strtmps[2])
    return numtmp
def getNowNumberDate():                                   #获取当前更新时间
    loctim = time.localtime()
    #time.struct_time(tm_year=2015, tm_mon=8, tm_mday=2, tm_hour=12, tm_min=16, tm_sec=47, tm_wday=6, tm_yday=214, tm_isdst=0)
    strdate = int(loctim.tm_year)*10000 + int(loctim.tm_mon)*100 + int(loctim.tm_mday)
    return strdate
def getNowHour():
    loctim = time.localtime()
    return int(loctim.tm_hour)
def getNowStrDate():
    loctim = time.localtime()
    #time.struct_time(tm_year=2015, tm_mon=8, tm_mday=2, tm_hour=12, tm_min=16, tm_sec=47, tm_wday=6, tm_yday=214, tm_isdst=0)
    numdattmp = getNowNumberDate()
    strtmp = conventNumberToStrDate(numdattmp)
    return strtmp
#获取列表数组
def getDateListWithNumber(number):
    dtmp = number%100
    mtmp = (number/100)%100
    ytmp = number/10000
    outlist = [ytmp,mtmp,dtmp]
    return outlist
#获取列表样式日期
def getDateListWithStr(strdate):
    numtmp = conventStrDateToNumber(strdate)
    return getDateListWithNumber(numtmp)

#测试
if __name__ == '__main__':
    print '日期数据转换工具'




