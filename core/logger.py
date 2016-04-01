#-*- coding:utf8 -*-
import logging
import os
from conf.settings import *

logdir = os.path.join(os.getcwd(),'log')
logfile = os.path.join(logdir,logname)

#将error日志输出到文件及控制台
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename=logfile,
                filemode='a')

#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
formatter.datefmt = '%Y-%m-%d %H:%M:%S'
console.setFormatter(formatter)
logger = logging.getLogger('DevOps')
logger.addHandler(console)