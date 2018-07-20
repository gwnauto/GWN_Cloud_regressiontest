#coding=utf-8
#作者：曾祥卫
#时间：2018.06.14
#描述：cloud监控面板-概览用例集，调用overview_business

import unittest, time
from dashboard.overview.overview_business import OverViewBusiness
from system.settings.settings_business import SettingsBusiness
from dashboard.network_list.networklist_business import NetworkListBusiness
from navbar.user.user_business import UserBusiness
from dashboard.ap_list.allaplist_business import AllApListBusiness
from access_points.aps_business import APSBusiness
from ssids.ssids_business import SSIDSBusiness
from data import data
from data.logfile import Log
import requests
log = Log("overview")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()




class TestOverview(unittest.TestCase):
    u"""测试监控面板-概览的用例集(runtime:0.44h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = NetworkListBusiness(self.s)
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
        print("add 3 model aps to cloud pass!")

    #修改ssid，使用无线client连接，并打流
    def test_002_client_connect_iperf_ap(self):
        u"""修改ssid，使用无线client连接，并打流"""
        log.debug("002")
        #修改ssid
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'membership_macs': "%s,%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper(),
                                             data_ap['7610_mac'].upper()),
                    'ssid_ssid': data_wireless['all_ssid']}
        tmp.edit_ssid(data_ap['7610_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(60)
        #AP 上传流量统计的准确性
        tmp = APSBusiness(self.s)
        tmp.run_AP_download(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        #等待5分钟
        result = tmp.connect_DHCP_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        tmp.dhcp_release_wlan_backup(data_basic['wlan_pc'])
        self.assertIn(data_wireless['all_ssid'], result)

    #验证监控面板-概览-AP总数
    def test_003_check_overview_ap_count(self):
        u"""获取监控面板-概览-AP总数"""
        log.debug("003")
        tmp = OverViewBusiness(self.s)
        result = tmp.get_overview_ap_count()
        self.assertEqual(result, 3)

    #验证监控面板-概览-在线和离线AP数
    def test_004_check_overview_ap_online_offline_count(self):
        u"""验证监控面板-概览-在线和离线AP数"""
        log.debug("004")
        tmp = OverViewBusiness(self.s)
        online_ap_count, offline_ap_count = tmp.get_overview_ap_online_offline_count()
        self.assertEqual(online_ap_count, 3)
        self.assertEqual(offline_ap_count, 0)

    #验证监控面板-概览-客户端总数
    def test_005_check_overview_client_count(self):
        u"""验证监控面板-概览-客户端总数"""
        log.debug("005")
        tmp = OverViewBusiness(self.s)
        result = tmp.get_overview_client_count()
        self.assertEqual(result, 1)

    #验证客户端2.4G+5G=总数
    def test_006_check_overview_client_count_equal_2g4_and_5g(self):
        u"""验证客户端2.4G+5G=总数"""
        log.debug("006")
        tmp = OverViewBusiness(self.s)
        result = tmp.get_overview_client_count()
        g24_client_count, g5_client_count = tmp.get_overview_client_online_offline_count()
        self.assertEqual(result, (g24_client_count+g5_client_count))

    #验证最近1天监控面板-概览-客户端数量，返回最后一条客户端在线数量
    def test_007_check_1d_overview_last_clientcount(self):
        u"""验证最近1天监控面板-概览-客户端数量，返回最后一条客户端在线数量"""
        log.debug("007")
        tmp = OverViewBusiness(self.s)
        clientcount = tmp.get_overview_last_clientcount("1d")
        self.assertEqual(clientcount, 1)

    # #验证最近1天监控面板-概览-速率，上传下载的bandwidth是否正确
    # def test_008_check_1d_overview_bandwidth(self):
    #     u"""验证最近1天监控面板-概览-速率，上传下载的bandwidth是否正确"""
    #     log.debug("008")
    #     tmp = OverViewBusiness(self.s)
    #     result = tmp.check_overview_bandwidth("1d")
    #     self.assertTrue(result)

    #验证最近1天监控面板-概览-Top Aps，第一个ap的信息
    def test_008_check_1d_overview_last_clientcount(self):
        u"""验证最近1天监控面板-概览-Top Aps，第一个ap的信息"""
        log.debug("008")
        tmp = OverViewBusiness(self.s)
        apType = tmp.get_overview_top_aps("1d")['apType']
        self.assertIn("GWN76", apType)

    #验证最近1天监控面板-概览-Top Clients，第一个client的mac地址
    def test_009_check_1d_overview_top_clients(self):
        u"""验证最近1天监控面板-概览-Top Clients，第一个client的mac地址"""
        log.debug("009")
        tmp = OverViewBusiness(self.s)
        wlan_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        result = tmp.check_overview_top_client("1d", wlan_mac)
        self.assertTrue(result)

    #验证最近1天监控面板-概览-Top SSIDs，第一个SSID的name
    def test_010_check_1d_overview_top_ssids(self):
        u"""验证最近1天监控面板-概览-Top SSIDs，第一个SSID的name"""
        log.debug("010")
        tmp = OverViewBusiness(self.s)
        name = tmp.get_overview_top_ssids("1d")
        self.assertEqual(name, data_wireless['all_ssid'])

    #验证最近2小时监控面板-概览-客户端数量，返回最后一条客户端在线数量
    def test_011_check_2h_overview_last_clientcount(self):
        u"""验证最近2小时监控面板-概览-客户端数量，返回最后一条客户端在线数量"""
        log.debug("011")
        tmp = OverViewBusiness(self.s)
        clientcount = tmp.get_overview_last_clientcount("2h")
        self.assertEqual(clientcount, 1)

    # #验证最近2小时监控面板-概览-速率，上传下载的bandwidth是否正确
    # def test_013_check_2h_overview_bandwidth(self):
    #     u"""验证最近2小时监控面板-概览-速率，上传下载的bandwidth是否正确"""
    #     log.debug("013")
    #     tmp = OverViewBusiness(self.s)
    #     result = tmp.check_overview_bandwidth("2h")
    #     self.assertTrue(result)

    #验证最近2小时监控面板-概览-Top Aps，第一个ap的信息
    def test_012_check_2h_overview_last_clientcount(self):
        u"""验证最近2小时监控面板-概览-Top Aps，第一个ap的信息"""
        log.debug("012")
        tmp = OverViewBusiness(self.s)
        apType = tmp.get_overview_top_aps("2h")['apType']
        self.assertIn("GWN76", apType)

    #验证最近2小时监控面板-概览-Top Clients，第一个client的mac地址
    def test_013_check_2h_overview_top_clients(self):
        u"""验证最近2小时监控面板-概览-Top Clients，第一个client的mac地址"""
        log.debug("013")
        tmp = OverViewBusiness(self.s)
        wlan_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        result = tmp.check_overview_top_client("2h", wlan_mac)
        self.assertTrue(result)

    #验证最近2小时监控面板-概览-Top SSIDs，第一个SSID的name
    def test_014_check_2h_overview_top_ssids(self):
        u"""验证最近2小时监控面板-概览-Top SSIDs，第一个SSID的name"""
        log.debug("014")
        tmp = OverViewBusiness(self.s)
        name = tmp.get_overview_top_ssids("2h")
        self.assertEqual(name, data_wireless['all_ssid'])


    #删除ap，并恢复cloud的初始环境
    def test_015_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("015")
        #测试完后恢复初始环境
        #1.修改ap的ssid为GWN-Cloud
        tmp1 = SSIDSBusiness(self.s)
        tmp1.dhcp_release_wlan(data_basic['wlan_pc'])
        tmp1.disconnect_ap()
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': "GWN-Cloud",
                     'ssid_ssid_band': ""}
        tmp1.edit_ssid("", data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
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
