#coding=utf-8
#作者：曾祥卫
#时间：2018.06.11
#描述：cloud监控面板-网络列表用例集，调用networklist_business

import unittest, time
from dashboard.network_list.networklist_business import NetworkListBusiness
from navbar.user.user_business import UserBusiness
from dashboard.ap_list.allaplist_business import AllApListBusiness
from access_points.aps_business import APSBusiness
from ssids.ssids_business import SSIDSBusiness
from data import data
from data.logfile import Log
import requests
log = Log("networklist")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()




class TestNetworkList(unittest.TestCase):
    u"""测试监控面板-网络列表的用例集(runtime:0.25h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = NetworkListBusiness(self.s)
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])



    #创建新的网络组并判断是否添加成功
    def test_001_add_network(self):
        u"""创建新的网络组并判断是否添加成功"""
        log.debug("001")
        #获取登录名对应的id
        tmp1 =UserBusiness(self.s)

        #描述：启用无线网卡
        tmp1.wlan_enable(data_basic['wlan_pc'])
        tmp1.dhcp_release_wlan(data_basic['wlan_pc'])

        user_id = tmp1.get_network_id(data_basic['cloud_user'])
        tmp = NetworkListBusiness(self.s)
        #添加网络组
        tmp.add_network("group1", user_id, "")
        time.sleep(60)
        #获取网络组对应的id--监控面板--网络列表
        network_id = tmp.get_network_id("group1")
        self.assertNotEqual(network_id, None)

    #新建的网络组添加ap
    def test_002_newNetwork_add_ap(self):
        u"""新建的网络组添加ap"""
        log.debug("002")
        tmp = NetworkListBusiness(self.s)
        #选择进入group1网络组
        tmp.goin_network("group1")
        #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
        tmp1 = APSBusiness(self.s)
        tmp1.add_ap_2_local_cloud(data_basic['7610_ip'], data_ap['7610_mac'], "autotest_7610")
        time.sleep(60)
        #获取ap列表ap的网络组名
        tmp2 = AllApListBusiness(self.s)
        network_name = tmp2.get_ap_info(data_ap['7610_mac'])['network']
        self.assertEqual(network_name, "group1")

    #无线连接该ap
    def test_003_client_connect_newNetwork_ap(self):
        u"""无线连接该ap"""
        log.debug("003")
        tmp = NetworkListBusiness(self.s)
        #选择进入group1网络组
        tmp.goin_network("group1")
        #修改新网络组的ssid
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['all_ssid']+"-group1"
                     }
        tmp1.edit_ssid(data_ap['7610_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接ap
        result = tmp.connect_WPA_AP(data_wireless['all_ssid']+"-group1",
                                    data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #移动ap-从default移动到group1
    def test_004_remove_ap1(self):
        u"""移动ap-从default移动到group1"""
        log.debug("004")
        #获取group1的id
        tmp = NetworkListBusiness(self.s)
        network_id = tmp.get_network_id("group1")
        #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
        tmp1 = APSBusiness(self.s)
        tmp1.add_ap_2_local_cloud(data_basic['7600lr_ip'], data_ap['7600lr_mac'], "autotest_7600lr")
        time.sleep(60)
        #移动该ap到group1中
        tmp1.move_aps(data_ap['7600lr_mac'].upper(), network_id)
        time.sleep(60)
        #获取ap列表ap的网络组名
        tmp2 = AllApListBusiness(self.s)
        network_name = tmp2.get_ap_info(data_ap['7600lr_mac'])['network']
        self.assertEqual(network_name, "group1")

    #移动ap-从group1移动到default
    def test_005_remove_ap2(self):
        u"""移动ap-从group1移动到default"""
        log.debug("005")
        #获取default的id
        tmp = NetworkListBusiness(self.s)
        network_id = tmp.get_network_id("default")
        #选择进入group1网络组
        tmp.goin_network("group1")
        #移动该ap到group1中
        tmp1 = APSBusiness(self.s)
        tmp1.move_aps(data_ap['7600lr_mac'].upper(), network_id)
        time.sleep(60)
        #获取ap列表ap的网络组名
        tmp2 = AllApListBusiness(self.s)
        network_name = tmp2.get_ap_info(data_ap['7600lr_mac'])['network']
        self.assertEqual(network_name, "default")

    #移动多ap-从default移动到group1
    def test_006_remove_many_aps1(self):
        u"""移动多ap-从default移动到group1"""
        log.debug("006")
        #获取group1的id
        tmp = NetworkListBusiness(self.s)
        network_id = tmp.get_network_id("group1")
        #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
        tmp1 = APSBusiness(self.s)
        tmp1.add_ap_2_local_cloud(data_basic['7600_ip'], data_ap['7600_mac'], "autotest_7600")
        time.sleep(60)
        #移动两个ap（7600,7600lr）到group1中
        tmp1.move_aps("%s,%s"%(data_ap['7600_mac'].upper(),data_ap['7600lr_mac'].upper()), network_id)
        time.sleep(60)
        #获取ap列表ap的网络组名
        tmp2 = AllApListBusiness(self.s)
        network_name_7600lr = tmp2.get_ap_info(data_ap['7600lr_mac'])['network']
        network_name_7600 = tmp2.get_ap_info(data_ap['7600_mac'])['network']
        self.assertEqual(network_name_7600lr, "group1")
        self.assertEqual(network_name_7600, "group1")

    #移动多ap-从group1移动到default
    def test_007_remove_many_aps2(self):
        u"""移动多ap-从group1移动到default"""
        log.debug("007")
        #获取default的id
        tmp = NetworkListBusiness(self.s)
        network_id = tmp.get_network_id("default")
        #选择进入group1网络组
        tmp.goin_network("group1")
        #移动三个ap（7600,7600lr，7610）到group1中
        tmp1 = APSBusiness(self.s)
        tmp1.move_aps(data_ap['7600lr_mac'].upper(), network_id)
        tmp1.move_aps(data_ap['7600_mac'].upper(), network_id)
        tmp1.move_aps(data_ap['7610_mac'].upper(), network_id)
        time.sleep(60)
        #获取ap列表ap的网络组名
        tmp2 = AllApListBusiness(self.s)
        network_name_7600lr = tmp2.get_ap_info(data_ap['7600lr_mac'])['network']
        network_name_7600 = tmp2.get_ap_info(data_ap['7600_mac'])['network']
        network_name_7610 = tmp2.get_ap_info(data_ap['7610_mac'])['network']
        self.assertEqual(network_name_7600lr, "default")
        self.assertEqual(network_name_7600, "default")
        self.assertEqual(network_name_7610, "default")

    #删除新建的网络组
    def test_008_delete_newNetwork(self):
        u"""删除新建的网络组"""
        log.debug("008")
        #删除网络组group1
        tmp = NetworkListBusiness(self.s)
        tmp.delete_network("group1")
        time.sleep(60)
        #获取网络组对应的id--监控面板--网络列表
        network_id = tmp.get_network_id("group1")
        self.assertEqual(network_id, None)

    #删除ap，并恢复cloud的初始环境
    def test_009_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("009")
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
