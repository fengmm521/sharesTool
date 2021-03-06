#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import mysqlobj
import json


reload(sys)
sys.setdefaultencoding( "utf-8" )

#提交数据到MySQL数据库
class MySqlTool():
    def __init__(self,addr = '127.0.0.1',port = 3306,usname = 'root',uspw = 'password',defDB = 'test'):#root,abc7668150My00321
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

    #修改某个日期的
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
    def getTabDataWithCount(self,tid,tcount = 1):
        if tcount == 1:
            sqlcmd = "SELECT * FROM shares_dat.`%s` where id=(select max(id) from shares_dat.`%s`);"%(tid,tid)
            backstr = self.sqlobj.execute(sqlcmd)
            if backstr <= 100:
                return self.sqlobj.getOneDat()
            else:
                return None
        else:
            sqlcmd = "SELECT * FROM shares_dat.`%s` where id>(select max(id) from shares_dat.`%s`)-%d;"%(tid,tid,tcount)
            backstr = self.sqlobj.execute(sqlcmd)
            if backstr <= 100:
                return self.sqlobj.getAllDat()
            else:
                return None

    #获取最近一定数量的所有股票数据
    def getTabDataWithIDAndCount(self,tid,tcount):
        sqlcmd = "SELECT * FROM shares_dat.`%s` ORDER BY id DESC limit %d;"%(tid,tcount)
        backstr = self.sqlobj.execute(sqlcmd)
        if backstr > 0 and backstr <= tcount:
            return self.sqlobj.getAllDat()
        else:
            return None
    
    #取一个最近的推荐数据
    def getLastSelectTabData(self):
        sqlcmd = "SELECT * FROM shares_dat.everydayshare ORDER BY id DESC limit 1;"
        backstr = self.sqlobj.execute(sqlcmd)
        if backstr > 0:
            return self.sqlobj.getAllDat()
        else:
            return None

    def updateOneShareAnalyseDataToSql(self,tid,tdate,datas):
        #UPDATE `shares_dat`.`selectshares` SET `count3000`='3000', `nowprice`='1.0', `pp3000`='0.1', `dp3000`='0.2', `maxp3000`='10.0', `minp3000`='1.0', `pp1000`='0.2', `dp1000`='0.3', `maxp1000`='9.0', `minp1000`='2.0', `pp600`='0.3', `dp600`='0.4', `maxp600`='8.0', `minp600`='3.0', `pp300`='0.5', `dp300`='0.621', `maxp300`='7.9', `minp300`='3.8', `pp150`='0.61', `dp150`='0.412', `maxp150`='8.3', `minp150`='3.2' WHERE `id`='2' and`shareid`='000099';
        sqlcmd = "UPDATE `shares_dat`.`selectshares` SET `date`='%s', `count3000`='%d', `nowprice`='%.2f', `pp3000`='%.6f', `dp3000`='%.6f', `maxp3000`='%.2f', `minp3000`='%.2f', `between3000`='%d', `pp1000`='%.6f', `dp1000`='%.6f', `maxp1000`='%.2f', `minp1000`='%.2f', `between1000`='%d', `pp600`='%.6f', `dp600`='%.6f', `maxp600`='%.2f', `minp600`='%.2f', `between600`='%d', `pp300`='%.6f', `dp300`='%.6f', `maxp300`='%.2f', `minp300`='%.2f', `between300`='%d', `pp150`='%.6f', `dp150`='%.6f', `maxp150`='%.2f', `minp150`='%.2f', `between150`='%d' WHERE `shareid`='%s';"%(tdate,datas[0],datas[1],datas[2],datas[3],datas[4],datas[5],datas[6],datas[7],datas[8],datas[9],datas[10],datas[11],datas[12],datas[13],datas[14],datas[15],datas[16],datas[17],datas[18],datas[19],datas[20],datas[21],datas[22],datas[23],datas[24],datas[25],datas[26],tid)
        backsql = 0
        backstr = self.sqlobj.execute(sqlcmd)
        if backstr != 0:
            backsql = backstr
        return backsql
    #保存一组前复权数据到数据库
    def updateOneShareAnalyseFQDataToSql(self,tid,tdate,datas):
        #UPDATE `shares_dat`.`selectshares` SET `count3000`='3000', `nowprice`='1.0', `pp3000`='0.1', `dp3000`='0.2', `maxp3000`='10.0', `minp3000`='1.0', `pp1000`='0.2', `dp1000`='0.3', `maxp1000`='9.0', `minp1000`='2.0', `pp600`='0.3', `dp600`='0.4', `maxp600`='8.0', `minp600`='3.0', `pp300`='0.5', `dp300`='0.621', `maxp300`='7.9', `minp300`='3.8', `pp150`='0.61', `dp150`='0.412', `maxp150`='8.3', `minp150`='3.2' WHERE `id`='2' and`shareid`='000099';
        sqlcmd = "UPDATE `shares_dat`.`fuquanselectshares` SET `date`='%s', `count3000`='%d', `nowprice`='%.2f', `pp3000`='%.6f', `dp3000`='%.6f', `maxp3000`='%.2f', `minp3000`='%.2f', `between3000`='%d', `pp1000`='%.6f', `dp1000`='%.6f', `maxp1000`='%.2f', `minp1000`='%.2f', `between1000`='%d', `pp600`='%.6f', `dp600`='%.6f', `maxp600`='%.2f', `minp600`='%.2f', `between600`='%d', `pp300`='%.6f', `dp300`='%.6f', `maxp300`='%.2f', `minp300`='%.2f', `between300`='%d', `pp150`='%.6f', `dp150`='%.6f', `maxp150`='%.2f', `minp150`='%.2f', `between150`='%d' WHERE `shareid`='%s';"%(tdate,datas[0],datas[1],datas[2],datas[3],datas[4],datas[5],datas[6],datas[7],datas[8],datas[9],datas[10],datas[11],datas[12],datas[13],datas[14],datas[15],datas[16],datas[17],datas[18],datas[19],datas[20],datas[21],datas[22],datas[23],datas[24],datas[25],datas[26],tid)
        backsql = 0
        backstr = self.sqlobj.execute(sqlcmd)
        if backstr != 0:
            backsql = backstr
        return backsql

    #保存今日分析推存数据到数据库
    def saveTodayAnalyseShareToSql(self,tdate,datadic):
        #INSERT INTO `shares_dat`.`everydayshare` (`date`, `sharetext`) VALUES ('2017-03-03', 'aaa');
        outjson = json.dumps(datadic)
        sqlcmd = "INSERT INTO `shares_dat`.`everydayshare` (`date`, `sharetext`) VALUES ('%s', '%s');"%(tdate,outjson)
        backstr = self.sqlobj.execute(sqlcmd)
        if backstr < 100:
            print '保存%s推荐股票数据完成:%s'%(tdate,str(backstr))
        else:
            print "保存推存股票数据(日期:%s)错误"%(tdate)

    #保存今日分析前复权推存数据到数据库
    def saveTodayFQAnalyseShareToSql(self,tdate,datadic):
        #INSERT INTO `shares_dat`.`everydayshare` (`date`, `sharetext`) VALUES ('2017-03-03', 'aaa');
        outjson = json.dumps(datadic)
        sqlcmd = "INSERT INTO `shares_dat`.`fuquaneverydayshare` (`date`, `sharetext`) VALUES ('%s', '%s');"%(tdate,outjson)
        backstr = self.sqlobj.execute(sqlcmd)
        if backstr < 100:
            print '保存%s推荐股票数据完成:%s'%(tdate,str(backstr))
        else:
            print "保存推存股票数据(日期:%s)错误"%(tdate)

    #保存CSV数据到数据库,数据库列值使用CSV表头的中文拼音
    def saveCSVDataToSql(self,tabID,csvDatas,cname):
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
            # if backstr <= 100: #插入数据正常,加入第二天数据更新
            #     #UPDATE `shares_dat`.`000001` SET `tomorrow`='99' WHERE `id`='4145' and`date`='2017-02-20';
                
        return backtype
    #保存CSV数据到数据库,数据库列值使用CSV表头的中文拼音
    def addCSVDataToSql(self,tabID,csvDatas,cname,lastsqldic):
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

            if backstr <= 100: #插入数据正常,加入第二天数据更新
                tmpsqlid = self.sqlobj.lastrowid
                #UPDATE `shares_dat`.`000001` SET `tomorrow`='99' WHERE `id`='4145' and`date`='2017-02-20';
                sqlcmd = "UPDATE `shares_dat`.`%s` SET `tomorrow`='%s' WHERE `id`='%s';"%(tabID,str(listtmp[3]),str(lastsqldic[tabID][0]))
                self.sqlobj.execute(sqlcmd)
                lastsqldic[tabID][0] = tmpsqlid
            lastsqldic[tabID][1] = listtmp[0]
                
        return backtype

    #为数据表填加数据,增加数据后修改上一行数据的第二天数据
    def addOneLineTab(self,csvdatdic,fsqlIDdic,closeddic,datatmp):  #fsqlID为上一行的sqlID，通过这个ID更新上一天的第二天数据
        #INSERT INTO `shares_dat`.`000001` (`id`, `date`, `codeid`, `name`, `close`, `high`, `low`, `open`, `fclose`, `updown`, `percent`, `change`, `tradecount`, `trade`, `market`, `movemarket`) VALUES ('1', '2000-01-01', '000001', '深发展A', '18.29', '18.55', '17.2', '17.5', '17.45', '0.84', '4.81', '0.7667', '8216086', '147325356.78', '28383283312.7', '19600193797.9');
        #INSERT INTO `shares_dat`.`000001` (`id`, `date`, `codeid`, `name`, `close`, `high`, `low`, `open`, `fclose`, `updown`, `percent`, `change`, `tradecount`, `trade`, `market`, `movemarket`) VALUES ('2', '2000-01-05', '000001', '深发展A', '18.06', '18.85', '18', '18.35', '18.29', '-0.23', '-1.2575', '0.8771', '9399315', '173475158.81', '28026358481.5', '19353717878');
        ##日期 股票代码    名称  收盘价 最高价 最低价 开盘价 前收盘         涨跌额     涨跌幅        成交量     成交金额    
        #time k          k.   price high. low.   open. yestclose    updown     percent      volume     turnover
        backtype = 0
        for k in csvdatdic.keys():#每行数据
            sqlcmd = 'INSERT INTO `shares_dat`.`%s` (`date`, `codeid`, `name`, `close`, `high`, `low`, `open`, `fclose`, `updown`, `percent`, `tradecount`, `trade`) VALUES ('%(k)
            sqlcmd += csvdatdic[k] + ");"
            backstr = self.sqlobj.execute(sqlcmd,True)
            if backstr != 0:
                backtype = backstr
            if backstr <= 100: #插入数据正常,加入第二天数据更新
                tmpsqlid = self.sqlobj.lastrowid
                #UPDATE `shares_dat`.`000001` SET `tomorrow`='99' WHERE `id`='4145' and`date`='2017-02-20';
                sqlcmd = "UPDATE `shares_dat`.`%s` SET `tomorrow`='%s' WHERE `id`='%s';"%(k,closeddic[k],str(fsqlIDdic[k][0]))
                self.sqlobj.execute(sqlcmd,True)
                fsqlIDdic[k][0] = tmpsqlid
            fsqlIDdic[k][1] = datatmp
        return backtype


#测试
if __name__ == '__main__':
    sqltool = MySqlTool()

        
