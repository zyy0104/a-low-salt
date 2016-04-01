作者： Yuntu   
版本：v0.1    
程序介绍：   
	采用多进程，对批量主机执行命令、文件上传、下载、创建用户、删除用户   

1、对批量主机执行命令，返回执行结果   
2、上传批量文件或指定文件、指定目录到批量远程主机，默认覆盖；返回各主机上传成功文件数量   
3、下载批量文件或指定文件、指定目录到本地；   
	如指定单独远程主机，默认覆盖行为；   
	如指定为主机组，如同目录下存在相同文件，会覆盖，不可预测文件一致性，建议下载时不要存着相同文件名；   
	返回各主机下载成功文件数量；   
4、创建用户，可不指定home、shell、uid默认为系统下/home/user   
5、删除用户，如home为True，则删除用户家目录   

记录操作日志；   
	记录命令、及执行时间及结果；   
	记录文件操作、数量及结果；   

cmd.run      #执行命令   
file.get     #下载文件及目录   
file.put     #上传文件及目录   
test.ping    #测试   
user.present #批量添加主机账号及更新主机账号密码，uid,home,shell可选，但参数不能为空   
user.del     #批量删除主机账号，是否删除家目录可选   

├── bin    
│   ├── __init__.py   
│   └── pyssh.py        #调用命令解析module，根据sls文件执行相关命令   
├── conf   
│   ├── __init__.py   
│   ├── roster          #主机paramiko信息       
│   └── settings.py     #程序配置信息   
├── core   
│   ├── hosts_format.py #处理roster文件   
│   ├── __init__.py   
│   ├── logger.py       #日志记录   
│   ├── module.py       #命令解释及执行   
│   └── sls_format.py   #处理sls文件   
├── log   
│   └── pyssh.log       #日志文件   
├── sls      
│   ├── getfile.sls     #下载文件或目录模板      
│   ├── lsal.sls        #执行命令模板   
│   └── putfile.sls     #上传文件或目录模板   
└── yeal.py                #主执行程序   

1、对所有主机执行命令   
[root@python yealstack]# python3.5 yeal.py '*' cmd.run id   
192.168.1.249 :   
uid=0(root) gid=0(root) 组=0(root)   

192.168.1.44 :   
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023   

2、使用sls yaml文件执行命令        
[root@python yealstack]# more sls/lsal.sls   
cmd.run:   
    host:   
    - test1   
    - test3   
    command: id   
[root@python yealstack]# python3.5 yeal.py cmd.run lsal   
192.168.1.44 :   
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023   

192.168.1.249 :   
uid=0(root) gid=0(root) 组=0(root)   

3、使用sls yaml下载文件或目录   
[root@python yealstack]# more sls/getfile.sls   
file.get:   
    host:   
    - test1   
    source: /etc/passwd   
    destination: /tmp/test.pwd      
[root@python yealstack]# python3.5 yeal.py test3 file.get getfile      
192.168.1.249   
Get Total files number: 1   
Get Error files number: 0   
192.168.1.44   
Get Total files number: 1   
Get Error files number: 0   

[root@python yealstack]# more sls/getfile.sls   
file.get:   
    host:   
    - test1   
    source: /home/a   
    destination: /tmp/a   
[root@python yealstack]# python3.5 yeal.py test3 file.get getfile   
192.168.1.44   
Get Total files number: 10   
Get Error files number: 0   
192.168.1.249   
Get Total files number: 1805   
Get Error files number: 0   

3、使用sls yaml上传文件或目录   
[root@python yealstack]# more sls/putfile.sls   
file.put:   
    host:   
    - test1   
    source: /etc/passwd   
    destination: /home/a.txt   
[root@python yealstack]# python3.5 yeal.py  file.put putfile   
192.168.1.44   
Put Total files number: 1   
Put Error files number: 0   

[root@python yealstack]# more sls/putfile.sls   
file.put:   
    host:   
    - test1   
    source: /home/a   
    destination: /tmp   
[root@python yealstack]# python3.5 yeal.py test3 file.put putfile   
192.168.1.249   
Put Total files number: 8   
Put Error files number: 0   
192.168.1.44   
Put Total files number: 8   
Put Error files number: 0   

4、检查主机paramiko配置是否正确   
D:\OldMan_Python\day9\yealstack>python yeal.py '*' test.ping   
192.168.1.44 :   
        OK   
192.168.1.44 :   
        False   
192.168.1.249 :   
        OK   
5、批量添加主机账号   
user.present:   
  host:   
  - test1   
  - test3   
  user1:   
  - user: user13   
  - password: 123456   
  - shell: /bin/bash   
#  - home: /home/user13   
#  - gid: 1012   
  user2:   
  - user: user14   
  - password: 123456   
  - shell: /bin/bash   
  - home: /home/user14   
  - gid: 1030   
C:\Users\Yuntu\Desktop\Python\Yuntu\day9\yealstack>python yeal.py user.present useradd   
192.168.1.44 :   
Changing password for user user14.   
passwd: all authentication tokens updated successfully.   
Changing password for user user13.   
passwd: all authentication tokens updated successfully.   

192.168.1.249 :   
更改用户 user14 的密码 。   
passwd： 所有的身份验证令牌已经成功更新。   
更改用户 user13 的密码 。   
passwd： 所有的身份验证令牌已经成功更新。   

5、批量删除主机账号   
user.del:   
  host:   
  - test1   
  user1:   
  - user: user1   
  - home: True   
  user2:   
  - user: user2   
  - home: False   
C:\Users\Yuntu\Desktop\Python\Yuntu\day9\yealstack>python yeal.py user.del userdel   
192.168.1.44 :OK   
