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
import commitDatToSql



#为所有股票创建mysql数据表
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


#找出所有股票代码
def findAllSharesID():
    ids = getAllCSVFile()
    allids = []
    for d in ids:
        tmpid = getFileNameFromPath(d)
        allids.append(tmpid)
    return allids

def printLinesList(dats):
    for d in dats:
        print d

#为每中股票创建数据表
def createTabsWithIDs(dats):
    mysqtool = commitDatToSql.MySqlDataTool()
    for d in dats:
        backstr = mysqtool.createOneTab(d)
        print '创建数据表:'+d+'返回结果:' + str(backstr)
        time.sleep(0.001)

def main():
    
    aids = findAllSharesID()
    createTabsWithIDs(aids)
    print '数据表创建完成'
if __name__ == '__main__':  
    main()
