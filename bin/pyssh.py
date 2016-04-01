#-*- coding:utf8 -*-

"""
Author:Yuntu
datetime:2016-03-14
Email:zyy0104@yeah.net
"""

import multiprocessing
import sys,os

from core.module import PySSH
from core.hosts_format import Hosts
from core.sls_format import SlsFormat

from conf.settings import *

#默认多进程数量等于CPU核数
if not process_pool_number:
    process_pool_number = multiprocessing.cpu_count()

#对sls文件进行格式化，取出指令信息
sls = SlsFormat(sys.argv[-1])
roster_dir = os.path.join(os.getcwd(),'conf')
#对roster文件进行格式，提取paramiko登录信息
info = Hosts(os.path.join(roster_dir,hosts_file))


def hosts():
    """
    :return: host set
    """
    host_list = []
    cmd = ['cmd.run','file.get','file.put','*','test.ping','user.present','user.del']
    if sys.argv[1].strip('\'\"') not in cmd and len(sys.argv) >= 3:
        host_list.append(sys.argv[1])
    if sys.argv[1].strip('\'\"') == '*':
        for h in info.hosts:
            host_list.append(h)
    if sls.exists:
        module ,sls_host, command = sls.info()
        for h in sls_host:
            host_list.append(h)
    return set(host_list)

def module():
    """
    :return: module list,ex:cmd.run
    """
    if 'cmd.run' in sys.argv:module = 'cmd.run'
    if 'file.get' in sys.argv:module = 'file.get'
    if 'file.put' in sys.argv:module = 'file.put'
    if 'test.ping' in sys.argv:module = 'test.ping'
    if 'user.present' in sys.argv:module = 'user.present'
    if 'user.del' in sys.argv:module = 'user.del'
    if sls.exists:
        module ,sls_host, command = sls.info()
    return module

def command():
    """
    :return: command
    """
    command = None
    if 'cmd.run' in sys.argv:
        i = sys.argv.index('cmd.run')
        command = sys.argv[i+1].strip('\'\"')
    if sls.exists:
        module ,sls_host, command = sls.info()
    return command

class ExecArgv(object):
    """
    call execution module,parse sls file execution related commands.
    """
    def __init__(self,hosts,module,command=None):
        """
        execute related modules func.
        :param hosts: host set
        :param module: cmd.run|file.get|file.put
        :param command: command
        :return:
        """
        self.hosts = hosts
        self.module = module
        self.command = command
        if module == 'cmd.run':self.exec()
        if module == 'file.get':self.get()
        if module == 'file.put':self.put()
        if module == 'test.ping':self.ping()
        if module == 'user.present':self.exec()
        if module == 'user.del':self.exec()

    def exec(self):
        """
        execute command,call exec_run to runing use multiprocessing
        :return:
        """
        pool = multiprocessing.Pool(process_pool_number)
        for h in self.hosts:
            pool.apply_async(func=self.exec_run(h))
        pool.close()
        pool.join()

    def exec_run(self,h):
        """
        execute command
        :param h: one of the host sets
        :return:
        """
        #to determine whether the existence of the host
        if h.strip('\'\"') in info.hosts:
            self.ip,self.username, self.password, self.port = info.host_info(h)
            #生产实例
            try:
                ssh_server = PySSH(self.ip,self.port,self.username,self.password)
                ssh_server.command(self.command)
            except Exception as e:
                print (self.ip,':')
                print ('\tFalse\n')
        else:
            print ('Host %s not found!!!'%h)

    def ping(self):
        pool = multiprocessing.Pool(process_pool_number)
        for h in self.hosts:
            pool.apply_async(func=self.ping_run(h))
        pool.close()
        pool.join()

    def ping_run(self,h):
        if h.strip('"\'') in info.hosts:
            self.ip,self.username, self.password, self.port = info.host_info(h)
        #生产实例
            try:
                ssh_server = PySSH(self.ip,self.port,self.username,self.password)
                print (self.ip,':')
                print ('\tOK')
            except Exception as e:
                print (self.ip,':')
                print ('\tFalse')
        else:
            print ('Host %s not found!!!'%h)

    def get(self):
        """
        execute file.get module,call get_run to runing use multiprocessing
        :return:
        """
        pool = multiprocessing.Pool(process_pool_number)
        for h in self.hosts:
            pool.apply_async(func=self.get_run(h))
        pool.close()
        pool.join()

    def get_run(self,h):
        """
        execute file.get module
        :param h: one of the host sets
        :return:
        """
        #to determine whether the existence of the host
        if h.strip('\'\"') in info.hosts:
            self.ip,self.username, self.password, self.port = info.host_info(h)
        #生产实例
            try:
                source,destination = self.command
                ssh_server = PySSH(self.ip,self.port,self.username,self.password)
                ssh_server.get(source,destination)
            except Exception as e:
                print (self.ip,':')
                print ('\tFalse\n')
        else:
            print ('Host %s not found!!!'%h)

    def put(self):
        """
        execute file.put module,call put_run to runing use multiprocessing
        :return:
        """
        pool = multiprocessing.Pool(process_pool_number)
        for h in self.hosts:
            pool.apply_async(func=self.put_run(h))
        pool.close()
        pool.join()

    def put_run(self,h):
        if h.strip('\'\"') in info.hosts:
            self.ip,self.username, self.password, self.port = info.host_info(h)
            #生产实例
            try:
                source,destination = self.command
                ssh_server = PySSH(self.ip,self.port,self.username,self.password)
                ssh_server.put(source,destination)
            except Exception as e:
                print (self.ip,':')
                print ('\tFalse\n')

        else:
            print ('Host %s not found!!!'%h)

def main():
    """
    running
    :return:
    """
    m = ExecArgv(hosts(),module(),command())


