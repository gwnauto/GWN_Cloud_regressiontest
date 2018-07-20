#coding=utf-8
#作者：曾祥卫
#时间：2018.05.31
#描述：Network-system-settings用例集，调用settings_business

import unittest, time, subprocess
from access_points.aps_business import APSBusiness
from system.settings.settings_business import SettingsBusiness
from ssids.ssids_business import SSIDSBusiness
from clients.clients_business import Clients_Business
from access_control.access_list.accesslist_business import AccessListBusiness
from access_control.time_policy.timepolicy_business import TimePolicyBusiness
from data import data
from connect.ssh import SSH
from data.logfile import Log
import requests
log = Log("settings")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()




class TestSettings(unittest.TestCase):
    u"""测试Network-system-settings的用例集(runtime:1h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = SettingsBusiness(self.s)
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

    #国家检查默认配置
    def test_002_check_country_default_setting(self):
        u"""国家检查默认配置(testlink_ID:1623)"""
        log.debug("002")
        tmp = SettingsBusiness(self.s)
        #获取默认国家信息
        country = tmp.get_countryDomain()
        #在AP CLI下查看国家默认配置
        ssh_pwd = tmp.get_ssh_pwd()
        result_7600 = tmp.get_cli_country(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd)
        result_7610 = tmp.get_cli_country(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd)
        result_7600lr = tmp.get_cli_country(data_basic['7600lr_ip'],
                data_basic['sshUser'], ssh_pwd)
        self.assertEqual("US", country)
        self.assertIn("840", result_7600)
        self.assertIn("840", result_7610)
        self.assertIn("840", result_7600lr)

    #验证修改国家配置是否生效
    def test_003_change_country_setting(self):
        u"""验证修改国家配置是否生效(testlink_ID:1624)"""
        log.debug("003")
        tmp = SettingsBusiness(self.s)
        #修改国家为中国
        tmp.set_setting({'countryDomain':"CN"})
        time.sleep(60)
        #在AP CLI下查看国家默认配置
        ssh_pwd = tmp.get_ssh_pwd()
        result1 = tmp.get_cli_country(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd)
        result2 = tmp.get_cli_ath0_country(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd)
        result3 = tmp.get_cli_ath1_country(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd)
        self.assertIn("156", result1)
        self.assertIn("156", result2)
        self.assertIn("156", result3)

    #页面重启验证国家
    def test_004_reboot_ap_check_country(self):
        u"""页面重启验证国家(testlink_ID:1626)"""
        log.debug("004")
        #重启7600
        tmp1 = APSBusiness(self.s)
        tmp1.reboot_one_ap(data_ap['7600_mac'])
        time.sleep(420)
        tmp = SettingsBusiness(self.s)
        #在AP CLI下查看国家默认配置
        ssh_pwd = tmp.get_ssh_pwd()
        result = tmp.get_cli_country(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd)
        self.assertIn("156", result)

    #重置验证国家
    def test_005_reset_ap_check_country(self):
        u"""重置验证国家(testlink_ID:1628)"""
        log.debug("005")
        #删除7600
        tmp1 = APSBusiness(self.s)
        tmp1.delete_ap(data_ap['7600_mac'])
        time.sleep(360)
        tmp = SettingsBusiness(self.s)
        result = tmp.get_cli_country(data_basic['7600_ip'],
                data_basic['sshUser'], "admin")
        self.assertIn("840", result)

    #重启AP之后查看时区
    def test_006_reboot_ap_check_timezone(self):
        u"""重启AP之后查看时区(testlink_ID:1642)"""
        log.debug("006")
        #7600再添加回cloud
        tmp1 = APSBusiness(self.s)
        tmp1.add_ap_2_local_cloud(data_basic['7600_ip'], data_ap['7600_mac'], "autotest_7600")
        #修改时区为北京
        tmp = SettingsBusiness(self.s)
        tmp.set_setting({'timezone':"Asia/Shanghai"})
        time.sleep(60)
        #然后重启7600
        tmp1.reboot_one_ap(data_ap['7600_mac'])
        time.sleep(420)
        #获取ap cli的时区
        ssh_pwd = tmp.get_ssh_pwd()
        result = tmp.get_cli_timezone(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd)
        self.assertIn("+0800", result)

    #AP离线时配置时区
    def test_007_offline_ap_check_timezone(self):
        u"""AP离线时配置时区(testlink_ID:1643)"""
        log.debug("007")
        #重启7600
        tmp1 = APSBusiness(self.s)
        tmp1.reboot_one_ap(data_ap['7600_mac'])
        time.sleep(100)
        #修改时区为GWT
        tmp = SettingsBusiness(self.s)
        tmp.set_setting({'timezone':"Etc/GMT"})
        time.sleep(320)
        #获取ap cli的时区
        ssh_pwd = tmp.get_ssh_pwd()
        result = tmp.get_cli_timezone(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd)
        self.assertIn("+0000", result)

    #纯数字SSH密码检测
    def test_008_sshPassword_digital(self):
        u"""纯数字SSH密码检测(testlink_ID:1646,1649)"""
        log.debug("008")
        tmp = SettingsBusiness(self.s)
        #获取默认ssh password
        default_ssh_password = tmp.get_ssh_pwd()
        #修改ssh 密码为纯数字
        tmp.set_setting({'sshPassword':"12345678"})
        time.sleep(60)
        #在AP CLI下查看国家默认配置
        result1 = tmp.get_cli_ssh_password(data_basic['7600_ip'],
                data_basic['sshUser'], "12345678")
        result2 = tmp.get_cli_ssh_password(data_basic['7600lr_ip'],
                data_basic['sshUser'], "12345678")
        result3 = tmp.get_cli_ssh_password(data_basic['7610_ip'],
                data_basic['sshUser'], "12345678")
        #把ssh 密码为默认
        tmp.set_setting({'sshPassword':default_ssh_password})
        time.sleep(60)
        self.assertIn("12345678", result1)
        self.assertIn("12345678", result2)
        self.assertIn("12345678", result3)

    #纯字母SSH密码检测
    def test_009_sshPassword_letter(self):
        u"""纯字母SSH密码检测(testlink_ID:1647,1650)"""
        log.debug("009")
        tmp = SettingsBusiness(self.s)
        #获取默认ssh password
        default_ssh_password = tmp.get_ssh_pwd()
        #修改ssh 密码为纯数字
        tmp.set_setting({'sshPassword':"abcdefgh"})
        time.sleep(60)
        #在AP CLI下查看国家默认配置
        result1 = tmp.get_cli_ssh_password(data_basic['7600_ip'],
                data_basic['sshUser'], "abcdefgh")
        result2 = tmp.get_cli_ssh_password(data_basic['7600lr_ip'],
                data_basic['sshUser'], "abcdefgh")
        result3 = tmp.get_cli_ssh_password(data_basic['7610_ip'],
                data_basic['sshUser'], "abcdefgh")
        #把ssh 密码为默认
        tmp.set_setting({'sshPassword':default_ssh_password})
        time.sleep(60)
        self.assertIn("abcdefgh", result1)
        self.assertIn("abcdefgh", result2)
        self.assertIn("abcdefgh", result3)

    #字母和数字组合SSH密码检测
    def test_010_sshPassword_letter_and_digital(self):
        u"""字母和数字组合SSH密码检测(testlink_ID:1648,1651)"""
        log.debug("010")
        tmp = SettingsBusiness(self.s)
        #获取默认ssh password
        default_ssh_password = tmp.get_ssh_pwd()
        #修改ssh 密码为纯数字
        tmp.set_setting({'sshPassword':"abcd1234"})
        time.sleep(60)
        #在AP CLI下查看国家默认配置
        result1 = tmp.get_cli_ssh_password(data_basic['7600_ip'],
                data_basic['sshUser'], "abcd1234")
        result2 = tmp.get_cli_ssh_password(data_basic['7600lr_ip'],
                data_basic['sshUser'], "abcd1234")
        result3 = tmp.get_cli_ssh_password(data_basic['7610_ip'],
                data_basic['sshUser'], "abcd1234")
        #把ssh 密码为默认
        tmp.set_setting({'sshPassword':default_ssh_password})
        time.sleep(60)
        self.assertIn("abcd1234", result1)
        self.assertIn("abcd1234", result2)
        self.assertIn("abcd1234", result3)

    #错误SSH密码登录失败验证
    def test_011_error_password(self):
        u"""错误SSH密码登录失败验证(testlink_ID:1653)"""
        log.debug("011")
        tmp = SettingsBusiness(self.s)
        result = tmp.get_cli_ssh_password(data_basic['7600_ip'],
                data_basic['sshUser'], "12345678")
        self.assertNotIn("12345678", result)

    #设备重启后，SSH登录验证
    def test_012_reboot_ap_check_ssh_password(self):
        u"""设备重启后，SSH登录验证(testlink_ID:1657)"""
        log.debug("012")
        tmp = SettingsBusiness(self.s)
        #获取默认ssh password
        default_ssh_password = tmp.get_ssh_pwd()
        #修改ssh 密码为纯数字
        tmp.set_setting({'sshPassword':"abcdefgh"})
        time.sleep(60)
        tmp1 = APSBusiness(self.s)
        tmp1.reboot_many_aps(data_ap['7610_mac'], data_ap['7600_mac'], data_ap['7600lr_mac'])
        time.sleep(420)
        #在AP CLI下查看国家默认配置
        result1 = tmp.get_cli_ssh_password(data_basic['7600_ip'],
                data_basic['sshUser'], "abcdefgh")
        result2 = tmp.get_cli_ssh_password(data_basic['7600lr_ip'],
                data_basic['sshUser'], "abcdefgh")
        result3 = tmp.get_cli_ssh_password(data_basic['7610_ip'],
                data_basic['sshUser'], "abcdefgh")
        #把ssh 密码为默认
        tmp.set_setting({'sshPassword':default_ssh_password,
                         'countryDomain':"US"})
        time.sleep(60)
        self.assertIn("abcdefgh", result1)
        self.assertIn("abcdefgh", result2)
        self.assertIn("abcdefgh", result3)

    #删除ap，并恢复cloud的初始环境
    def test_013_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("013")
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
