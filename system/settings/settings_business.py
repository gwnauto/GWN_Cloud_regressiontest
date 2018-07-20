#coding=utf-8
#作者：曾祥卫
#时间：2018.03.20
#描述：cloud系统设置-设置的业务层


from settings_control import SettingsControl
from connect.ssh import SSH
from data import data
import time

data_basic = data.data_basic()

class SettingsBusiness(SettingsControl):

    def __init__(self, s):
        #继承SettingsControl类的属性和方法
        SettingsControl.__init__(self, s)

    #在AP CLI下查看国家默认配置
    def get_cli_country(self, host, user, pwd):
        ssh = SSH(host, pwd)
        result = ssh.ssh_cmd(user, "cat /etc/config/grandstream |grep country")
        return result

    #在AP CLI下查看无线ath0国家默认配置
    def get_cli_ath0_country(self, host, user, pwd):
        ssh = SSH(host, pwd)
        result = ssh.ssh_cmd(user, "iwpriv ath0 get_countrycode")
        return result

    #在AP CLI下查看无线ath1国家默认配置
    def get_cli_ath1_country(self, host, user, pwd):
        ssh = SSH(host, pwd)
        result = ssh.ssh_cmd(user, "iwpriv ath1 get_countrycode")
        return result

    #获取ap cli的时区
    def get_cli_timezone(self, host, user, pwd):
        ssh = SSH(host, pwd)
        result = ssh.ssh_cmd(user, "date -R")
        return result

    #获取ap cli密码
    def get_cli_ssh_password(self, host, user, pwd):
        ssh = SSH(host, pwd)
        result = ssh.ssh_cmd(user, "uci show grandstream.general.admin_password")
        return result