import yaml

class Hosts(object):
    """
    parse host yaml file
    """
    def __init__(self,yamlfile):
        self.yamlfile = yamlfile
        self.dict_hosts = self.yaml_dict()

    def yaml_dict(self):
        """
        load host yaml file
        :return: host dict
        """
        with open(self.yamlfile) as f:
            s = yaml.load(f)
        return s

    @property
    def hosts(self):
        """
        :return: a host list contains all hosts
        """
        host_list = []
        for k,v in self.dict_hosts.items():
            host_list.append(k)
        return host_list

    def host_info(self,name):
        """
        according to the host name,obtain host-ip、username、passwd、port
        :param name:
        :return:
        """
        for k,v in self.dict_hosts.items():
            if k == name:
                return str(v['host']),str(v['user']),str(v['passwd']),int(v['port'])


if __name__ ==  '__main__':
    a = Hosts('roster')
    print (a.hosts)
    print (a.host_info('test3'))