#coding=utf-8
#作者：曾祥卫
#时间：2018.06.12
#描述：navbar-user用例集，调用user_business

import unittest, time
from navbar.user.user_business import UserBusiness
from dashboard.network_list.networklist_business import NetworkListBusiness
from access_points.aps_business import APSBusiness
from system.settings.settings_business import SettingsBusiness
from ssids.ssids_business import SSIDSBusiness
from clients.clients_business import Clients_Business
from system.upgrade.upgrade_business import UpgradeBusiness
from data import data
from data.logfile import Log
import requests
log = Log("user")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()




class TestUser(unittest.TestCase):
    u"""测试navbar-user的用例集(runtime:0.39h)"""
    def setUp(self):
        self.s = requests.session()

    #平台管理员-能添加ap
    def test_001_Platform_Administrator_add_ap(self):
        u"""平台管理员-能添加ap"""
        log.debug("001")
        tmp1 = NetworkListBusiness(self.s)
        #描述：启用无线网卡
        tmp1.wlan_enable(data_basic['wlan_pc'])
        tmp1.dhcp_release_wlan(data_basic['wlan_pc'])
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp1.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取默认网络组default的id
        networkid = tmp1.get_network_id("default")
        time.sleep(60)
        tmp = UserBusiness(self.s)
        #修改测试用户为平台管理员
        tmp.set_user_authority(data_basic['Cloud_test_user'], \
            data_basic['Cloud_test_email'], "Platform Administrator", [networkid])
        time.sleep(60)
        #admin用户退出登录
        tmp.webLogout()
        #使用测试用户登录
        tmp2 = APSBusiness(self.s)
        tmp2.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        #添加ap-7610
        #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
        tmp2.add_ap_2_local_cloud(data_basic['7610_ip'], data_ap['7610_mac'], "autotest_7610")
        #cloud上获取该网络组的ssh密码
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        #判断ap是否已经和cloud配对上
        result = tmp2.check_ap_pair_cloud(data_basic['7610_ip'],
                    data_basic['sshUser'], ssh_pwd)
        self.assertTrue(result)

    #平台管理员-修改ssid
    def test_002_Platform_Administrator_edit_ssid(self):
        u"""平台管理员-修改ssid"""
        log.debug("002")
        #修改ssid
        tmp = SSIDSBusiness(self.s)
        #使用测试用户登录
        tmp.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        time.sleep(180)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['all_ssid']}
        tmp.edit_ssid(data_ap['7610_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(120)
        #获取修改后的ssid
        ssid = tmp.get_ssid_info(data_wireless['all_ssid'])['ssid']
        self.assertEqual(ssid, data_wireless['all_ssid'])

    #平台管理员-无线网卡能连接
    def test_003_Platform_Administrator_client_connect_ssid(self):
        u"""平台管理员-无线网卡能连接"""
        log.debug("003")
        tmp = SSIDSBusiness(self.s)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #平台管理员-添加网络组
    def test_004_Platform_Administrator_add_network(self):
        u"""平台管理员-添加网络组"""
        log.debug("004")
        #获取登录名对应的id
        tmp1 =UserBusiness(self.s)
        #使用测试用户登录
        tmp1.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        user_id = tmp1.get_network_id(data_basic['Cloud_test_user'])
        tmp = NetworkListBusiness(self.s)
        #添加网络组
        tmp.add_network("group1", user_id, "")
        time.sleep(60)
        #获取网络组对应的id--监控面板--网络列表
        network_id = tmp.get_network_id("group1")
        self.assertNotEqual(network_id, None)

    #平台管理员-删除网路组
    def test_005_Platform_Administrator_delete_network(self):
        u"""平台管理员-删除网路组"""
        log.debug("005")
        #删除网络组group1
        tmp = NetworkListBusiness(self.s)
        #使用测试用户登录
        tmp.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        tmp.delete_network("group1")
        time.sleep(60)
        #获取网络组对应的id--监控面板--网络列表
        network_id = tmp.get_network_id("group1")
        self.assertEqual(network_id, None)

    #平台管理员-删除ap
    def test_006_Platform_Administrator_delete_ap(self):
        u"""平台管理员-删除ap"""
        log.debug("006")
        tmp = APSBusiness(self.s)
        #使用测试用户登录
        tmp.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        tmp.delete_ap(data_ap['7610_mac'])
        time.sleep(360)
        #判断ap是否是在出厂值状态
        result = tmp.check_ap_factory(data_basic['7610_ip'])
        self.assertTrue(result)

    #网络管理员-能添加ap
    def test_007_Network_Administrator_add_ap(self):
        u"""网络管理员-能添加ap"""
        log.debug("007")
        tmp1 = NetworkListBusiness(self.s)
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp1.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取默认网络组default的id
        networkid = tmp1.get_network_id("default")
        time.sleep(60)
        tmp = UserBusiness(self.s)
        #修改测试用户为网络管理员
        tmp.set_user_authority(data_basic['Cloud_test_user'], \
            data_basic['Cloud_test_email'], "Network Administrator", [networkid])
        time.sleep(60)
        #admin用户退出登录
        tmp.webLogout()
        #使用测试用户登录
        tmp2 = APSBusiness(self.s)
        tmp2.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        #添加ap-7610
        #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
        tmp2.add_ap_2_local_cloud(data_basic['7610_ip'], data_ap['7610_mac'], "autotest_7610")
        #cloud上获取该网络组的ssh密码
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        #判断ap是否已经和cloud配对上
        result = tmp2.check_ap_pair_cloud(data_basic['7610_ip'],
                    data_basic['sshUser'], ssh_pwd)
        self.assertTrue(result)

    #网络管理员-修改ssid
    def test_008_Network_Administrator_edit_ssid(self):
        u"""网络管理员-修改ssid"""
        log.debug("008")
        #修改ssid
        tmp = SSIDSBusiness(self.s)
        #使用测试用户登录
        tmp.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        time.sleep(180)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['all_ssid']+"NW"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #获取修改后的ssid
        ssid = tmp.get_ssid_info(data_wireless['all_ssid']+"NW")['ssid']
        self.assertEqual(ssid, data_wireless['all_ssid']+"NW")

    #网络管理员-无线网卡能连接
    def test_009_Network_Administrator_client_connect_ssid(self):
        u"""网络管理员-无线网卡能连接"""
        log.debug("009")
        tmp = SSIDSBusiness(self.s)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid']+"NW",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp.dhcp_release_wlan(data_basic['wlan_pc'])
        tmp.disconnect_ap()
        self.assertIn(data_wireless['all_ssid']+"NW", result)

    #网络管理员-删除ap
    def test_010_Network_Administrator_delete_ap(self):
        u"""网络管理员-删除ap"""
        log.debug("010")
        tmp = APSBusiness(self.s)
        #使用测试用户登录
        tmp.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        tmp.delete_ap(data_ap['7610_mac'])
        time.sleep(360)
        #判断ap是否是在出厂值状态
        result = tmp.check_ap_factory(data_basic['7610_ip'])
        self.assertTrue(result)

    #网络管理员-不能添加网络组
    def test_011_Network_Administrator_add_network(self):
        u"""网络管理员-不能添加网络组"""
        log.debug("011")
        #获取登录名对应的id
        tmp1 =UserBusiness(self.s)
        #使用测试用户登录
        tmp1.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        user_id = tmp1.get_network_id(data_basic['Cloud_test_user'])
        tmp = NetworkListBusiness(self.s)
        #添加网络组
        result = tmp.add_network("group1", user_id, "")
        self.assertFalse(result)

    #访客管理员-不能添加ap
    def test_012_Guest_Editor_add_ap(self):
        u"""访客管理员-不能添加ap"""
        log.debug("012")
        tmp1 = NetworkListBusiness(self.s)
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp1.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        time.sleep(60)
        #获取默认网络组default的id
        networkid = tmp1.get_network_id("default")
        tmp = UserBusiness(self.s)
        #修改测试用户为访客管理员
        tmp.set_user_authority(data_basic['Cloud_test_user'], \
            data_basic['Cloud_test_email'], "Guest Editor", [networkid])
        time.sleep(60)
        #admin用户退出登录
        tmp.webLogout()
        #使用测试用户登录
        tmp2 = APSBusiness(self.s)
        tmp2.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        #添加ap-7610
        result = tmp2.add_ap_2_local_cloud(data_basic['7610_ip'], data_ap['7610_mac'], "autotest_7610")
        self.assertFalse(result)

    #访客管理员-不能修改ssid
    def test_013_Guest_Editor_edit_ssid(self):
        u"""访客管理员-不能修改ssid"""
        log.debug("013")
        #修改ssid
        tmp = SSIDSBusiness(self.s)
        #使用测试用户登录
        tmp.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        result = tmp.add_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"GE",\
                              data_wireless['short_wpa'])
        self.assertFalse(result)

    #访客管理员-不能添加网络组
    def test_014_Guest_Editor_add_network(self):
        u"""访客管理员-不能添加网络组"""
        log.debug("014")
        #获取登录名对应的id
        tmp1 =UserBusiness(self.s)
        #使用admin登录
        tmp1.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        time.sleep(60)
        user_id = tmp1.get_network_id(data_basic['Cloud_test_user'])
        #admin用户退出登录
        tmp1.webLogout()
        #使用测试用户登录
        tmp1.webLogin(data_basic['Cloud_test_user'], data_basic['Cloud_test_pwd'])
        tmp = NetworkListBusiness(self.s)
        #添加网络组
        result = tmp.add_network("group1", user_id, "")
        self.assertFalse(result)

    #恢复cloud的初始环境
    def test_015_reset_cloud(self):
        u"""恢复cloud的初始环境"""
        log.debug("015")
        #测试完后恢复初始环境
        #1.修改ap的ssid为GWN-Cloud
        tmp1 = SSIDSBusiness(self.s)
        tmp1.dhcp_release_wlan(data_basic['wlan_pc'])
        tmp1.disconnect_ap()
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp1.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': "GWN-Cloud",
                     'ssid_ssid_band': ""}
        tmp1.edit_ssid("", data_wireless['all_ssid']+"NW",
                       encry_dict, data_dict)
        time.sleep(120)








    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
