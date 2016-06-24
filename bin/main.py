#!/usr/bin/env python
# -*- coding:utf-8 -*-
import prettytable,MySQLdb,server_ftp,SocketServer

conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', db='jiang', charset="utf8")
cur = conn.cursor()
x = prettytable.PrettyTable(["\033[32m编号\033[0m","\033[33m名称\033[0m"])
x.add_row([1,'添加ftp用户'])
x.add_row([2,'删除ftp用户'])
x.add_row([3,'启动 ftp_client'])
x.add_row([4,'exit'])
print x
enter=raw_input("enter number:").strip()
if enter=='1':
    enter_user=raw_input("enter username:").strip()
    enter_pass=raw_input("enter password:").strip()
    peire=raw_input("请输入用户空间大小（单位:M）").strip()
    conn = MySQLdb.connect(host='127.0.0.1', user='jwh', passwd='123456', db='jiang')
    cur = conn.cursor()
    reCount = cur.execute('insert into userpass(username,password,peire) values(%s,%s,%s)', (enter_user, enter_pass,peire))
    conn.commit()
    print ('添加用户{}成功！'.format(enter_user))

elif enter=='2':
    enter_user = raw_input("enter username:").strip()
    enter_pass = raw_input("enter password:").strip()
    reCount = cur.execute("delete from userpass where username='%s' and password='%s'   "%(enter_user,enter_pass))
    conn.commit()
    print ('delete用户{}成功！'.format(enter_user))

elif enter=='3':

    import  client_ftp
cur.close()
conn.close()