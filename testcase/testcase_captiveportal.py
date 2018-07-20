#coding=utf-8
#作者：曾祥卫
#时间：2018.07.10
#描述：Network-captive portal用例集

import unittest, time, subprocess
from access_points.aps_business import APSBusiness
from system.settings.settings_business import SettingsBusiness
from ssids.ssids_business import SSIDSBusiness
from clients.clients_business import Clients_Business
from captive_portal.captiveportal_business import CPBusiness
from captive_portal.policy_list.policylist_business import PolicyListBusiness
from captive_portal.vouchers.vouchers_business import VouchersBusiness
from captive_portal.summary.summary_business import SummaryBusiness
from captive_portal.guest.guest_business import GuestBusiness
from data import data
from connect.ssh import SSH
from data.logfile import Log
import requests


log = Log("captiveportal")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()



class TestCP(unittest.TestCase):
    u"""测试Network-captive portal的用例集(runtime:13.18h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = CPBusiness(self.s)
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


    #验证Captive Portal一键开启，Portal能生效
    def test_002_open_portal_function(self):
        u"""验证Captive Portal一键开启，Portal能生效(testlinkID:1017)"""
        log.debug("002")
        #新建一个policy list,并获取该list的id
        tmp1 = PolicyListBusiness(self.s)
        list_id = tmp1.add_policylist("List1", 120, data_basic['splashpage_name'])
        time.sleep(10)
        #ssid修改
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['all_ssid'],
                     'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(list_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        self.assertTrue(result, msg="check portal function fail!")

    #验证无线不加密Captive Portal一键开启，Portal能生效
    def test_003_NoneEncryption_open_portal_function(self):
        u"""验证无线不加密Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("003")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为无线不加密
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "open")
        self.assertTrue(result, msg="check NoneEncryption portal function fail!")

    #验证WEP-64bitCaptive Portal一键开启，Portal能生效
    def test_004_wep64bit_open_portal_function(self):
        u"""验证WEP-64bitCaptive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("004")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-64bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", data_wireless['wep64'])
        self.assertTrue(result, msg="check WEP-64bit portal function fail!")

    #验证WEP-128bitCaptive Portal一键开启，Portal能生效
    def test_005_wep128bit_open_portal_function(self):
        u"""验证WEP-128bitCaptive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("005")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-128bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", data_wireless['wep128'])
        self.assertTrue(result, msg="check WEP-128bit portal function fail!")

    #验证WPA/WPA2-PSK AES Captive Portal一键开启，Portal能生效
    def test_006_wpa_aes_open_portal_function(self):
        u"""验证WPA/WPA2-PSK AES Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("006")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        self.assertTrue(result, msg="check WPA/WPA2-PSK AES portal function fail!")


    #验证WPA/WPA2-PSK AES long pwd Captive Portal一键开启，Portal能生效
    def test_007_wpa_aes_longpwd_open_portal_function(self):
        u"""验证WPA/WPA2-PSK AES long pwd Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("007")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['long_wpa'])
        self.assertTrue(result, msg="check WPA/WPA2-PSK AES long pwd portal function fail!")


    #验证WPA/WPA2 AES/TKIP Captive Portal一键开启，Portal能生效
    def test_008_wpa_tkip_open_portal_function(self):
        u"""验证WPA/WPA2 AES/TKIP Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("008")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        self.assertTrue(result, msg="check WPA/WPA2 AES/TKIP portal function fail!")

    #验证WPA/WPA2 AES/TKIP long pwd Captive Portal一键开启，Portal能生效
    def test_009_wpa_tkip_longpwd_open_portal_function(self):
        u"""验证WPA/WPA2 AES/TKIP long pwd Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("009")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['long_wpa'])
        self.assertTrue(result, msg="check WPA/WPA2-PSK AES/TKIP long pwd portal function fail!")

    #验证WPA2 AES Captive Portal一键开启，Portal能生效
    def test_010_wpa2_aes_open_portal_function(self):
        u"""验证WPA2 AES Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("010")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        self.assertTrue(result, msg="check WPA2 AES portal function fail!")

    #验证WPA2 AES long pwd Captive Portal一键开启，Portal能生效
    def test_011_wpa2_aes_longpwd_open_portal_function(self):
        u"""验证WPA2 AES long pwd Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("011")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['long_wpa'])
        self.assertTrue(result, msg="check WPA2 AES long pwd portal function fail!")

    #验证WPA2 AES/TKIP Captive Portal一键开启，Portal能生效
    def test_012_wpa2_tkip_open_portal_function(self):
        u"""验证WPA2 AES/TKIP Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("010")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        self.assertTrue(result, msg="check WPA2 AES/TKIP portal function fail!")

    #验证WPA2 AES/TKIP long pwd Captive Portal一键开启，Portal能生效
    def test_013_wpa2_tkip_longpwd_open_portal_function(self):
        u"""验证WPA2 AES/TKIP long pwd Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("013")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['long_wpa'])
        self.assertTrue(result, msg="check WPA2 AES/TKIP long pwd portal function fail!")

    #验证WPA/WPA2-802.1x AES Captive Portal一键开启，Portal能生效
    def test_014_wpa_8021x_open_portal_function(self):
        u"""验证WPA/WPA2-802.1x AES Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("014")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x")
        self.assertTrue(result, msg="check WPA/WPA2-802.1x AES portal function fail!")

    #验证WPA/WPA2-802.1x AES/TKIP Captive Portal一键开启，Portal能生效
    def test_015_wpa_8021x_open_portal_function(self):
        u"""验证WPA/WPA2-802.1x AES/TKIPCaptive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("015")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x")
        self.assertTrue(result, msg="check WPA/WPA2-802.1x AES/TKIP portal function fail!")

    #验证WPA2-802.1x AES Captive Portal一键开启，Portal能生效
    def test_016_wpa2_8021x_open_portal_function(self):
        u"""验证WPA2-802.1x AES Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("016")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x")
        self.assertTrue(result, msg="check WPA2-802.1x AES portal function fail!")

    #验证WPA2-802.1x AES/TKIP Captive Portal一键开启，Portal能生效
    def test_017_wpa2_8021x_open_portal_function(self):
        u"""验证WPA2-802.1x AES/TKIP Captive Portal一键开启，Portal能生效(testlinkID:)"""
        log.debug("017")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面，判断是否跳转到portal页面
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        result = tmp3.check_jump_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x")
        self.assertTrue(result, msg="check WPA2-802.1x AES/TKIP portal function fail!")

    #验证无线不加密Captive Portal免认证功能生效
    def test_018_NoEncryption_NoAuth_portal_access_portal(self):
        u"""验证无线不加密Captive Portal免认证功能生效(testlinkID:*)"""
        log.debug("018")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为无线不加密
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "open",title)
        self.assertNotIn(False, result)

    #验证WEP-64bit Captive Portal免认证功能生效
    def test_019_wep64bit_NoAuth_portal_access_portal(self):
        u"""验证WEP-64bit Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("019")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-64bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep",title, data_wireless['wep64'])
        self.assertNotIn(False, result)

    #验证WEP-128bit Captive Portal免认证功能生效
    def test_020_wep128bit_NoAuth_portal_access_portal(self):
        u"""验证WEP-128bit Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("020")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-128bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep",title, data_wireless['wep128'])
        self.assertNotIn(False, result)

    #验证WPA/WPA2-PSK AES Captive Portal免认证功能生效
    def test_021_wpa_aes_NoAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("021")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['short_wpa'])
        self.assertNotIn(False, result)

    #验证WPA/WPA2-PSK AES long pwd Captive Portal免认证功能生效
    def test_022_wpa_aes_longpwd_NoAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES long pwd Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("022")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['long_wpa'])
        self.assertNotIn(False, result)

    #验证WPA/WPA2 AES/TKIP Captive Portal免认证功能生效
    def test_023_wpa_tkip_NoAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("023")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['short_wpa'])
        self.assertNotIn(False, result)

    #验证WPA/WPA2 AES/TKIP long pwd Captive Portal免认证功能生效
    def test_024_wpa_tkip_longpwd_NoAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP long pwd Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("024")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['long_wpa'])
        self.assertNotIn(False, result)

    #验证WPA2 AES Captive Portal免认证功能生效
    def test_025_wpa2_aes_NoAuth_portal_access_portal(self):
        u"""验证WPA2 AES Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("025")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['short_wpa'])
        self.assertNotIn(False, result)

    #验证WPA2 AES long pwd Captive Portal免认证功能生效
    def test_026_wpa2_aes_NoAuth_portal_access_portal(self):
        u"""验证WPA2 AES long pwd Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("026")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['long_wpa'])
        self.assertNotIn(False, result)

    #验证WPA2 AES/TKIP Captive Portal免认证功能生效
    def test_027_wpa2_tkip_NoAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("027")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['short_wpa'])
        self.assertNotIn(False, result)

    #验证WPA2 AES/TKIP long pwd Captive Portal免认证功能生效
    def test_028_wpa2_tkip_NoAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP long pwd Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("028")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['long_wpa'])
        self.assertNotIn(False, result)

    #验证WPA/WPA2-802.1x AES Captive Portal免认证功能生效
    def test_029_wpa_8021x_NoAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("029")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x",title)
        self.assertNotIn(False, result)

    #验证WPA/WPA2-802.1x AES/TKIP Captive Portal免认证功能生效
    def test_030_wpa_8021x_NoAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES/TKIP Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("030")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
       #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x",title)
        self.assertNotIn(False, result)

    #验证WPA2-802.1x AES Captive Portal免认证功能生效
    def test_031_wpa2_8021x_NoAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("031")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x",title)
        self.assertNotIn(False, result)

    #验证WPA2-802.1x AES/TKIP Captive Portal免认证功能生效
    def test_032_wpa2_8021x_NoAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES/TKIP Captive Portal免认证功能生效(testlinkID:)"""
        log.debug("032")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x",title)
        self.assertNotIn(False, result)

    #验证无线不加密 Captive Portal密码认证功能生效
    def test_033_NoEncryption_PWDAuth_portal_access_portal(self):
        u"""验证无线不加密 Captive Portal密码认证功能生效(testlinkID:*)"""
        log.debug("033")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为无线不加密
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "open", data_basic["portal_pwd"],\
                        title)
        self.assertNotIn(False,result)

    #验证WEP-64bit Captive Portal密码认证功能生效
    def test_034_wep64bit_PWDAuth_portal_access_portal(self):
        u"""验证WEP-64bit Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("034")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-64bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", data_basic["portal_pwd"],\
                        title, data_wireless['wep64'])
        self.assertNotIn(False,result)

    #验证WEP-128bit Captive Portal密码认证功能生效
    def test_035_wep128bit_PWDAuth_portal_access_portal(self):
        u"""验证WEP-128bit Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("035")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-128bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", data_basic["portal_pwd"],\
                        title, data_wireless['wep128'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-PSK AES Captive Portal密码认证功能生效
    def test_036_wpa_aes_PWDAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("036")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-PSK AES long pwd Captive Portal密码认证功能生效
    def test_037_wpa_aes_longpwd_PWDAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES long pwd Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("037")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2 AES/TKIP Captive Portal密码认证功能生效
    def test_038_wpa_tkip_PWDAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("038")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2 AES/TKIP long pwd Captive Portal密码认证功能生效
    def test_039_wpa_tkip_longpwd_PWDAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP long pwd Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("039")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES Captive Portal密码认证功能生效
    def test_040_wpa2_aes_PWDAuth_portal_access_portal(self):
        u"""验证WPA2 AES Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("040")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES long pwd Captive Portal密码认证功能生效
    def test_041_wpa2_aes_PWDAuth_portal_access_portal(self):
        u"""验证WPA2 AES long pwd Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("041")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES/TKIP Captive Portal密码认证功能生效
    def test_042_wpa2_tkip_PWDAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("042")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES/TKIP long pwd Captive Portal密码认证功能生效
    def test_043_wpa2_tkip_PWDAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP long pwd Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("043")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-802.1x AES Captive Portal密码认证功能生效
    def test_044_wpa_8021x_PWDAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("044")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", data_basic["portal_pwd"],\
                        title)
        self.assertNotIn(False,result)

    #验证WPA/WPA2-802.1x AES/TKIP Captive Portal密码认证功能生效
    def test_045_wpa_8021x_PWDAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES/TKIP Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("045")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", data_basic["portal_pwd"],\
                        title)
        self.assertNotIn(False,result)

    #验证WPA2-802.1x AES Captive Portal密码认证功能生效
    def test_046_wpa2_8021x_PWDAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("046")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", data_basic["portal_pwd"],\
                        title)
        self.assertNotIn(False,result)

    #验证WPA2-802.1x AES/TKIP Captive Portal密码认证功能生效
    def test_047_wpa2_8021x_PWDAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES/TKIP Captive Portal密码认证功能生效(testlinkID:)"""
        log.debug("047")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", data_basic["portal_pwd"],\
                        title)
        self.assertNotIn(False,result)

    #验证无线不加密 Captive Portal帐号认证功能生效
    def test_048_NoEncryption_RadiusAuth_portal_access_portal(self):
        u"""验证无线不加密 Captive Portal帐号认证功能生效(testlinkID:*)"""
        log.debug("048")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为无线不加密
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "open", data_basic['radius_usename'],\
                        data_basic['radius_password'], title)
        self.assertNotIn(False,result)

    #验证WEP-64bit Captive Portal帐号认证功能生效
    def test_049_wep64bit_RadiusAuth_portal_access_portal(self):
        u"""验证WEP-64bit Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("049")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-64bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['wep64'])
        self.assertNotIn(False,result)

    #验证WEP-128bit Captive Portal帐号认证功能生效
    def test_050_wep128bit_RadiusAuth_portal_access_portal(self):
        u"""验证WEP-128bit Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("050")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-128bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['wep128'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-PSK AES Captive Portal帐号认证功能生效
    def test_051_wpa_aes_RadiusAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("051")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-PSK AES long pwd Captive Portal帐号认证功能生效
    def test_052_wpa_aes_longpwd_RadiusAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES long pwd Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("052")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2 AES/TKIP Captive Portal帐号认证功能生效
    def test_053_wpa_tkip_RadiusAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("053")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2 AES/TKIP long pwd Captive Portal帐号认证功能生效
    def test_054_wpa_tkip_longpwd_RadiusAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP long pwd Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("054")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES Captive Portal帐号认证功能生效
    def test_055_wpa2_aes_RadiusAuth_portal_access_portal(self):
        u"""验证WPA2 AES Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("055")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES long pwd Captive Portal帐号认证功能生效
    def test_056_wpa2_aes_RadiusAuth_portal_access_portal(self):
        u"""验证WPA2 AES long pwd Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("056")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES/TKIP Captive Portal帐号认证功能生效
    def test_057_wpa2_tkip_RadiusAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("057")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES/TKIP long pwd Captive Portal帐号认证功能生效
    def test_058_wpa2_tkip_RadiusAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP long pwd Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("058")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-802.1x AES Captive Portal帐号认证功能生效
    def test_059_wpa_8021x_RadiusAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("059")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", data_basic['radius_usename'],\
                        data_basic['radius_password'], title)
        self.assertNotIn(False,result)

    #验证WPA/WPA2-802.1x AES/TKIP Captive Portal帐号认证功能生效
    def test_060_wpa_8021x_RadiusAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES/TKIP Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("060")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", data_basic['radius_usename'],\
                        data_basic['radius_password'], title)
        self.assertNotIn(False,result)

    #验证WPA2-802.1x AES Captive Portal帐号认证功能生效
    def test_061_wpa2_8021x_RadiusAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("061")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", data_basic['radius_usename'],\
                        data_basic['radius_password'], title)
        self.assertNotIn(False,result)

    #验证WPA2-802.1x AES/TKIP Captive Portal帐号认证功能生效
    def test_062_wpa2_8021x_RadiusAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES/TKIP Captive Portal帐号认证功能生效(testlinkID:)"""
        log.debug("062")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", data_basic['radius_usename'],\
                        data_basic['radius_password'], title)
        self.assertNotIn(False,result)

    #验证无线不加密 Captive Portal微信认证功能生效
    def test_063_NoEncryption_WeChatAuth_portal_access_portal(self):
        u"""验证无线不加密 Captive Portal微信认证功能生效(testlinkID:*)"""
        log.debug("063")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为无线不加密
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "open", title)
        self.assertNotIn(False,result)

    #验证WEP-64bit Captive Portal微信认证功能生效
    def test_064_wep64bit_WeChatAuth_portal_access_portal(self):
        u"""验证WEP-64bit Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("064")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-64bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", title, data_wireless['wep64'])
        self.assertNotIn(False,result)

    #验证WEP-128bit Captive Portal微信认证功能生效
    def test_065_wep128bit_WeChatAuth_portal_access_portal(self):
        u"""验证WEP-128bit Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("065")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-128bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", title, data_wireless['wep128'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-PSK AES Captive Portal微信认证功能生效
    def test_066_wpa_aes_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("066")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-PSK AES long pwd Captive Portal微信认证功能生效
    def test_067_wpa_aes_longpwd_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES long pwd Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("067")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2 AES/TKIP Captive Portal微信认证功能生效
    def test_068_wpa_tkip_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("068")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2 AES/TKIP long pwd Captive Portal微信认证功能生效
    def test_069_wpa_tkip_longpwd_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP long pwd Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("069")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES Captive Portal微信认证功能生效
    def test_070_wpa2_aes_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2 AES Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("070")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES long pwd Captive Portal微信认证功能生效
    def test_071_wpa2_aes_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2 AES long pwd Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("071")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES/TKIP Captive Portal微信认证功能生效
    def test_072_wpa2_tkip_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("072")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES/TKIP long pwd Captive Portal微信认证功能生效
    def test_073_wpa2_tkip_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP long pwd Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("073")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-802.1x AES Captive Portal微信认证功能生效
    def test_074_wpa_8021x_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("074")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", title)
        self.assertNotIn(False,result)

    #验证WPA/WPA2-802.1x AES/TKIP Captive Portal微信认证功能生效
    def test_075_wpa_8021x_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES/TKIP Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("075")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                           data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", title)
        self.assertNotIn(False,result)

    #验证WPA2-802.1x AES Captive Portal微信认证功能生效
    def test_076_wpa2_8021x_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("076")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", title)
        self.assertNotIn(False,result)

    #验证WPA2-802.1x AES/TKIP Captive Portal微信认证功能生效
    def test_077_wpa2_8021x_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES/TKIP Captive Portal微信认证功能生效(testlinkID:)"""
        log.debug("077")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", title)
        self.assertNotIn(False,result)

    #验证无线不加密 Captive Portal凭据认证功能生效
    def test_078_NoEncryption_VouchersAuth_portal_access_portal(self):
        u"""验证无线不加密 Captive Portal凭据认证功能生效(testlinkID:*)"""
        log.debug("078")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为无线不加密
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #新建个凭据
        tmp4 = VouchersBusiness(self.s)
        tmp4.add_vouchers_list("Voucher_List1")
        time.sleep(30)
        #随机获取这个凭据组的一个密码
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "open", title, Voucher_password)
        self.assertNotIn(False,result)

    #验证WEP-64bit Captive Portal凭据认证功能生效
    def test_079_wep64bit_VouchersAuth_portal_access_portal(self):
        u"""验证WEP-64bit Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("079")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-64bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", title, \
                        Voucher_password, data_wireless['wep64'])
        self.assertNotIn(False,result)

    #验证WEP-128bit Captive Portal凭据认证功能生效
    def test_080_wep128bit_WeChatAuth_portal_access_portal(self):
        u"""验证WEP-128bit Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("080")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WEP-128bit
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wep", title, \
                        Voucher_password, data_wireless['wep128'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-PSK AES Captive Portal凭据认证功能生效
    def test_081_wpa_aes_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("081")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-PSK AES long pwd Captive Portal凭据认证功能生效
    def test_082_wpa_aes_longpwd_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-PSK AES long pwd Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("082")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-PSK AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2 AES/TKIP Captive Portal凭据认证功能生效
    def test_083_wpa_tkip_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("083")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2 AES/TKIP long pwd Captive Portal凭据认证功能生效
    def test_084_wpa_tkip_longpwd_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2 AES/TKIP long pwd Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("084")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES Captive Portal凭据认证功能生效
    def test_085_wpa2_aes_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2 AES Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("085")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES long pwd Captive Portal凭据认证功能生效
    def test_086_wpa2_aes_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2 AES long pwd Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("086")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES/TKIP Captive Portal凭据认证功能生效
    def test_087_wpa2_tkip_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("087")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #验证WPA2 AES/TKIP long pwd Captive Portal凭据认证功能生效
    def test_088_wpa2_tkip_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2 AES/TKIP long pwd Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("088")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2 AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['long_wpa'])
        self.assertNotIn(False,result)

    #验证WPA/WPA2-802.1x AES Captive Portal凭据认证功能生效
    def test_089_wpa_8021x_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("089")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", title, \
                        Voucher_password)
        self.assertNotIn(False,result)

    #验证WPA/WPA2-802.1x AES/TKIP Captive Portal凭据认证功能生效
    def test_090_wpa_8021x_WeChatAuth_portal_access_portal(self):
        u"""验证WPA/WPA2-802.1x AES/TKIP Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("090")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA/WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                           data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", title, \
                        Voucher_password)
        self.assertNotIn(False,result)

    #验证WPA2-802.1x AES Captive Portal凭据认证功能生效
    def test_091_wpa2_8021x_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("091")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", title, \
                        Voucher_password)
        self.assertNotIn(False,result)

    #验证WPA2-802.1x AES/TKIP Captive Portal凭据认证功能生效
    def test_092_wpa2_8021x_WeChatAuth_portal_access_portal(self):
        u"""验证WPA2-802.1x AES/TKIP Captive Portal凭据认证功能生效(testlinkID:)"""
        log.debug("092")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #修改加密为WPA2-802.1x AES/TKIP
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "802.1x", title, \
                        Voucher_password)
        self.assertNotIn(False,result)

    #一个ap有五个ssid，每个ssid的通过不同的portal过认证-免费认证
    def test_093_1ap_5ssid_NoAuth(self):
        u"""一个ap有五个ssid，每个ssid的通过不同的portal过认证-免费认证(testlinkID:)"""
        log.debug("093")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #新增4个ssid，每个ssid都开启portal认证，并都加入到一个ap里面
        tmp2 = SSIDSBusiness(self.s)
        tmp2.add_ssid_no_ap(data_wireless['all_ssid']+"-2", data_wireless['short_wpa'])
        tmp2.add_ssid_no_ap(data_wireless['all_ssid']+"-3", data_wireless['short_wpa'])
        tmp2.add_ssid_no_ap(data_wireless['all_ssid']+"-4", data_wireless['short_wpa'])
        tmp2.add_ssid_no_ap(data_wireless['all_ssid']+"-5", data_wireless['short_wpa'])
        #每个ssid开启portal
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'], \
                       encry_dict, data_dict)
        time.sleep(60)
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-2", \
                       encry_dict, data_dict)
        time.sleep(60)
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-3", \
                       encry_dict, data_dict)
        time.sleep(60)
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-4", \
                       encry_dict, data_dict)
        time.sleep(60)
        tmp2.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-5", \
                       encry_dict, data_dict)
        time.sleep(120)
        #第一个ssid通过免费认证
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['short_wpa'])
        self.assertNotIn(False, result)

    #一个ap有五个ssid，每个ssid的通过不同的portal过认证-密码认证
    def test_094_1ap_5ssid_PWDAuth(self):
        u"""一个ap有五个ssid，每个ssid的通过不同的portal过认证-密码认证(testlinkID:)"""
        log.debug("094")
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid']+"-2", \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #一个ap有五个ssid，每个ssid的通过不同的portal过认证-帐号认证
    def test_095_1ap_5ssid_RadiusAuth(self):
        u"""一个ap有五个ssid，每个ssid的通过不同的portal过认证-帐号认证(testlinkID:)"""
        log.debug("095")
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid']+"-3", \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #一个ap有五个ssid，每个ssid的通过不同的portal过认证-微信认证
    def test_096_1ap_5ssid_WeChatAuth(self):
        u"""一个ap有五个ssid，每个ssid的通过不同的portal过认证-微信认证(testlinkID:)"""
        log.debug("096")
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid']+"-4", \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #一个ap有五个ssid，每个ssid的通过不同的portal过认证-凭据认证
    def test_097_1ap_5ssid_VouchersAuth(self):
        u"""一个ap有五个ssid，每个ssid的通过不同的portal过认证-凭据认证(testlinkID:)"""
        log.debug("097")
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid']+"-5", \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #每个ap对应一个ssid，每个ssid通过不同的portal通过认证-免费认证
    def test_098_1ap_to_1ssid_NoAuth(self):
        u"""每个ap对应一个ssid，每个ssid通过不同的portal通过认证-免费认证(testlinkID:)"""
        log.debug("098")
        #获取policy List1的id
        tmp1 = PolicyListBusiness(self.s)
        policylist_id = tmp1.get_policylist_id("List1")
        #删除ssid4,ssid5
        tmp2 = SSIDSBusiness(self.s)
        tmp2.delete_ssid(data_wireless['all_ssid']+"-4")
        time.sleep(60)
        tmp2.delete_ssid(data_wireless['all_ssid']+"-5")
        time.sleep(60)
        #ssid2分配到7600,ssid3分配到7600lr
        #每个ssid开启portal
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        data_dict2 = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(policylist_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2", \
                       encry_dict, data_dict1)
        time.sleep(60)
        tmp2.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid']+"-3", \
                       encry_dict, data_dict2)
        time.sleep(120)
        #第一个ssid通过免费认证
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['short_wpa'])
        self.assertNotIn(False, result)

    #每个ap对应一个ssid，每个ssid通过不同的portal通过认证-密码认证
    def test_099_1ap_to_1ssid_PWDAuth(self):
        u"""每个ap对应一个ssid，每个ssid通过不同的portal通过认证-密码认证(testlinkID:)"""
        log.debug("099")
        #第二个ssid通过密码认证
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid']+"-2", \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #每个ap对应一个ssid，每个ssid通过不同的portal通过认证-帐号认证
    def test_100_1ap_to_1ssid_RadiusAuth(self):
        u"""每个ap对应一个ssid，每个ssid通过不同的portal通过认证-帐号认证(testlinkID:)"""
        log.debug("100")
        #第三个ssid通过帐号认证
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid']+"-3", \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #每个ap对应一个ssid，每个ssid通过不同的portal通过认证-微信认证
    def test_101_1ap_to_1ssid_WeChatAuth(self):
        u"""每个ap对应一个ssid，每个ssid通过不同的portal通过认证-微信认证(testlinkID:)"""
        log.debug("101")
        #第一个ssid通过微信认证
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #每个ap对应一个ssid，每个ssid通过不同的portal通过认证-凭据认证
    def test_102_1ap_to_1ssid_VouchersAuth(self):
        u"""每个ap对应一个ssid，每个ssid通过不同的portal通过认证-凭据认证(testlinkID:)"""
        log.debug("102")
        #第二个ssid通过凭据认证
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid']+"-2", \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #切换list-免费认证
    def test_103_change_list_NoAuth(self):
        u"""切换list-免费认证(testlinkID:)"""
        log.debug("103")
        tmp1 = SSIDSBusiness(self.s)
        #删除多余ssid
        tmp1.delete_ssid(data_wireless['all_ssid']+"-2")
        time.sleep(60)
        tmp1.delete_ssid(data_wireless['all_ssid']+"-3")
        time.sleep(60)
        #新建了policy list
        tmp2 = PolicyListBusiness(self.s)
        list_id2 = tmp2.add_policylist("List2", 120, data_basic['splashpage_name'])
        #ssid1改为list2
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(list_id2),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_NoAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa",title, data_wireless['short_wpa'])
        self.assertNotIn(False, result)

     #切换list-密码认证
    def test_104_change_list_PWDAuth(self):
        u"""切换list-密码认证(testlinkID:)"""
        log.debug("104")
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_PWDAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic["portal_pwd"],\
                        title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #切换list-帐号认证
    def test_105_change_list_RadiusAuth(self):
        u"""切换list-帐号认证(testlinkID:)"""
        log.debug("105")
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_RadiusAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_basic['radius_usename'],\
                        data_basic['radius_password'], title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #切换list-微信认证
    def test_106_change_list_WeChatAuth(self):
        u"""切换list-微信认证(testlinkID:)"""
        log.debug("106")
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_WeChatAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #切换list-凭据认证
    def test_107_change_list_VouchersAuth(self):
        u"""切换list-凭据认证(testlinkID:)"""
        log.debug("107")
        #随机获取这个凭据组的一个密码
        tmp4 = VouchersBusiness(self.s)
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过凭据认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        title = u"腾讯首页"
        result = tmp3.check_VouchersAuth_portal(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", title, \
                        Voucher_password, data_wireless['short_wpa'])
        self.assertNotIn(False,result)

    #概要-新增访客会话-当客户端连接上ssid并且已通过认证时-免费认证
    def test_108_summary_GuestNewSession_NoAuth(self):
        u"""概要-新增访客会话-当客户端连接上ssid并且已通过认证时-免费认证(testlinkID:)"""
        log.debug("108")
        #修改policylist的List1的过期时间为8分钟
        tmp2 = PolicyListBusiness(self.s)
        list1_id = tmp2.edit_policylist("List1", 480, data_basic['splashpage_name'])
        #ssid1改为list1
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_portal_enable': "1",
                     'ssid_portal_policy': "{}".format(list1_id),
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1 = SSIDSBusiness(self.s)
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #使用无线客户端访问web页面,并通过免费认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        #portal测试的准备工作
        tmp3.portal_test_ready(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        #使用免费认证通过认证
        tmp3.set_NoAuth_access_portal(url)
        #等待5分钟，让ap数据上传到cloud上
        time.sleep(300)
        #无线网卡释放ip地址
        tmp3.dhcp_release_wlan(data_basic["wlan_pc"])
        #启用有线网卡
        tmp3.wlan_enable(data_basic["lan_pc"])
        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp4 = SummaryBusiness(self.s)
        tmp4.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取强制网络门户-概要-新增访客会话，返回最后一条客户端在线数量
        clientcount_1d = tmp4.get_portal_summary_GuestNewSession("1d")
        clientcount_2h = tmp4.get_portal_summary_GuestNewSession("2h")
        self.assertEqual(clientcount_1d, 1)
        self.assertEqual(clientcount_2h, 1)

    #访客菜单检查-免费认证
    def test_109_check_guest_NoAuth(self):
        u"""访客菜单检查-免费认证(testlinkID:)"""
        log.debug("109")
        tmp = GuestBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        result = tmp.check_client_info(client_mac, data_ap['7610_mac'], \
                                       data_wireless['all_ssid'], 0, "9")
        #portal测试的清理工作
        tmp3 = CPBusiness(self.s)
        tmp3.portal_test_finish(data_basic["wlan_pc"], data_basic["lan_pc"])
        self.assertTrue(result)

    #概要-访客认证会话-免费认证
    def test_110_summary_GuestSessionByAuthentication_NoAuth(self):
        u"""概要-访客认证会话-免费认证(testlinkID:)"""
        log.debug("110")
        tmp = SummaryBusiness(self.s)
        #获取访客认证会话中所有通过认证的方式
        result_1d = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        result_2h = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        self.assertIn("no_authentication", result_1d)
        self.assertIn("no_authentication", result_2h)

    #概要-访客SSID会话
    def test_111_summary_GuestSessionBySSID(self):
        u"""概要-访客SSID会话(testlinkID:)"""
        log.debug("111")
        #获取访客SSID会话
        tmp = SummaryBusiness(self.s)
        result = tmp.get_portal_summary_GuestSessionBySSID()
        self.assertIn(data_wireless['all_ssid'], result)

    #概要-新增访客会话-当客户端连接上ssid并且已通过认证时-密码认证
    def test_112_summary_GuestNewSession_PWDAuth(self):
        u"""概要-新增访客会话-当客户端连接上ssid并且已通过认证时-密码认证(testlinkID:)"""
        log.debug("112")
        #等待3分钟,让客户端被portal踢下线
        time.sleep(180)
        #使用无线客户端访问web页面,并通过密码认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        #portal测试的准备工作
        tmp3.portal_test_ready(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        #使用密码认证通过认证
        tmp3.set_PWDAuth_access_portal(url, data_basic["portal_pwd"])
        #等待5分钟，让ap数据上传到cloud上
        time.sleep(300)
        #无线网卡释放ip地址
        tmp3.dhcp_release_wlan(data_basic["wlan_pc"])
        #启用有线网卡
        tmp3.wlan_enable(data_basic["lan_pc"])
        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp4 = SummaryBusiness(self.s)
        tmp4.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取强制网络门户-概要-新增访客会话，返回最后一条客户端在线数量
        clientcount_1d = tmp4.get_portal_summary_GuestNewSession("1d")
        clientcount_2h = tmp4.get_portal_summary_GuestNewSession("2h")
        self.assertEqual(clientcount_1d, 1)
        self.assertEqual(clientcount_2h, 1)

    #访客菜单检查-密码认证
    def test_113_check_guest_PWDAuth(self):
        u"""访客菜单检查-密码认证(testlinkID:)"""
        log.debug("113")
        tmp = GuestBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        result = tmp.check_client_info(client_mac, data_ap['7610_mac'], \
                                       data_wireless['all_ssid'], 13, "9")
        #portal测试的清理工作
        tmp3 = CPBusiness(self.s)
        tmp3.portal_test_finish(data_basic["wlan_pc"], data_basic["lan_pc"])
        self.assertTrue(result)

    #概要-访客认证会话-密码认证
    def test_114_summary_GuestSessionByAuthentication_PWDAuth(self):
        u"""概要-访客认证会话-密码认证(testlinkID:)"""
        log.debug("114")
        tmp = SummaryBusiness(self.s)
        #获取访客认证会话中所有通过认证的方式
        result_1d = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        result_2h = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        self.assertIn("password_authentication", result_1d)
        self.assertIn("password_authentication", result_2h)

    #概要-新增访客会话-当客户端连接上ssid并且已通过认证时-帐号认证
    def test_115_summary_GuestNewSession_RadiusAuth(self):
        u"""概要-新增访客会话-当客户端连接上ssid并且已通过认证时-帐号认证(testlinkID:)"""
        log.debug("115")
        #等待3分钟,让客户端被portal踢下线
        time.sleep(180)
        #使用无线客户端访问web页面,并通过帐号认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        #portal测试的准备工作
        tmp3.portal_test_ready(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        #使用帐号认证通过认证
        tmp3.set_RadiusAuth_access_portal(url, data_basic['radius_usename'],\
                        data_basic['radius_password'])
        #等待5分钟，让ap数据上传到cloud上
        time.sleep(300)
        #无线网卡释放ip地址
        tmp3.dhcp_release_wlan(data_basic["wlan_pc"])
        #启用有线网卡
        tmp3.wlan_enable(data_basic["lan_pc"])
        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp4 = SummaryBusiness(self.s)
        tmp4.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取强制网络门户-概要-新增访客会话，返回最后一条客户端在线数量
        clientcount_1d = tmp4.get_portal_summary_GuestNewSession("1d")
        clientcount_2h = tmp4.get_portal_summary_GuestNewSession("2h")
        self.assertEqual(clientcount_1d, 1)
        self.assertEqual(clientcount_2h, 1)

    #访客菜单检查-帐号认证
    def test_116_check_guest_RadiusAuth(self):
        u"""访客菜单检查-帐号认证(testlinkID:)"""
        log.debug("116")
        tmp = GuestBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        result = tmp.check_client_info(client_mac, data_ap['7610_mac'], \
                                       data_wireless['all_ssid'], 1, "9")
        #portal测试的清理工作
        tmp3 = CPBusiness(self.s)
        tmp3.portal_test_finish(data_basic["wlan_pc"], data_basic["lan_pc"])
        self.assertTrue(result)

    #概要-访客认证会话-帐号认证
    def test_117_summary_GuestSessionByAuthentication_RadiusAuth(self):
        u"""概要-访客认证会话-帐号认证(testlinkID:)"""
        log.debug("117")
        tmp = SummaryBusiness(self.s)
        #获取访客认证会话中所有通过认证的方式
        result_1d = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        result_2h = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        self.assertIn("radius_authentication", result_1d)
        self.assertIn("radius_authentication", result_2h)

    #概要-新增访客会话-当客户端连接上ssid并且已通过认证时-微信认证
    def test_118_summary_GuestNewSession_WeChatAuth(self):
        u"""概要-新增访客会话-当客户端连接上ssid并且已通过认证时-微信认证(testlinkID:)"""
        log.debug("118")
        #等待3分钟,让客户端被portal踢下线
        time.sleep(180)
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        #portal测试的准备工作
        tmp3.portal_test_ready(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        #使用微信认证通过认证
        tmp3.set_WeChatAuth_access_portal(url)
        #等待5分钟，让ap数据上传到cloud上
        time.sleep(300)
        #无线网卡释放ip地址
        tmp3.dhcp_release_wlan(data_basic["wlan_pc"])
        #启用有线网卡
        tmp3.wlan_enable(data_basic["lan_pc"])
        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp4 = SummaryBusiness(self.s)
        tmp4.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取强制网络门户-概要-新增访客会话，返回最后一条客户端在线数量
        clientcount_1d = tmp4.get_portal_summary_GuestNewSession("1d")
        clientcount_2h = tmp4.get_portal_summary_GuestNewSession("2h")
        self.assertEqual(clientcount_1d, 1)
        self.assertEqual(clientcount_2h, 1)

    #访客菜单检查-微信认证
    def test_119_check_guest_WeChatAuth(self):
        u"""访客菜单检查-微信认证(testlinkID:)"""
        log.debug("119")
        tmp = GuestBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        result = tmp.check_client_info(client_mac, data_ap['7610_mac'], \
                                       data_wireless['all_ssid'], 2, "9")
        #portal测试的清理工作
        tmp3 = CPBusiness(self.s)
        tmp3.portal_test_finish(data_basic["wlan_pc"], data_basic["lan_pc"])
        self.assertTrue(result)

    #概要-访客认证会话-微信认证
    def test_120_summary_GuestSessionByAuthentication_WeChatAuth(self):
        u"""概要-访客认证会话-微信认证(testlinkID:)"""
        log.debug("120")
        tmp = SummaryBusiness(self.s)
        #获取访客认证会话中所有通过认证的方式
        result_1d = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        result_2h = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        self.assertIn("wechat", result_1d)
        self.assertIn("wechat", result_2h)

    #概要-新增访客会话-当客户端连接上ssid并且已通过认证时-凭据认证
    def test_121_summary_GuestNewSession_VouchersAuth(self):
        u"""概要-新增访客会话-当客户端连接上ssid并且已通过认证时-凭据认证(testlinkID:)"""
        log.debug("121")
        #等待3分钟,让客户端被portal踢下线
        time.sleep(180)
        tmp4 = VouchersBusiness(self.s)
        #删除凭据Voucher_List1
        tmp4.delete_vouchers_list("Voucher_List1")
        #然后再新建一个凭据Voucher_List1,过期时间为8分钟
        tmp4.add_vouchers_list("Voucher_List1",{'effectDurationMap':{'d': 0, 'h': 0, 'm': "8"}})
        #随机获取这个凭据组的一个密码
        Voucher_password = tmp4.get_vouchers_not_used_password("Voucher_List1")
        #使用无线客户端访问web页面,并通过微信认证
        tmp3 = CPBusiness(self.s)
        url = "http://www.qq.com"
        #portal测试的准备工作
        tmp3.portal_test_ready(url, data_basic["lan_pc"], \
                        data_wireless['all_ssid'], \
                        data_basic["wlan_pc"], "wpa", data_wireless['short_wpa'])
        #使用凭据认证通过认证
        tmp3.set_VouchersAuth_access_portal(url, Voucher_password)
        #等待5分钟，让ap数据上传到cloud上
        time.sleep(300)
        #无线网卡释放ip地址
        tmp3.dhcp_release_wlan(data_basic["wlan_pc"])
        #启用有线网卡
        tmp3.wlan_enable(data_basic["lan_pc"])
        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp4 = SummaryBusiness(self.s)
        tmp4.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取强制网络门户-概要-新增访客会话，返回最后一条客户端在线数量
        clientcount_1d = tmp4.get_portal_summary_GuestNewSession("1d")
        clientcount_2h = tmp4.get_portal_summary_GuestNewSession("2h")
        self.assertEqual(clientcount_1d, 1)
        self.assertEqual(clientcount_2h, 1)

    #访客菜单检查-凭据认证
    def test_122_check_guest_VouchersAuth(self):
        u"""访客菜单检查-凭据认证(testlinkID:)"""
        log.debug("122")
        tmp = GuestBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        result = tmp.check_client_info(client_mac, data_ap['7610_mac'], \
                                       data_wireless['all_ssid'], 12, "9")
        #portal测试的清理工作
        tmp3 = CPBusiness(self.s)
        tmp3.portal_test_finish(data_basic["wlan_pc"], data_basic["lan_pc"])
        self.assertTrue(result)

    #概要-访客认证会话-凭据认证
    def test_123_summary_GuestSessionByAuthentication_VouchersAuth(self):
        u"""概要-访客认证会话-凭据认证(testlinkID:)"""
        log.debug("123")
        tmp = SummaryBusiness(self.s)
        #获取访客认证会话中所有通过认证的方式
        result_1d = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        result_2h = tmp.get_portal_summary_GuestSessionByAuthentication("1d")
        self.assertIn("voucher", result_1d)
        self.assertIn("voucher", result_2h)

    #删除ap，并恢复cloud的初始环境
    def test_124_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("124")
        #测试完后恢复初始环境
        tmp1 = SSIDSBusiness(self.s)
        tmp1.dhcp_release_wlan(data_basic['wlan_pc'])
        tmp1.disconnect_ap()
        #修改ssid1为初始状态
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan': "0",
                     'ssid_isolation': "0",
                     'ssid_rssi_enable': "0",
                    'ssid_ssid': "GWN-Cloud",
                    'ssid_ssid_band': "",
                     'ssid_portal_enable': "0"}
        tmp1.edit_ssid("", data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #删除policy list
        tmp2 = PolicyListBusiness(self.s)
        tmp2.delete_policylist("List1")
        tmp2.delete_policylist("List2")
        #删除凭据组
        tmp3 = VouchersBusiness(self.s)
        tmp3.delete_vouchers_list("Voucher_List1")
        #删除三个ap
        tmp = APSBusiness(self.s)
        tmp.delete_ap(data_ap['7610_mac'])
        tmp.delete_ap(data_ap['7600_mac'])
        tmp.delete_ap(data_ap['7600lr_mac'])
        time.sleep(360)




    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
