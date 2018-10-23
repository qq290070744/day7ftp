作业：开发一个支持多用户在线的FTP程序

要求及完成情况：

  用户加密认证————使用hmac加密密码生成md5值,发送用户名+md5值到服务器进行比较，
  允许同时多用户登录————使用socketserver.ThreadingTCPServer实现多线程服务端，以支持多用户
  每个用户有自己的家目录 ，且只能访问自己的家目录————新建的用户产生单独配置文件及家目录
  对用户进行磁盘配额，每个用户的可用空间不同————磁盘配额在新建用户时配置
  允许用户在ftp server上随意切换目录————  使用方法：cd <目录>  无法进入其他目录，只能在家目录下
  允许用户查看当前目录下文件———— 使用方法：ls
  允许上传和下载文件，保证文件一致性————上传方法：put <文件名> 下载方法：get <文件名>
  文件传输过程中显示进度条

脚本目录介绍：

  day7├── bin                                    主程序目录
  │   ├── DBInit.py                       DB初始化（1、初始化conf目录和ftp目录 2、加用户 3、删用户）
  │   ├── ftpClient.py                    ftp客户端
  │   ├── ftpServer.py                    ftp服务端
  │   └── __init__.py
  ├── clientftp                         ftp客户端目录（下载时存放文件，上传时使用此文件夹下的文件）
  │   ├── hb.jpg
  │   ├── store.png
  │  
  │  
  ├── users                        用户家目录文件夹
  │   ├── __init__.py
  │   ├── jwh
  │   └── test
  ├── __init__.py
  ├── logs                                     服务端日志目录，简单记录登录登出，及操作错误
  │   ├── __init__.py
  │   └── xxxxx.log
  └── readme

本程序使用方法（本程序在linux系统下，以python2.7为基础开发，请在linux环境下运行）：

  一、启动ftp服务端程序
  python server_ftp
  二、启动main.py主程序
  python main.py
  启动 出现
  +------+-----------------+
  | 编号 |       名称      |
  +------+-----------------+
  |  1   |   添加ftp用户   |
  |  2   |   删除ftp用户   |
  |  3   | 启动 ftp_client |
  |  4   |       exit      |
  +------+-----------------+
  enter number:
  三、使用ftp客户端程序
  python client_ftp
  执行后输入用户名和密码后可以执行命令。
  四，此程序需要连接mysql数据库，
  数据库名jiang
  表名userpass
  mysql> select * from userpass;
  +----------+----------+------+---------+-------+
  | username | password | flag | rmb     | peire |
  +----------+----------+------+---------+-------+
  | jwh      | 123456   |    0 | 4557950 |   100 |
  | wenhui   | 123456   |    0 | 1000000 |   100 |
  | test     | test     |    0 | 1000000 |   100 |
  +----------+----------+------+---------+-------+
  3 rows in set (0.00 sec)
  mysql>



![Alt text](http://s1.51cto.com/images/20180504/1525403548451542.png)
