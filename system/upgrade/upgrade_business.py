#coding=utf-8
#作者：曾祥卫
#时间：2018.06.12
#描述：cloud system-upgrade的业务层


from upgrade_control import UpgradeControl
from connect.ssh import SSH
from data import data
import time, subprocess

data_basic = data.data_basic()
data_ap = data.data_AP()

class UpgradeBusiness(UpgradeControl):

    def __init__(self, s):
        #继承UpgradeControl类的属性和方法
        UpgradeControl.__init__(self, s)


    #将三个ap立即降级并检查是否降级成功
    def check_ap_downgrade_now(self):
        #选择现在时间升级ap
        self.set_ap_upgrade_now("GWN7610", data_basic['7610_old_version'], \
            data_ap['7610_mac'], data_basic['Cloud_ssh_ip'], \
            data_basic['Cloud_ssh_user'], data_basic['Cloud_ssh_pwd'])
        self.set_ap_upgrade_now("GWN7600", data_basic['7600_old_version'], \
            data_ap['7600_mac'], data_basic['Cloud_ssh_ip'], \
            data_basic['Cloud_ssh_user'], data_basic['Cloud_ssh_pwd'])
        self.set_ap_upgrade_now("GWN7600LR", data_basic['7600_old_version'], \
            data_ap['7600lr_mac'], data_basic['Cloud_ssh_ip'], \
            data_basic['Cloud_ssh_user'], data_basic['Cloud_ssh_pwd'])
        time.sleep(900)
        #获取ap当前的版本
        version_7610 = self.get_ap_current_version(data_ap['7610_mac'])
        version_7600 = self.get_ap_current_version(data_ap['7600_mac'])
        version_7600lr = self.get_ap_current_version(data_ap['7600lr_mac'])
        print("7610's version is {}".format(version_7610))
        print("7600's version is {}".format(version_7600))
        print("7600lr's version is {}".format(version_7600lr))
        if (version_7610 == data_basic['7610_old_version']) and \
            (version_7600 == data_basic['7600_old_version']) and \
            (version_7600lr == data_basic['7600_old_version']):
            return True
        else:
            return False


    #将三个ap立即升级并检查是否升级成功
    def check_ap_upgrade_now(self):
        #选择现在时间升级ap
        self.set_ap_upgrade_now("GWN7610", data_basic['7610_new_version'], \
            data_ap['7610_mac'], data_basic['Cloud_ssh_ip'], \
            data_basic['Cloud_ssh_user'], data_basic['Cloud_ssh_pwd'])
        self.set_ap_upgrade_now("GWN7600", data_basic['7600_new_version'], \
            data_ap['7600_mac'], data_basic['Cloud_ssh_ip'], \
            data_basic['Cloud_ssh_user'], data_basic['Cloud_ssh_pwd'])
        self.set_ap_upgrade_now("GWN7600LR", data_basic['7600_new_version'], \
            data_ap['7600lr_mac'], data_basic['Cloud_ssh_ip'], \
            data_basic['Cloud_ssh_user'], data_basic['Cloud_ssh_pwd'])
        time.sleep(900)
        #获取ap当前的版本
        version_7610 = self.get_ap_current_version(data_ap['7610_mac'])
        version_7600 = self.get_ap_current_version(data_ap['7600_mac'])
        version_7600lr = self.get_ap_current_version(data_ap['7600lr_mac'])
        print("7610's version is {}".format(version_7610))
        print("7600's version is {}".format(version_7600))
        print("7600lr's version is {}".format(version_7600lr))
        if (version_7610 == data_basic['7610_new_version']) and \
            (version_7600 == data_basic['7600_new_version']) and \
            (version_7600lr == data_basic['7600_new_version']):
            return True
        else:
            return False

