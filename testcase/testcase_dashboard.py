#coding=utf-8
#作者：蒋甜
#时间：2018.07.11
#描述：cloud监控面板-概览用例集

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
log = Log("dashboard")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()

class TestDashboard(unittest.TestCase):
    u"""测试监控面板(runtime:1.5h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = NetworkListBusiness(self.s)
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])

     #在cloud中添加两个netwrok,并且判断是否成功
    def test_001_add_2_network_cloud(self):
        u"""cloud中添加两个netwrok,并且判断是否成功"""
        log.debug("001")
        tmp = APSBusiness(self.s)
        #描述：启用无线网卡
        tmp.wlan_enable(data_basic['wlan_pc'])
        tmp.dhcp_release_wlan(data_basic['wlan_pc'])
        #获取登录名对应的id
        tmp1 =UserBusiness(self.s)
        user_id = tmp1.get_network_id(data_basic['cloud_user'])
        tmp2 = NetworkListBusiness(self.s)
        #添加2个网络组
        result = tmp2.add_network("group1", user_id, "")
        result1 = tmp2.add_network("group2",user_id,"")
        #获取网络组对应的id--监控面板--网络列表
        network_id = tmp2.get_network_id("group1")
        network_id1 = tmp2.get_network_id("group2")
        self.assertEqual(network_id, int(result['data']['value']))
        self.assertEqual(network_id1,int(result1['data']['value']))

    #三个netwrok分别添加不同的ap，并判断是否添加成功
    def test_002_add_3_model_aps_2_cloud(self):
        u"""三个netwrok分别添加不同的ap，并判断是否添加成功"""
        log.debug("002")
        tmp = APSBusiness(self.s)
        tmp1 = NetworkListBusiness(self.s)
        tmp2 = SettingsBusiness(self.s)
        #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
        tmp.add_ap_2_local_cloud(data_basic['7610_ip'], data_ap['7610_mac'], "autotest_7610")
        #cloud上获取该网络组的ssh密码
        ssh_pwd = tmp2.get_ssh_pwd()
        #选择进入group1网络组
        tmp1.goin_network("group1")
        tmp.add_ap_2_local_cloud(data_basic['7600_ip'], data_ap['7600_mac'], "autotest_7600")
        #cloud上获取该网络组的ssh密码
        ssh_pwd1 = tmp2.get_ssh_pwd()
        #选择进入group2网络组
        tmp1.goin_network("group2")
        tmp.add_ap_2_local_cloud(data_basic['7600lr_ip'], data_ap['7600lr_mac'], "autotest_7600lr")
        #cloud上获取该网络组的ssh密码
        ssh_pwd2 = tmp2.get_ssh_pwd()
        #判断ap是否已经和cloud配对上
        result1 = tmp.check_ap_pair_cloud(data_basic['7610_ip'],
                    data_basic['sshUser'], ssh_pwd)
        result2 = tmp.check_ap_pair_cloud(data_basic['7600_ip'],
                    data_basic['sshUser'], ssh_pwd1)
        result3 = tmp.check_ap_pair_cloud(data_basic['7600lr_ip'],
                    data_basic['sshUser'], ssh_pwd2)
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        print("add 3 model aps to cloud pass!")

    #验证监控面板-多个network概览-AP总数
    def test_003_check_overview_ap_count(self):
        u"""获取监控面板-概览-AP总数"""
        log.debug("003")
        tmp = OverViewBusiness(self.s)
        result = tmp.get_overview_ap_count()
        self.assertEqual(result, 3)

    #获取监控面板-多个network概览-AP在线和离线数量
    def test_004_check_overview_ap_online_offline(self):
        u"""获取监控面板-概览-AP在线和离线"""
        log.debug("004")
        tmp = OverViewBusiness(self.s)
        result,result1 = tmp.get_overview_ap_online_offline_count()
        self.assertEqual(result, 3)
        self.assertEqual(result1,0)

    #获取某个network的AP总数
    def test_005_check_network_overview(self):
        u"""获取某个network的AP总数"""
        log.debug("005")
        tmp = OverViewBusiness(self.s)
        #选择进入group1网络组
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group1")
        result = tmp.get_network_overview_ap_count()
        self.assertEqual(result, 1)

    #获取某个network概览-AP在线和离线数量
    def test_006_check_network_ap_online_offline_count(self):
        u"""获取某个network概览-AP在线和离线数量"""
        log.debug("006")
        tmp = OverViewBusiness(self.s)
        #选择进入group1网络组
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group2")
        result,result1= tmp.get_network_overview_ap_online_offline_count()
        self.assertEqual(result, 1)
        self.assertEqual(result1,0)

    #修改ssid，使用无线client连接，并打流,2.4G
    def test_007_default_client_connect_iperf_ap(self):
        u"""修改group1下面ssid，使用无线client连接，并打流"""
        log.debug("007")
        #修改ssid
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'membership_macs': "%s"%(data_ap['7610_mac'].upper()),
                    'ssid_ssid': data_wireless['all_ssid'],
                    'ssid_ssid_band': "2"}
        tmp.edit_ssid(data_ap['7610_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(60)
        #AP 上传流量统计的准确性
        tmp = APSBusiness(self.s)
        tmp.run_AP_download_back(data_wireless['all_ssid'],
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

        #检查监控-概览--client数量 2.4G客户端
    def test_008_overview_client_count(self):
        u"""检查监控-概览--client数量"""
        log.debug("008")
        tmp = OverViewBusiness(self.s)
        result = tmp.get_overview_client_count_detail()
        result1 = result[0]['value']
        self.assertEqual(result1, 1)

    #修改ssid，使用无线client连接，并打流5G
    def test_009_default_client_connect_iperf_ap(self):
        u"""修改default下面ssid0频段为5G，使用无线client连接"""
        log.debug("009")
        #修改ssid
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'membership_macs': "%s"%(data_ap['7610_mac'].upper()),
                    'ssid_ssid': data_wireless['all_ssid'],
                    'ssid_ssid_band': "5",
                     }
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
                #AP 上传流量统计的准确性
        tmp2 = APSBusiness(self.s)
        tmp2.run_AP_download_back(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        time.sleep(360)
        #等待5分钟
        result = tmp.connect_DHCP_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        tmp.dhcp_release_wlan_backup(data_basic['wlan_pc'])
        self.assertIn(data_wireless['all_ssid'], result)

    #检查监控-概览--client数量
    def test_010_overview_client_count(self):
        u"""检查监控-概览--client数量"""
        log.debug("010")
        tmp = OverViewBusiness(self.s)
        result = tmp.get_overview_client_count_detail()
        result1 = result[1]['value']
        self.assertEqual(result1, 1)

    #检查network-概览-client数量
    def test_011_get_network_overview_total_client_count(self):
        u"""检查network-概览--client数量"""
        log.debug("011")
        tmp = OverViewBusiness(self.s)
        result = tmp.get_overview_client_count()
        self.assertEqual(result, 1)

     #修改group1下面ssid，使用无线client连接，并打流
    def test_012_check_change_network_client_count(self):
        u"""修改group1下面ssid，使用无线client连接，并打流"""
        log.debug("012")
        #选择进入group1网络组
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group1")
        #修改ssid
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'membership_macs': "%s"%(data_ap['7600_mac'].upper()),
                    'ssid_ssid': data_wireless['grou1_all_ssid']}
        tmp.edit_ssid(data_ap['7600_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(60)
        #AP 上传流量统计的准确性
        tmp2 = APSBusiness(self.s)
        tmp2.run_AP_download_back(data_wireless['grou1_all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        #等待5分钟
        result = tmp.connect_DHCP_WPA_AP(data_wireless['grou1_all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        tmp.dhcp_release_wlan_backup(data_basic['wlan_pc'])
        self.assertIn(data_wireless['grou1_all_ssid'], result)

    #修改group2的ssid名称，避免客户端数量被干扰
    def test_013_edit_ssid_name(self):
        u"""修改group2的ssid名称，避免客户端数量被干扰"""
        log.debug('013')
        #选择进入group1网络组
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group2")
        #修改ssid
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'membership_macs': "%s"%(data_ap['7600lr_mac'].upper()),
                    'ssid_ssid': data_wireless['grou1_all_ssid']+"3"}
        tmp.edit_ssid(data_ap['7600lr_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(60)
        #AP 上传流量统计的准确性
        tmp2 = APSBusiness(self.s)
        tmp2.run_AP_download_back(data_wireless['grou1_all_ssid']+"3",
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        time.sleep(360)
        #等待5分钟
        result = tmp.connect_DHCP_WPA_AP(data_wireless['grou1_all_ssid']+"3",
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        tmp.dhcp_release_wlan_backup(data_basic['wlan_pc'])
        self.assertIn(data_wireless['grou1_all_ssid']+"3", result)

    #切换network检查network-概览-client数量
    def test_014_get_network_overview_client_count(self):
        u"""检查network-概览--client数量"""
        log.debug("014")
        tmp = OverViewBusiness(self.s)
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group1")
        result = tmp.get_overview_client_count()
        self.assertEqual(result, 1)

    #将client切换ssid,验证network-概览-client数量
    def test_015_check_change_ssid_client_count(self):
        u"""将client切换ssid,验证network-概览-client数量"""
        log.debug("015")
        #选择进入group1网络组
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group1")
        tmp2 = OverViewBusiness(self.s)
        #AP 上传流量统计的准确性
        tmp3 = APSBusiness(self.s)
        #新增一个network
        tmp = SSIDSBusiness(self.s)
        tmp.add_ssid(data_ap['7600_mac'],data_wireless['grou1_all_ssid']+"-2",data_wireless['short_wpa'])
        time.sleep(60)
        tmp3.run_AP_download_back(data_wireless['grou1_all_ssid']+"-2",
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        time.sleep(360)
        #AP 上传流量统计的准确性
        result = tmp.connect_DHCP_WPA_AP(data_wireless['grou1_all_ssid']+"-2",
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        tmp.dhcp_release_wlan_backup(data_basic['wlan_pc'])
        result1 = tmp2.get_overview_client_count()
        self.assertIn(data_wireless['grou1_all_ssid']+"-2",result)
        self.assertEqual(result1, 1)


    #验证最近1天监控面板-概览-客户端数量，返回最后一条客户端在线数量
    def test_016_check_1d_overview_last_clientcount(self):
        u"""验证最近1天监控面板-概览-客户端数量，返回最后一条客户端在线数量"""
        log.debug("016")
        tmp = OverViewBusiness(self.s)
        clientcount = tmp.get_overview_last_clientcount("1d")
        self.assertEqual(clientcount, 1)

    #验证default network中最近1天监控面板-概览-客户端数量，返回最后一条客户端在线数量
    def test_017_check_network_1d_overview_last_clientcount(self):
        u"""验证default network最近1天监控面板-概览-客户端数量，返回最后一条客户端在线数量"""
        log.debug("017")
        tmp = OverViewBusiness(self.s)
        #选择进入group1网络组
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group1")
        clientcount = tmp.get_overview_last_clientcount("1d",menu=9)
        self.assertEqual(clientcount, 1)

    #验证最近2小时监控面板-概览-客户端数量，返回最后一条客户端在线数量
    def test_018_check_2h_overview_last_clientcount(self):
        u"""验证最近2小时监控面板-概览-客户端数量，返回最后一条客户端在线数量"""
        log.debug("018")
        tmp = OverViewBusiness(self.s)
        clientcount = tmp.get_overview_last_clientcount("2h")
        self.assertEqual(clientcount, 1)

    #验证default network最近2小时监控面板-概览-客户端数量，返回最后一条客户端在线数量
    def test_019_check_network_2h_overview_last_clientcount(self):
        u"""验证default network最近2小时监控面板-概览-客户端数量，返回最后一条客户端在线数量"""
        log.debug("019")
        tmp = OverViewBusiness(self.s)
        #选择进入group1网络组
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group1")
        #菜单参数
        clientcount = tmp.get_overview_last_clientcount("2h",menu=9)
        self.assertEqual(clientcount, 1)

     #验证最近一天监控面板-概览-top ap的数量
    def test_020_check_1d_overview_top_ap_count(self):
        u"""验证最近一天监控面板-概览-top ap"""
        log.debug("020")
        tmp = OverViewBusiness(self.s)
        ap_count = tmp.get_overview_top_aps_count("1d")
        self.assertEqual(ap_count, 3)

     #验证最近一天监控面板-概览-top ap的数量
    def test_021_check_network_1d_overview_top_ap_count(self):
        u"""验证最近一天监控面板-概览-top ap"""
        log.debug("021")
        tmp = OverViewBusiness(self.s)
        ap_count = tmp.get_overview_top_aps_count("1d",menu=9)
        self.assertEqual(ap_count, 1)

     #验证最近一天监控面板-概览-top ap的数量
    def test_022_check_network_2h_overview_top_ap_count(self):
        u"""验证最近一天监控面板-概览-top ap"""
        log.debug("022")
        tmp = OverViewBusiness(self.s)
        ap_count = tmp.get_overview_top_aps_count("2h",menu=9)
        self.assertEqual(ap_count, 1)

       #验证最近一天监控面板-概览-top ap的mac
    def test_023_check_1d_overview_top_ap_mac(self):
        u"""验证最近一天监控面板-概览-top ap的mac"""
        log.debug("023")
        tmp = OverViewBusiness(self.s)
        ap_mac = tmp.get_overview_top_aps_mac("1d")
        mac1 = data_ap['7600_mac'].upper()
        mac2 = data_ap['7610_mac'].upper()
        self.assertIn(mac1,ap_mac)
        self.assertIn(mac2,ap_mac)

    #验证最近两小时监控面板-概览-top ap的mac
    def test_024_check_2h_overview_top_ap_mac(self):
        u"""验证最近两小时监控面板-概览-top ap的mac"""
        log.debug("024")
        tmp = OverViewBusiness(self.s)
        ap_mac = tmp.get_overview_top_aps_mac("2h")
        mac1 = data_ap['7600_mac'].upper()
        mac2 = data_ap['7610_mac'].upper()
        self.assertIn(mac1,ap_mac)
        self.assertIn(mac2,ap_mac)

       #验证group1中最近一天监控面板-概览-top ap的mac
    def test_025_check_network_1d_overview_top_ap_mac(self):
        u"""验证最近一天监控面板-概览-top ap的mac"""
        log.debug("025")
        tmp = OverViewBusiness(self.s)
        #选择进入group1网络组
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group1")
        ap_mac = tmp.get_overview_top_aps_mac("1d",menu=9)
        mac1 = data_ap['7600_mac'].upper()
        self.assertIn(mac1,ap_mac)

    #验证group1最近两小时监控面板-概览-top ap的mac
    def test_026_check_network_2h_overview_top_ap_mac(self):
        u"""验证最近两小时监控面板-概览-top ap的mac"""
        log.debug("026")
        tmp = OverViewBusiness(self.s)
        #选择进入group1网络组
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network("group1")
        ap_mac = tmp.get_overview_top_aps_mac("2h",menu=9)
        mac1 = data_ap['7600_mac'].upper()
        self.assertIn(mac1,ap_mac)

    #验证最近一天监控面板-概览-top ap的usage排序正确
    def test_027_check_1d_overview_top_ap_usage(self):
        u"""验证最近一天监控面板-概览-top ap的usage排序正确"""
        log.debug("027")
        tmp = OverViewBusiness(self.s)
        usage = tmp.get_overview_top_aps_usage("1d")
        self.assertGreater(usage[0],usage[1])

    #验证最近两小时监控面板-概览-top ap的usage排序正确
    def test_028_check_2h_overview_top_ap_usage(self):
        u"""验证最近两小时监控面板-概览-top ap的usage排序正确"""
        log.debug("028")
        tmp = OverViewBusiness(self.s)
        usage = tmp.get_overview_top_aps_usage("2h")
        self.assertGreater(usage[0],usage[1])

     #验证最近两小时监控面板-概览-top ap的mac对应的name正确
    def test_029_check_2h_overview_top_ap_name(self):
        u"""验证最近两小时监控面板-概览-top ap的mac对应的name正确"""
        log.debug("029")
        tmp = OverViewBusiness(self.s)
        mac = data_ap['7610_mac'].upper()
        mac1 = data_ap['7600_mac'].upper()
        mac2 = data_ap['7600lr_mac'].upper()
        name = tmp.get_overview_top_aps_name("2h",mac)
        name1 = tmp.get_overview_top_aps_name("2h",mac1)
        name2 = tmp.get_overview_top_aps_name("2h",mac2)
        self.assertEqual("autotest_7610",name)
        self.assertEqual("autotest_7600",name1)
        self.assertEqual("autotest_7600lr",name2)

     #验证default network最近两小时监控面板-概览-top ap的mac对应的name正确
    def test_030_check_network_2h_overview_top_ap_name(self):
        u"""验证default network最近两小时监控面板-概览-top ap的mac对应的name正确"""
        log.debug("030")
        tmp = OverViewBusiness(self.s)
        mac = data_ap['7610_mac'].upper()
        name = tmp.get_overview_top_aps_name("2h",mac,menu=9)
        self.assertEqual("autotest_7610",name)

    #验证一天监控面板-概览-Top Clients，第一个client的mac地址
    def test_031_check_1d_overview_top_clients(self):
        u"""验证最近一天监控面板-概览-Top Clients，第一个client的mac地址"""
        log.debug("031")
        tmp = OverViewBusiness(self.s)
        wlan_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        result = tmp.check_overview_top_client("1d", wlan_mac)
        self.assertTrue(result)

    #验证最近2小时监控面板-概览-Top Clients，第一个client的mac地址
    def test_032_check_2h_overview_top_clients(self):
        u"""验证最近2小时监控面板-概览-Top Clients，第一个client的mac地址"""
        log.debug("032")
        tmp = OverViewBusiness(self.s)
        wlan_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        result = tmp.check_overview_top_client("2h", wlan_mac)
        self.assertTrue(result)

    #验证default network最近2小时监控面板-概览-Top Clients，第一个client的mac地址
    def test_033_check_network_2h_overview_top_clients(self):
        u"""验证default network最近2小时监控面板-概览-Top Clients，第一个client的mac地址"""
        log.debug("033")
        tmp = OverViewBusiness(self.s)
        wlan_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        result = tmp.check_overview_top_client("2h", wlan_mac,menu=9)
        self.assertTrue(result)

    #验证最近2小时监控面板-概览-Top Clients，第一个client的usage不为0
    def test_034_check_network_2h_overview_top_clients_usage(self):
        u"""验证最近2小时监控面板-概览-Top Clients，第一个client的usage不为0"""
        log.debug("034")
        tmp = OverViewBusiness(self.s)
        result = tmp.check_overview_top_client_usage("2h")
        self.assertTrue(result)

    #验证最近一天监控面板-概览-Top SSIDs，第一个SSID的name
    def test_035_check_1d_overview_top_ssids(self):
        u"""验证最近一天监控面板-概览-Top SSIDs，第一个SSID的name"""
        log.debug("035")
        tmp = OverViewBusiness(self.s)
        name = tmp.get_overview_top_ssids_name("1d")
        self.assertIn(data_wireless['all_ssid'],name)
        self.assertIn(data_wireless['grou1_all_ssid'],name)

    #验证最近两小时监控面板-概览-Top SSIDs
    def test_036_check_2h_overview_top_ssids(self):
        u"""验证最近两小时监控面板-概览-Top SSIDs"""
        log.debug("036")
        tmp = OverViewBusiness(self.s)
        name = tmp.get_overview_top_ssids_name("2h")
        self.assertIn(data_wireless['all_ssid'],name)
        self.assertIn(data_wireless['grou1_all_ssid'],name)

    #验证最近两小时监控面板-概览-Top SSIDs的usage
    def test_037_check_network_2h_overview_top_ssids_usage(self):
        u"""验证最近两小时监控面板-概览-Top SSIDs的usage"""
        log.debug("037")
        tmp = OverViewBusiness(self.s)
        usage= tmp.get_overview_top_ssids_usage("2h")
        self.assertGreater(usage[0],usage[1])
        self.assertGreater(usage[1],usage[2])

    #验证default network最近一天监控面板-概览-Top SSIDs的usage
    def test_038_check_network_1h_overview_top_ssids_usage(self):
        u"""验证default network最近一天监控面板-概览-Top SSIDs的usage"""
        log.debug("038")
        tmp = OverViewBusiness(self.s)
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network('group1')
        usage= tmp.get_overview_top_ssids_usage("1d",menu=9)
        self.assertGreater(usage[0],usage[1])

    #验证group1最近两小时监控面板-概览-Top SSIDs的usage
    def test_039_check_network_2h_overview_top_ssids_usage(self):
        u"""验证group1最近两小时监控面板-概览-Top SSIDs的usage"""
        log.debug("039")
        tmp = OverViewBusiness(self.s)
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network('group1')
        usage= tmp.get_overview_top_ssids_usage("2h",menu=9)
        self.assertGreater(usage[0],usage[1])

    #验证最近两小时监控面板-概览-Top SSIDs ssid与netwrok之间的对应关系
    def test_040_check_2h_overview_top_ssids(self):
        u"""验证最近两小时监控面板-概览-Top SSIDs ssid与netwrok之间的对应关系"""
        log.debug("040")
        tmp = OverViewBusiness(self.s)
        network = tmp.get_overview_top_ssids_network("2h",data_wireless['all_ssid'])
        network1 = tmp.get_overview_top_ssids_network("2h",data_wireless['grou1_all_ssid'])
        network2 = tmp.get_overview_top_ssids_network("2h",data_wireless['grou1_all_ssid']+"-2")
        self.assertEqual(network,'default')
        self.assertEqual(network1,'group1')
        self.assertEqual(network2,'group1')

    #验证group1 network中最近两小时监控面板-概览-Top SSIDs ssid与netwrok之间的对应关系
    def test_041_check_network_2h_overview_top_ssids(self):
        u"""验证group1 network中最近两小时监控面板-概览-Top SSIDs ssid与netwrok之间的对应关系"""
        log.debug("041")
        tmp = OverViewBusiness(self.s)
        tmp1 = NetworkListBusiness(self.s)
        tmp1.goin_network('group1')
        network1 = tmp.get_overview_top_ssids_network("2h",data_wireless['grou1_all_ssid'],menu=9)
        network2 = tmp.get_overview_top_ssids_network("2h",data_wireless['grou1_all_ssid']+"-2",menu=9)
        self.assertEqual(network1,'group1')
        self.assertEqual(network2,'group1')

    #检查network list中network的个数
    def test_042_check_network_list_count(self):
        u"""检查network list中network的个数"""
        log.debug("042")
        tmp = NetworkListBusiness(self.s)
        network_count = tmp.get_network_count()
        self.assertEqual(3,network_count)

    #检查network list中network的名称
    def test_043_check_network_list_name(self):
        u"""检查network list中network的名称"""
        log.debug("043")
        tmp = NetworkListBusiness(self.s)
        network_name = tmp.get_network_name()
        self.assertIn("default",network_name)
        self.assertIn("group1",network_name)
        self.assertIn("group2",network_name)

    #检查network list中每个network中的ap离线百分比
    def test_044_check_network_ap_offline(self):
        u"""检查network list中每个network中的ap离线百分比"""
        log.debug("044")
        tmp = NetworkListBusiness(self.s)
        network_offline = tmp.get_network_offiline()
        self.assertEqual([0,0,0],network_offline)

     #检查network list中每个network的ap总数
    def test_045_check_network_ap_total(self):
        u"""检查network list中每个network的ap总数"""
        log.debug("045")
        tmp = NetworkListBusiness(self.s)
        ap_total = tmp.get_network_ap_total()
        self.assertEqual([1,1,1],ap_total)

    #检查networklist中每个network的客户端数量
    def test_046_check_network_client(self):
        u"""检查networklist中每个network的客户端数量"""
        log.debug("046")
        tmp = NetworkListBusiness(self.s)
        network_client = tmp.get_network_client()
        self.assertEqual([0,1,0],network_client)

    #检查network list中default network的国家代码和时区(默认)
    def test_047_check_default_network_country_timezone(self):
        u"""检查default network的国家代码和时区(默认"""
        log.debug("047")
        tmp = NetworkListBusiness(self.s)
        id = tmp.get_network_id('default')
        network_country,network_timezone = tmp.get_networkitem_country_timezone(id)
        self.assertEqual('US',network_country)
        self.assertEqual("Etc/GMT",network_timezone)

     #检查network list中group1 network的国家代码和时区
    def test_048_check_network_country_timezone(self):
        u"""检查group1 network的国家代码和时区"""
        log.debug("048")
        tmp = NetworkListBusiness(self.s)
        id = tmp.get_network_id('group1')
        network_country,network_timezone = tmp.get_networkitem_country_timezone(id)
        self.assertEqual('US',network_country)
        self.assertEqual("Etc/GMT",network_timezone)

     #检查network list中group2 network的国家代码和时区
    def test_049_check_network_country_timezone(self):
        u"""检查group2 network的国家代码和时区"""
        log.debug("049")
        tmp = NetworkListBusiness(self.s)
        id = tmp.get_network_id('group2')
        network_country,network_timezone = tmp.get_networkitem_country_timezone(id)
        self.assertEqual('US',network_country)
        self.assertEqual("Etc/GMT",network_timezone)

    #检查network list中default network的网络管理员
    def test_050_check_default_network_uesr(self):
        u"""检查default network的网络管理员"""
        log.debug("050")
        tmp = NetworkListBusiness(self.s)
        id = tmp.get_network_id('default')
        count,user = tmp.get_networkitem_all_user(id)
        self.assertEqual(2,count)
        self.assertIn(data_basic['cloud_user'],user)
        self.assertIn(data_basic['Cloud_test_user'],user)

    #检查network list中group1 network的网络管理员
    def test_051_check_group1_network_uesr(self):
        u"""检查group1 network的网络管理员"""
        log.debug("051")
        tmp = NetworkListBusiness(self.s)
        id = tmp.get_network_id('group1')
        count,user = tmp.get_networkitem_all_user(id)
        self.assertEqual(2,count)
        self.assertIn(data_basic['cloud_user'],user)
        self.assertIn(data_basic['Cloud_test_user'],user)

    #检查network list中group2 network的网络管理员
    def test_052_check_group2_network_uesr(self):
        u"""检查group2 network的网络管理员"""
        log.debug("052")
        tmp = NetworkListBusiness(self.s)
        id = tmp.get_network_id('group1')
        count,user = tmp.get_networkitem_all_user(id)
        self.assertEqual(2,count)
        self.assertIn(data_basic['cloud_user'],user)
        self.assertIn(data_basic['Cloud_test_user'],user)

    #检查ap_list中ap的设备类型，固件版本，网络是否正确
    def test_053_ap_list_7610(self):
        u"""检查ap_list中7610的设备类型，固件版本，网络是否正确"""
        log.debug("053")
        tmp = AllApListBusiness(self.s)
        ap_type,ap_network,ap_ip,ap_version = tmp.\
                                get_ap_detail(data_ap['7610_mac'])
        self.assertEqual("GWN7610",ap_type)
        self.assertEqual(data_basic['7610_ip'],ap_ip)
        self.assertEqual("default",ap_network)
        self.assertEqual(ap_version,data_basic['7610_new_version'])

    #检查ap_list中ap的设备类型，固件版本，网络是否正确
    def test_054_ap_list_7600(self):
        u"""检查ap_list中7600的设备类型，固件版本，网络是否正确"""
        log.debug("054")
        tmp = AllApListBusiness(self.s)
        ap_type,ap_network,ap_ip,ap_version = tmp.\
                                get_ap_detail(data_ap['7600_mac'])
        self.assertEqual("GWN7600",ap_type)
        self.assertEqual(data_basic['7600_ip'],ap_ip)
        self.assertEqual("group1",ap_network)
        self.assertEqual(ap_version,data_basic['7600_new_version'])

    #检查ap_list中ap的设备类型，固件版本，网络是否正确
    def test_056_ap_list_7600lr(self):
        u"""检查ap_list中7600lr的设备类型，固件版本，网络是否正确"""
        log.debug("056")
        tmp = AllApListBusiness(self.s)
        ap_type,ap_network,ap_ip,ap_version = tmp.\
                                get_ap_detail(data_ap['7600lr_mac'])
        self.assertEqual("GWN7600LR",ap_type)
        self.assertEqual(data_basic['7600lr_ip'],ap_ip)
        self.assertEqual("group2",ap_network)
        self.assertEqual(ap_version,data_basic['7600_new_version'])

    #删除ap，并恢复cloud的初始环境
    def test_057_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("057")
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
        tmp1 = NetworkListBusiness(self.s)
        tmp.delete_ap(data_ap['7610_mac'])
        tmp1.goin_network('group1')
        tmp.delete_ap(data_ap['7600_mac'])
        tmp1.goin_network('group2')
        tmp.delete_ap(data_ap['7600lr_mac'])
        tmp1.delete_network('group1')
        tmp1.delete_network('group2')
        time.sleep(360)


    def tearDown(self):
        pass




if __name__ == '__main__':
    unittest.main()