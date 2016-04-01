#-*- coding:utf8 -*-

import paramiko
import re
import os

from core.logger import logger
from conf.settings import *

class PySSH(object):
    """
    #主类，对参数进行解析、执行
    """
    def __init__(self,remote_host_address,port,username,password):
        """
        #初始化默认主机信息，优先级大于配置文件
        """
        self.remote_host_address = remote_host_address
        self.port = port
        self.username = username
        self.password = password
        self.sucess_count = self.make_count()
        self.error_count = self.make_count()
        #Get、Put
        self.t = paramiko.Transport((self.remote_host_address, self.port))
        self.t.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.t)
        #Command
        self.s = paramiko.SSHClient()
        self.s.load_system_host_keys()
        self.s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.s.connect(self.remote_host_address,self.port,self.username,self.password,timeout=connect_timeout)

    def make_count(self):
        """
        #使用闭包统计自定义数量
        """
        count = 0
        def counter(print_reduce=0):
            nonlocal count
            count += 1
            count += print_reduce
            return count
        return counter

    def get_dirs(self,rpath,lpath):
        """
        #文件下载及目录下载
        """
        rpath = rpath.strip().rstrip('/')
        #判断get是文件or目录
        try:
            dir_or_file = str(self.sftp.stat(rpath))
            #如果是目录
            if re.match(r'd',dir_or_file):
                files_dirs = self.sftp.listdir(rpath)
                #判断目录下是否为空
                if not len(files_dirs) == 0:
                    for i in files_dirs:
                        r_files_dirs = rpath + '/' + i
                        try:
                            f_d = str(self.sftp.stat(r_files_dirs))
                        except Exception as e:
                            #将报错文件or目录写入日志
                            logger.error(e)
                        #对目录进程操作循环
                        if re.match(r'd',f_d):
                            rdir = rpath + '/' + i
                            lpath = lpath + os.sep + i
                            #本地创建递归目录结构
                            if not os.path.exists(lpath):
                                os.makedirs(lpath)
                            self.get_dirs(rdir,lpath)
                            #重新循环，格式lpath为原路径
                            lpath = os.path.split(lpath)[0]
                        #对目录下文件进行get
                        else:
                            rfile = rpath + '/' + i
                            lfile = lpath + os.sep + i
                            try:
                                self.sftp.get(rfile,lfile)
                                self.sucess_count()
                                if print_file_get:print ('%s Download complete.' % rfile.ljust(50))
                            except Exception as e:
                                self.error_count()
                                logger.error(str(e) + ' ' +rfile)
            #如果是文件
            else:
                #保存到指定目录
                if os.path.exists(lpath) and os.path.isdir(lpath):
                    filename = os.path.split(rpath)[-1]
                    lfile = lpath + os.sep + filename
                    try:
                        self.sftp.get(rpath,lfile)
                        self.sucess_count()
                        print ('%s Download complete.' % rpath.ljust(50))
                    except Exception as e:
                        self.error_count()
                        logger.error(str(e) + ' ' +rpath)
                #保存为指定文件名
                else:
                    try:
                        self.sftp.get(rpath,lpath)
                        self.sucess_count()
                        if print_file_get:print ('%s Download complete.' % rpath.ljust(50))
                    except Exception as e:
                        self.error_count()
                        logger.error(str(e) + ' ' +rpath)

        except FileNotFoundError as e:
            print (self.remote_host_address)
            print ("File or dir %s not found!" % rpath)

    def get(self,rpath,lpath):
        """
        #下载文件目录，调用get_dirs
        """
        self.get_dirs(rpath,lpath)
        print (self.remote_host_address)
        error_num = self.error_count(-1)
        msg_ok = 'Get Total files number: %s' % self.sucess_count(-1)
        msg_error = 'Get Error files number: %s' % error_num
        logger.info('%s %s %s' % (self.remote_host_address,rpath,msg_ok))
        if error_num > 0:
            logger.error('%s %s %s' % (self.remote_host_address,rpath,msg_error))
        print (msg_ok)
        print (msg_error)

    def command(self,command):
        """
        #执行命令模块
        """
        #print (command)
        stdin,stdout,stderr = self.s.exec_command(command)
        a = stderr.read().decode()
        if 'already exists' in a:
            ret = True
        else:
            ret = False
        if len(a) == 0 or ret:
            print (self.remote_host_address,':OK')
            out = stdout.read()
            try:
                print (out.decode())
            except UnicodeDecodeError:
                print (out.decode('gb2312'))
            msg = "[%s] exec command [%s] success" % (self.remote_host_address,command)
            logger.info(msg)
        else:
            print (self.remote_host_address,':')
            print (stderr.read().decode())
            logger.error(stderr.read().decode())
            print (a)
            print ('Somethings is Wrong,Please sure.')
        self.s.close()

    def put_dir(self,lpath,rpath=None):
        """
        #upload dirs
        """
        s_path = os.path.abspath(lpath)
        s_num = len(s_path)
        for path, dirname,filelist in os.walk(lpath):
            for dname in dirname:
                lpath_dirpath = os.path.abspath(os.path.join(path,dname))
                r_path = (rpath + lpath_dirpath[s_num:]).replace('\\', '/')
                command = 'mkdir -p %s' % r_path
                stdin,stdout,stderr = self.s.exec_command(command)
                if len(stderr.read().decode()) != 0:
                    logger.error(stderr.read().decode())
                    print ('%s command exec wrong!!!' % command)
            for fname in filelist:
                lfilepath = os.path.abspath(os.path.join(path,fname))
                rfilepath = (rpath + lfilepath[s_num:]).replace('\\', '/')
                yield lfilepath,rfilepath

    def put_file(self,lpath,rpath=None):
        """
        #Upload files
        """
        try:
            if re.match(r'd',str(self.sftp.stat(rpath))):
                rpath = rpath.rstrip('/') + '/' + os.path.split(lpath)[-1]
        except FileNotFoundError:
            pass
        try:
            self.sftp.put(lpath,rpath)
            self.sucess_count()
            if print_file_put:print ('%s Uploading complete.' % rpath.ljust(50))
        except Exception as e:
            self.error_count()
            logger.error(str(e) + ' ' + lpath)

    def put(self,lpath,rpath=None):
        if not rpath:
            print ('Please input remote file or dir')
        else:
            if os.path.isfile(lpath):
                self.put_file(lpath,rpath)
            else:
                if re.match(r'd',str(self.sftp.stat(rpath))):
                    for l,r in self.put_dir(lpath, rpath):
                        self.put_file(l,r)
                else:
                    print ('Remote path must be a dirname')
                self.s.close()
        print (self.remote_host_address)
        error_num = self.error_count(-1)
        msg_ok = 'Put Total files number: %s' % self.sucess_count(-1)
        msg_error = 'Put Error files number: %s' % error_num
        logger.info('%s %s %s' % (self.remote_host_address,rpath,msg_ok))
        if error_num > 0:
            logger.error('%s %s %s' % (self.remote_host_address,rpath,msg_error))
        print (msg_ok)
        print (msg_error)
