#coding=utf-8
#作者：曾祥卫
#时间：2018.06.12
#描述：system-upgrade用例集，调用upgrade_business

import unittest, time
from access_points.aps_business import APSBusiness
from system.settings.settings_business import SettingsBusiness
from clients.clients_business import Clients_Business
from system.upgrade.upgrade_business import UpgradeBusiness
from data import data
from data.logfile import Log
import requests
log = Log("upgrade")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()




class TestUpgrade(unittest.TestCase):
    u"""测试system-upgrade的用例集(runtime:0.44h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = Clients_Business(self.s)
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])



    #cloud添加三种型号的ap，并判断是否添加成功
    def test_001_add_3_model_aps_2_cloud(self):
        u"""cloud添加三种型号的ap，并判断是否添加成功(testlinkID:691-1)"""
        log.debug("001")
        tmp = APSBusiness(self.s)
        #描述：启用无线网卡
        tmp.wlan_enable(data_basic['wlan_pc'])
        tmp.dhcp_release_wlan(data_basic['wlan_pc'])
        #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
        tmp.add_ap_2_local_cloud(data_basic['7610_ip'], data_ap['7610_mac'], "autotest_7610")
        tmp.add_ap_2_local_cloud(data_basic['7600_ip'], data_ap['7600_mac'], "autotest_7600")
        tmp.add_ap_2_local_cloud(data_basic['7600lr_ip'], data_ap['7600lr_mac'], "autotest_7600lr")
        #cloud上获取该网络组的ssh密码
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        #判断ap是否已经和cloud配对上
        result1 = tmp.check_ap_pair_cloud(data_basic['7610_ip'],
                    data_basic['sshUser'], ssh_pwd)
        result2 = tmp.check_ap_pair_cloud(data_basic['7600_ip'],
                    data_basic['sshUser'], ssh_pwd)
        result3 = tmp.check_ap_pair_cloud(data_basic['7600lr_ip'],
                    data_basic['sshUser'], ssh_pwd)
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        print "add 3 model aps to cloud pass!"

    #将三个ap立即降级并检查是否降级成功
    def test_002_check_ap_downgrade_now(self):
        u"""将三个ap立即降级并检查是否降级成功"""
        log.debug("002")
        tmp = UpgradeBusiness(self.s)
        result = tmp.check_ap_downgrade_now()
        self.assertTrue(result)

    #将三个ap立即升级并检查是否升级成功
    def test_003_check_ap_upgrade_now(self):
        u"""将三个ap立即升级并检查是否升级成功"""
        log.debug("003")
        tmp = UpgradeBusiness(self.s)
        result = tmp.check_ap_upgrade_now()
        self.assertTrue(result)



    #删除ap，并恢复cloud的初始环境
    def test_004_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("004")
        #测试完后恢复初始环境
        #删除三个ap
        tmp = APSBusiness(self.s)
        tmp.dhcp_release_wlan(data_basic['wlan_pc'])
        tmp.disconnect_ap()
        tmp.delete_ap(data_ap['7610_mac'])
        tmp.delete_ap(data_ap['7600_mac'])
        tmp.delete_ap(data_ap['7600lr_mac'])
        time.sleep(360)



    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
