#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import shutil
import mysqlobj
import pinyin
import time
import copy
import chardet  #中文编码判断
import xlrd


reload(sys)
sys.setdefaultencoding( "utf-8" )

dbDir = "db"

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

# print pinyin.get('你好')

# print pinyin.get('你好', format="strip", delimiter=" ")

# print pinyin.get('你好', format="numerical")
#中文转拼音
def getStringName(hanyu):
    #pname = pinyin.get_initial(hanyu,delimiter='').upper()
    pname = pinyin.get(hanyu, format="strip", delimiter="").lower()
    return pname
#提交数据到MySQL数据库
class MySqlDataTool():
    def __init__(self,addr = 'test',port = 3306,usname = 'root',uspw = 'dddd',defDB = 'shares_dat'):#root,7668150My00
        self.sqlobj = mysqlobj.mysqlobj(addr,port,usname,uspw,defDB)
        print '连接数据库'
    #创建所有股票数据表
    def createAllIDsTab(self,ids):
        pass
    #创建一个数据表
    def createOneTab(self,tabID):
        sqlcmd = '''CREATE TABLE `shares_dat`.`%s` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '计算Key值',
  `date` DATE NOT NULL COMMENT '日期',
  `codeid` VARCHAR(45) NULL COMMENT '股票代码',
  `name` VARCHAR(45) NULL COMMENT '名称',
  `close` FLOAT NOT NULL DEFAULT 0.0 COMMENT '收盘价',
  `high` FLOAT NOT NULL DEFAULT 0.0 COMMENT '最高价',
  `low` FLOAT NOT NULL DEFAULT 0.0 COMMENT '最低价',
  `open` FLOAT NOT NULL DEFAULT 0.0 COMMENT '开盘价',
  `tomorrow` FLOAT NOT NULL DEFAULT 0.0 COMMENT '明日价格',
  `fclose` FLOAT NOT NULL DEFAULT 0.0 COMMENT '前收盘价',
  `updown` FLOAT NOT NULL DEFAULT 0.0 COMMENT '涨跌额',
  `percent` FLOAT NOT NULL DEFAULT 0.0 COMMENT '涨跌幅度',
  `change` FLOAT NOT NULL DEFAULT 0.0 COMMENT '换手率',
  `tradecount` INT(64) NOT NULL DEFAULT 0 COMMENT '成交量',
  `trade` DOUBLE NOT NULL DEFAULT 0.0 COMMENT '成交金额',
  `market` INT(64) NOT NULL DEFAULT 0 COMMENT '总市值',
  `movemarket` INT(64) NOT NULL DEFAULT 0 COMMENT '流通市值',
  `tradegroup` INT NOT NULL DEFAULT 0 COMMENT '成交笔数',
  PRIMARY KEY (`id`, `date`),
  UNIQUE INDEX `date_UNIQUE` (`date` ASC));
        '''%(tabID)
        backstr = self.sqlobj.execute(sqlcmd)
        return backstr

    #删除某个日期之前的数据
    def delDataWithDate(self,tabID,tdate):
        pass

    #修改某个日期的数据
    def changeOneLineTab(self,tabID,tdate):
        pass
        #查找id最小的数据
        #select * from shares_dat.`000002` order by id asc limit 1
        sqlcmd = "select * from shares_dat.`000002` order by id asc limit 1;"
        backstr = self.sqlobj.execute(sqlcmd)
        return backstr

    #获取一个日期之前后的数据
    def getTabDataWithDate(self,tabID,tdate):
        #查找id最小的数据
        #select * from shares_dat.`000002` order by id asc limit 1
        sqlcmd = "select * from shares_dat.`000002` order by id asc limit 1;"
        backstr = self.sqlobj.execute(sqlcmd)
        if int(backstr) < 100:
            return self.sqlobj.getOneDat()
        else:
            None

    #获取最近一定数量的数据
    def getTabDateWithCount(self,tabID,tcount):
        pass

    #获取最近一定数量的所有股票数据
    def getAllTabDataWithCount(self,tcount):
        pass

    #保存CSV数据到数据库,数据库列值使用CSV表头的中文拼音
    def saveCSVDataToSql(self,tabID,csvDatas,cname):
        print 'xxx'
        backtype = 0
        for d in csvDatas:#每行数据
            sqlcmd = 'INSERT INTO `shares_dat`.`%s` (`date`, `codeid`, `name`, `close`, `high`, `low`, `open`, `fclose`, `updown`, `percent`, `change`, `tradecount`, `trade`, `market`, `movemarket`) VALUES ('%(tabID)
            valuestr = ''
            listtmp = d[:-1]
            if listtmp[0] == 'None':
                continue
            for n in range(len(listtmp)):#每行数据中的数据项
                item = listtmp[n]
                if n > 0 and item == 'None':
                    valuestr += "'0',"
                elif n == 2:
                    valuestr += "'" + cname + "',"
                elif n < len(listtmp) - 4:
                    if item[0] == "'":
                        valuestr += str(item) + "',"
                    else:
                        valuestr += "'" + str(item) + "',"
                else:
                    valuestr += "'" + str(int(float(item)/10000)) + "',"
            sqlcmd += valuestr[:-1] + ");"
            backstr = self.sqlobj.execute(sqlcmd)
            if backstr != 0:
                backtype = backstr
        return backtype
    #为数据表填加数据
    def addOneLineTab(self,tabID,tdata):
        #INSERT INTO `shares_dat`.`000001` (`id`, `date`, `codeid`, `name`, `close`, `high`, `low`, `open`, `fclose`, `updown`, `percent`, `change`, `tradecount`, `trade`, `market`, `movemarket`) VALUES ('1', '2000-01-01', '000001', '深发展A', '18.29', '18.55', '17.2', '17.5', '17.45', '0.84', '4.81', '0.7667', '8216086', '147325356.78', '28383283312.7', '19600193797.9');
        #INSERT INTO `shares_dat`.`000001` (`id`, `date`, `codeid`, `name`, `close`, `high`, `low`, `open`, `fclose`, `updown`, `percent`, `change`, `tradecount`, `trade`, `market`, `movemarket`) VALUES ('2', '2000-01-05', '000001', '深发展A', '18.06', '18.85', '18', '18.35', '18.29', '-0.23', '-1.2575', '0.8771', '9399315', '173475158.81', '28026358481.5', '19353717878');
        pass

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
        prices.append(dtmps)
    tmp = list(reversed(prices))
    return tmp[:-1]

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


#日期 股票代码 名称  收盘价 最高价 最低价 开盘价 前收盘 涨跌额 涨跌幅 换手率 成交量 成交金额  总市值 流通市值 成交笔数
#反回日数据列数组
def AnalysisData(path):
    f = open(path,'r')
    datlines = f.readlines()
    f.close()
    prices = getPriceList(datlines)
    cnstrtype = chardet.detect(datlines[0])
    return prices,cnstrtype['encoding']

#提交所有股票数据
def updateDataToSql():
    #股票中文名
    excelfile1 = 'xlsx/2016code1.xls'
    id1s = getAllCodeID(excelfile1)
    idkeys = id1s.keys()

    sqltool = MySqlDataTool()
    ids = getAllCSVFile()

    outstr = ''

    for d in ids:
        tmpid = getFileNameFromPath(d)
        outstr += "call updateTom('%s');"%(tmpid) + '\n'

    f = open('updateother.sql','w')
    f.write(outstr)
    f.close()
    print outstr
#测试
if __name__ == '__main__':
    updateDataToSql()



# aaa = getStringName('中国')
# print aaa
        
