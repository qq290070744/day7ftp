#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket,hmac,json,os,sys,logging,MySQLdb,copy,hashlib,time
projectpath=os.path.abspath(os.path.dirname("..\..\.."))
sys.path.append(projectpath)
#print(sys.path)
#定义日志级别、格式、输出位配置
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %Y-%m-%d %H:%M:%S',
                    filename='../day7_ftp/logs/error.log',
                    filemode='a',
                    )


ip_port = ('localhost',55555)

sk = socket.socket()
sk.connect(ip_port)

def get(msg):  # 从服务器端下载文件
    cmd,file_name=str(msg).split(' ')
    print '--get func---', msg
    if len(msg) > 0:

        instruction = "FileTransfer|get|%s" % file_name  # 告诉服务器端要下载什么文件
        sk.send(instruction)
        feedback = sk.recv(100)  # 等待服务器端的消息确认
        print '-->', feedback
        if feedback.startswith("FileTransfer|get|ready"):  # 代表服务器上文件存在，并且服务器已经准备好了发送此文件到客户端
            file_size = int(feedback.split("|")[-1])  # 服务器端发回来的确认消息中，最后面一个值是文件大小，必须知道文件大小才知道一共要收多少内容
            sk.send("FileTransfer|get|recv_ready")  # 告诉服务器端已经准备好了接收
            recv_size = 0  # 因为文件可能会比较大，一次收不完，所以要循环收，每收到一次，就计个数
            with open('clientftp/%s' % os.path.basename(file_name), 'wb') as f:  # 在本地创建一个新文件来存这个要下载的文件内容
                print '--->', file_name
                i=0
                while not file_size == recv_size:  # 只要文件总大小和已收到的大小不想等，就代表还没收完
                    if file_size - recv_size > 1024:  # 文件总大下减已收到的大小等于还剩下没收到的大小，如果这个数大于1024，代表一次肯定收不完，那就还得多循环几次
                        data = sk.recv(1024)  # 这次收1024字节，但实际上收到的可能比1024小，所以需要以实际收到的数为准
                        recv_size += len(data)  # 已收到的大小加上这一次循环收到的实际大小
                    else:  # 如果最后剩下的少于1024，那就一次性把剩下的都收过来
                        data = sk.recv(file_size - recv_size)
                        # recv_size = file_size #不能这么写，因为这一次依然不一定能一次性收完，因为实际收到的数据可能比你规定的数据要少， 所以需要按下面这行的方式写
                        recv_size += (file_size - recv_size)

                    f.write(data)  # 收到的内容写入文件
                    i+=1
                    st = ("\r%s" % ("=" * i)).ljust(10) + ("[%dk]" % (i )).rjust(6)
                    sys.stdout.write(st)
                    time.sleep(0.01)


                else:
                    print '---recv file:%s---' % file_name

        else:
            print feedback

def put(msg) :
    global user
    cmd, file_name = str(msg).split(' ')
    print '--put func---', msg
    instruction = "FileTransfer|put|%s" % file_name  # 告诉服务器端要上传什么文件
    sk.send(instruction)
    feedback = sk.recv(100)  # 等待服务器端的消息确认
    print '-->', feedback
    if feedback.startswith("FileTransfer|put|ready"):  # 代表服务器上文件存在，并且服务器已经准备好了发送此文件到客户端
        file_size = int(feedback.split("|")[-1])  # 服务器端发回来的确认消息中，最后面一个值是文件大小，必须知道文件大小才知道一共要收多少内容
        sk.send("FileTransfer|put|recv_ready")  # 告诉服务器端已经准备好了接收
        recv_size = 0  # 因为文件可能会比较大，一次收不完，所以要循环收，每收到一次，就计个数

        with open('users/{}/{}'.format(user , os.path.basename(file_name)), 'wb') as f:  # 在ftp服务器建一个新文件来存这个要下载的文件内容
            print '--->', file_name
            i = 0
            while not file_size == recv_size:  # 只要文件总大小和已收到的大小不想等，就代表还没收完
                if file_size - recv_size > 1024:  # 文件总大下减已收到的大小等于还剩下没收到的大小，如果这个数大于1024，代表一次肯定收不完，那就还得多循环几次
                    data = sk.recv(1024)  # 这次收1024字节，但实际上收到的可能比1024小，所以需要以实际收到的数为准
                    recv_size += len(data)  # 已收到的大小加上这一次循环收到的实际大小
                else:  # 如果最后剩下的少于1024，那就一次性把剩下的都收过来
                    data = sk.recv(file_size - recv_size)
                    # recv_size = file_size #不能这么写，因为这一次依然不一定能一次性收完，因为实际收到的数据可能比你规定的数据要少， 所以需要按下面这行的方式写
                    recv_size += (file_size - recv_size)

                f.write(data)  # 收到的内容写入文件
                i += 1
                st = ("\r%s" % ("=" * i)).ljust(10) + ("[%dk]" % (i)).rjust(6)
                sys.stdout.write(st)
                time.sleep(0.01)


            else:
                print '---recv file:%s---' % file_name

    else:
        print feedback





while True:

    user=raw_input("enter user:").strip()
    sk.sendall(user)
    server_reply = sk.recv(500)
    if server_reply=="ok":
        break
while True:
    password=raw_input("enter password:").strip()
    h = hmac.new(password)
    print (h.hexdigest())
    sk.sendall(h.hexdigest())
    server_reply = sk.recv(500)
    if server_reply == "ok":
        break

while True:
    user_input = raw_input(">>:").strip()# 用户输入命令
    if len(user_input)==0:continue# 用户如果直接按了回车,既为空,则进行下次循环
    if 'get'  in user_input :
        get(user_input)
        continue
    if 'put' in user_input:
        put(user_input)
        continue
    sk.send(user_input)# 将用户的命令通过socket发送给服务器端
    res=''
    while True:
        server_reply = sk.recv(500)
        res+=server_reply
        print("-"*10)
        if len(server_reply)<500:#当接收到的字节小于500就判断已经接收完了。

            break

    print(res)






sk.close()
