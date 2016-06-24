#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket,subprocess,sys,SocketServer,select,logging,MySQLdb,hmac,os,re,copy,json,hashlib
projectpath=os.path.abspath(os.path.dirname("..\..\.."))
sys.path.append(projectpath)
print sys.path
#定义日志级别、格式、输出位配置
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %Y-%m-%d %H:%M:%S',
                    filename='../logs/error.log',
                    filemode='a',
                    )



class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        while True:
            data=self.request.recv(1024)
            #从数据库读取用户名和密码
            conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', db='jiang', charset="utf8")
            cur = conn.cursor()
            reCount = cur.execute("select * from userpass  where username='%s'" % (data))
            userpass = cur.fetchone()
            cur.close()
            conn.close()
            self.user, password = userpass[0], userpass[1]
            if data == self.user:
                self.request.send("ok")

                break
        self.userpath = subprocess.Popen('cd ../users/ && pwd', stdout=subprocess.PIPE, shell=True).stdout.read()
        print self.userpath
        while True:
            data = self.request.recv(1024)
            #print data,password
            h = hmac.new(str(password))

            if data==h.hexdigest():
                self.request.send("ok")
                #如果是第一次登录成功后创建用户家目录
                os.chdir(self.userpath.strip())
                if not os.path.isdir(self.user):
                    os.makedirs(self.user)
                    os.chdir( self.user)
                else:
                    os.chdir(self.user)

                self.pwd=subprocess.Popen('pwd',stdout=subprocess.PIPE,shell=True).stdout.read()


                break

        while True:

            self.ls = subprocess.Popen('ls', stdout=subprocess.PIPE, shell=True).stdout.read()
            print("conn:{}".format(self.client_address))
            data=self.request.recv(1024)
            if not data :
                break
            print("client :",data.decode())
            #self.request.send(data)
            print data

            if 'cd' in data :
                cmd, cmdpath = str(data).split(' ')
                path = subprocess.Popen("pwd", stdout=subprocess.PIPE, shell=True).stdout.read()

                if cmdpath.strip() in self.ls and os.path.isdir(cmdpath) :
                    obj = subprocess.Popen("{} && pwd".format(data), stdout=subprocess.PIPE, shell=True).stdout.read()
                    os.chdir(obj.strip())
                    print "已切换工作目录到：{}".format(obj)
                    self.request.send("已切换工作目录到：{}".format(obj))
                elif cmdpath.strip() in ".." and  self.user+'/' in path :
                    obj = subprocess.Popen("{} && pwd".format(data), stdout=subprocess.PIPE, shell=True).stdout.read()
                    os.chdir(obj.strip())
                    print "已切换工作目录到：{}".format(obj)
                    self.request.send("已切换工作目录到：{}".format(obj))
                else:
                    print "切换工作目录\033[31m失败\033[0m"
                    self.request.send("切换工作目录\033[31m失败\033[0m")
                continue

            if 'get'   in str(data) or 'put' in str(data):
                self.FileTransfer(data)
                continue

            obj= subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = obj.communicate()
            dat = "{}{}".format(out, err)
            self.request.send(dat)
            #print(obj)
            logging.error('enter cmd: {}!'.format(data.decode()))  # 记录用户输入了那些命令的日志

            if not dat:

                self.request.send("cmd 执行完成!")


    def FileTransfer(self, msg):  # 负责文件的发送和接收
        print '---filetransfer---', msg
        FileTransfer,cmd,filename=msg.split('|')
        if cmd.strip() == 'get':  # 如果客户端发来的指令是get,那就是下载文件
            print "客户端要下载文件:", filename
            if os.path.isfile(filename):  # 判断客户端发的文件名是否存在并是个文件
                file_size = os.path.getsize(filename)  # 获取文件大小
                res = "ready|%s" % file_size  # 把文件大小告诉客户端
            else:
                res = "file doesn't exist"  # 文件也有可能不存在
            send_confirmation = "FileTransfer|get|%s" % res
            self.request.send(send_confirmation)  # 发送确认消息给客户端
            feedback = self.request.recv(
                100)  # 等待客户端确认， 如果这时不等客户端确认就立刻给客户端发文件内容，因为为了减少IO操作，socket发送和接收是有缓冲区的，缓冲区满了才会发送，那上一条消息很有可能会和文件内容的一部分被合并成一条消息发给客户端，这就行成了粘包，所以这里等待客户端的一个确认消息，就把两次发送分开了，不会再有粘包
            if feedback == 'FileTransfer|get|recv_ready':  # 如果客户端说准备好接收了
                with open(filename, 'rb') as f:
                    send_size = 0  # 发送的逻辑跟客户端循环接收的逻辑是一样的
                    while not file_size == send_size:
                        if file_size - send_size > 1024:
                            data = f.read(1024)
                            send_size += 1024
                        else:  # left data less than 1024
                            data = f.read(file_size - send_size)
                            send_size += (file_size - send_size)
                        self.request.send(data)
                        print file_size, send_size
                    else:
                        print '---send file:%s done----' % filename


        elif cmd.strip() == 'put':
            print "客户端要上传文件:", filename
            if os.path.isfile('../../clientftp/{}'.format(filename)):  # 判断客户端发的文件名是否存在并是个文件
                file_size = os.path.getsize('../../clientftp/{}'.format(filename))  # 获取文件大小
                res = "ready|%s" % file_size  # 把文件大小告诉客户端
            else:
                res = "file doesn't exist"  # 文件也有可能不存在
            send_confirmation = "FileTransfer|put|%s" % res
            self.request.send(send_confirmation)  # 发送确认消息给客户端
            feedback = self.request.recv(
                100)  # 等待客户端确认， 如果这时不等客户端确认就立刻给客户端发文件内容，因为为了减少IO操作，socket发送和接收是有缓冲区的，缓冲区满了才会发送，那上一条消息很有可能会和文件内容的一部分被合并成一条消息发给客户端，这就行成了粘包，所以这里等待客户端的一个确认消息，就把两次发送分开了，不会再有粘包
            if feedback == 'FileTransfer|put|recv_ready':  # 如果客户端说准备好接收了
                with open('../../clientftp/{}'.format(filename), 'rb') as f:
                    send_size = 0  # 发送的逻辑跟客户端循环接收的逻辑是一样的
                    while not file_size == send_size:
                        if file_size - send_size > 1024:
                            data = f.read(1024)
                            send_size += 1024
                        else:  # left data less than 1024
                            data = f.read(file_size - send_size)
                            send_size += (file_size - send_size)
                        self.request.send(data)
                        print file_size, send_size
                    else:
                        print '---send file:%s done----' % filename

            pass

if __name__ == '__main__':
    host,port="127.0.0.1",55555

    server=SocketServer.ThreadingTCPServer((host,port),MyTCPHandler)
    server.serve_forever()