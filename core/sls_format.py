#-*- coding:utf8 -*-

import yaml
import os


class SlsFormat(object):
    """
    handle sls yaml file,obtain hosts、module、command
    """
    def __init__(self,yamlfile):
        self.yamlfile = yamlfile
        if self.exists:
            self.dict_sls = self.yaml_dict()

    def yaml_dict(self):
        """
        load sls yaml file
        :return: sls dict
        """
        with open(self.slsfile) as f:
            s = yaml.load(f)
        return s

    def info(self):
        """
        Different modules,obtain different command
        :return:
        """
        for k,v in self.dict_sls.items():

            if k == 'cmd.run':
                return k,v['host'],v['command']
            elif k == 'file.get':
                return k,v['host'],[v['source'],v['destination']]
            elif k == 'file.put':
                return k,v['host'],[v['source'],v['destination']]
            #create user and update password
            elif k == 'user.present':
                command = ''
                for i in v:
                    if i != 'host':
                        u = 'useradd '
                        for ai in v[i]:
                            #k = ai.keys()[0]
                            for aii in ai:
                                ke = aii
                                if ke == 'user':
                                    username = str(ai['user'])
                                    u = u + username + ' '
                                if ke == 'home':
                                    u = u + '-d ' + str(ai['home']) + ' '
                                else:
                                    u = u + '-m '
                                if ke == 'uid':u = u + '-u ' + str(ai['uid']) + ' '
                                if ke == 'shell':u = u + '-s ' + str(ai['shell']) + ' '
                            for ai in v[i]:
                                for aii in ai:
                                    ke = aii
                                    if ke == 'password':p =  ';echo %s|passwd --stdin %s '%(str(ai['password']),username)
                        u = u + p
                        command += '%s;'%u
                return (k,v['host'],command)
            elif k == 'user.del':
                command = ''
                for i in v:
                    if i != 'host':
                        u = 'userdel '
                        for ai in v[i]:
                            for aii in ai:
                                ke = aii
                                if ke == 'user':u = u + str(ai['user']) + ' '
                                if ke == 'home':
                                    if str(ai['home']) == 'True':
                                        u = u + '-r'
                        command += '%s;'%u
                return (k,v['host'],command)
            else:
                print ('Not to support!')

    @property
    def exists(self):
        """
        to determine whether the sls yaml file exists
        :return:
        """
        slsname = self.yamlfile + '.sls'
        slsdir = os.path.join(os.getcwd(),'sls')
        self.slsfile = os.path.join(slsdir,slsname)
        if os.path.exists(self.slsfile):
            return True


if __name__ == '__main__':
    a = SlsFormat(file)
    b = a._one()
    print (b.__next__())