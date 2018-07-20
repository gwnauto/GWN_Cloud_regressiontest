#coding=utf-8
#作者：曾祥卫
#时间：2018.03.20
#描述：cloud系统设置-设置的控制层


import time
from data import data
from publicControl.public_control import PublicControl




class SettingsControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #获取网络组的ssh密码
    def get_ssh_pwd(self):
        api = self.loadApi()['sysSettingShow']
        request = PublicControl(self.s)
        recvdata = request.apiRequest_get(api)
        ssh_pwd = recvdata['data']['sshPassword']
        print "ssh pwd is %s"%ssh_pwd
        return ssh_pwd

    #获取国家信息
    def get_countryDomain(self):
        api = self.loadApi()['sysSettingShow']
        request = PublicControl(self.s)
        recvdata = request.apiRequest_get(api)
        countryDomain = recvdata['data']['countryDomain']
        print "countryDomain is %s"%countryDomain
        return countryDomain

    #获取时区
    def get_timezone(self):
        api = self.loadApi()['sysSettingShow']
        request = PublicControl(self.s)
        recvdata = request.apiRequest_get(api)
        timezone = recvdata['data']['timezone']
        print "timezone is %s"%timezone
        return timezone


    #设置保存
    def set_setting(self, data_dict):
        country = self.get_countryDomain()
        timezone = self.get_timezone()
        sshPassword = self.get_ssh_pwd()
        #配置替换
        dict1 = {'countryDomain':country,
                    'led':1,
                    'schedule':"",
                    'sshPassword':sshPassword,
                    'timezone':timezone,
                    'dfs':1,
                    'outdoor':"0",
                    'reboot':"0"
                 }
        dict2 = self.replaceConfig(dict1, data_dict)
        api = self.loadApi()['sysSettingSave']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,dict2)
        return recvdata
