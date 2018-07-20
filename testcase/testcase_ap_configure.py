#coding=utf-8
#作者：曾祥卫
#时间：2018.03.20
#描述：Network-APs-Configure用例集，调用aps_business

import unittest,time
from access_points.aps_business import APSBusiness
from system.settings.settings_business import SettingsBusiness
from ssids.ssids_business import SSIDSBusiness
from data import data
from connect.ssh import SSH
from data.logfile import Log
import requests
log = Log("ap_configure")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()

class TestAPConfigure(unittest.TestCase):
    u"""测试Network-APs-Configure的用例集(runtime:4.04h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = APSBusiness(self.s)
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

    #按照设备类型进行过滤
    def test_002_aps_configure_filter_with_type(self):
        u"""按照设备类型进行过滤(testlinkID:763)"""
        log.debug("002")
        tmp = APSBusiness(self.s)
        time.sleep(180)
        result_7610 = tmp.check_configure_filter_ap("GWN7610")
        result_7600 = tmp.check_configure_filter_ap("GWN7600")
        result_7600lr = tmp.check_configure_filter_ap("GWN7600LR")
        self.assertTrue(result_7610)
        self.assertTrue(result_7600)
        self.assertTrue(result_7600lr)
        print "filter ap with ap type pass!"

    #按照ap完整mac进行搜索
    def test_003_aps_configure_search_all_mac(self):
        u"""按照ap完整mac进行搜索(testlinkID:764-1)"""
        log.debug("003")
        tmp = APSBusiness(self.s)
        result_7610 = tmp.check_configure_search_ap(data_ap['7610_mac'], data_ap['7610_mac'])
        result_7600 = tmp.check_configure_search_ap(data_ap['7600_mac'], data_ap['7600_mac'])
        result_7600lr = tmp.check_configure_search_ap(data_ap['7600lr_mac'], data_ap['7600lr_mac'])
        self.assertTrue(result_7610)
        self.assertTrue(result_7600)
        self.assertTrue(result_7600lr)
        print "search ap with ap's all mac pass!"

    #按照ap部分mac进行搜索
    def test_004_aps_configure_search_part_mac(self):
        u"""按照ap部分mac进行搜索(testlinkID:764-2)"""
        log.debug("004")
        tmp = APSBusiness(self.s)
        #取得mac地址的后6位mac地址
        search_str_7610 = tmp.get_last_6mac(data_ap['7610_mac'])
        search_str_7600 = tmp.get_last_6mac(data_ap['7600_mac'])
        search_str_7600lr = tmp.get_last_6mac(data_ap['7600lr_mac'])
        result_7610 = tmp.check_configure_search_ap(search_str_7610, data_ap['7610_mac'])
        result_7600 = tmp.check_configure_search_ap(search_str_7600, data_ap['7600_mac'])
        result_7600lr = tmp.check_configure_search_ap(search_str_7600lr, data_ap['7600lr_mac'])
        self.assertTrue(result_7610)
        self.assertTrue(result_7600)
        self.assertTrue(result_7600lr)
        print "search ap with ap's part mac pass!"

    #按照ap完整名称进行搜索
    def test_005_aps_configure_search_all_name(self):
        u"""按照ap完整名称进行搜索(testlinkID:764-3)"""
        log.debug("005")
        tmp = APSBusiness(self.s)
        result_7610 = tmp.check_configure_search_ap("autotest_7610", data_ap['7610_mac'])
        result_7600 = tmp.check_configure_search_ap("autotest_7600", data_ap['7600_mac'])
        result_7600lr = tmp.check_configure_search_ap("autotest_7600lr", data_ap['7600lr_mac'])
        self.assertTrue(result_7610)
        self.assertTrue(result_7600)
        self.assertTrue(result_7600lr)
        print "search ap with ap's all name pass!"

    #按照ap部分名称进行搜索
    def test_006_aps_configure_search_part_name(self):
        u"""按照ap部分名称进行搜索(testlinkID:764-4)"""
        log.debug("006")
        tmp = APSBusiness(self.s)
        result_7610 = tmp.check_configure_search_ap("7610", data_ap['7610_mac'])
        result_7600 = tmp.check_configure_search_ap("7600", data_ap['7600_mac'])
        result_7600lr = tmp.check_configure_search_ap("7600lr", data_ap['7600lr_mac'])
        self.assertTrue(result_7610)
        self.assertTrue(result_7600)
        self.assertTrue(result_7600lr)
        print "search ap with ap's part name pass!"

    #设备类型的过滤和名称/mac的筛选方式是并列方式
    def test_007_aps_configure_fliter_search_ap_mac(self):
        u"""设备类型的过滤和名称/mac的筛选方式是并列方式-mac(testlinkID:765-1)"""
        log.debug("007")
        tmp = APSBusiness(self.s)
        result_7610 = tmp.check_configure_filter_search_ap("GWN7610", data_ap['7610_mac'], data_ap['7610_mac'])
        result_7600 = tmp.check_configure_filter_search_ap("GWN7600", data_ap['7600_mac'], data_ap['7600_mac'])
        result_7600lr = tmp.check_configure_filter_search_ap("GWN7600LR", data_ap['7600lr_mac'], data_ap['7600lr_mac'])
        self.assertTrue(result_7610)
        self.assertTrue(result_7600)
        self.assertTrue(result_7600lr)
        print "search ap with ap's fiter and search mac pass!"

    #设备类型的过滤和名称/mac的筛选方式是并列方式
    def test_008_aps_configure_fliter_search_ap_name(self):
        u"""设备类型的过滤和名称/mac的筛选方式是并列方式-name(testlinkID:765-2)"""
        log.debug("008")
        tmp = APSBusiness(self.s)
        result_7610 = tmp.check_configure_filter_search_ap("GWN7610", "autotest_7610", data_ap['7610_mac'])
        result_7600 = tmp.check_configure_filter_search_ap("GWN7600", "autotest_7600", data_ap['7600_mac'])
        result_7600lr = tmp.check_configure_filter_search_ap("GWN7600LR", "autotest_7600lr", data_ap['7600lr_mac'])
        self.assertTrue(result_7610)
        self.assertTrue(result_7600)
        self.assertTrue(result_7600lr)
        print "search ap with ap's fiter and search name pass!"

    #正确显示设备类型model
    def test_009_aps_configure_device_type(self):
        u"""正确显示设备类型model(testlinkID:767)"""
        log.debug("009")
        tmp = APSBusiness(self.s)
        #判断设备类型和对应的mac地址显示正确
        result = tmp.check_configure_type_mac()
        self.assertNotIn(False,result)
        print "ap configure display device type pass!"

    #正确显示设备名称name
    def test_010_aps_configure_device_name_asii(self):
        u"""正确显示设备名称name-特殊字符(testlinkID:768-1)"""
        log.debug("010")
        tmp = APSBusiness(self.s)
        #修改7610的设备名称为特殊字符
        tmp.edit_ap(data_ap['7610_mac'], {"ap_name": data_login['asii_pwd']})
        #判断ap名称是否正确
        result = tmp.check_configure_device_name("GWN7610", data_login['asii_pwd'])
        self.assertTrue(result)
        print "check device name is asii pass!"

    #正确显示设备名称name
    def test_011_aps_configure_device_name_32bits(self):
        u"""正确显示设备名称name-32bits(testlinkID:768-2)"""
        log.debug("011")
        tmp = APSBusiness(self.s)
        #修改7610的设备名称为特殊字符
        tmp.edit_ap(data_ap['7610_mac'], {"ap_name": data_wireless['long_ssid']})
        #判断ap名称是否正确
        result = tmp.check_configure_device_name("GWN7610", data_wireless['long_ssid'])
        #修改7610的设备名称修改回autotest_7610
        tmp.edit_ap(data_ap['7610_mac'], {"ap_name": "autotest_7610"})
        self.assertTrue(result)
        print "check device name is 32bits pass!"

    #正确显示mac
    def test_012_aps_configure_device_mac(self):
        u"""正确显示mac(testlinkID:769)"""
        log.debug("012")
        tmp = APSBusiness(self.s)
        #判断设备类型和对应的mac地址显示正确
        result = tmp.check_configure_type_mac()
        self.assertNotIn(False,result)
        print "ap configure display device mac pass!"

    #正确显示ip类型
    def test_013_aps_configure_ip(self):
        u"""正确显示ip类型(testlinkID:770)"""
        log.debug("013")
        tmp = APSBusiness(self.s)
        #判断ap的ip类型是否正确
        result_7600 = tmp.check_configure_ip_model("GWN7600", "dynamic")
        result_7610 = tmp.check_configure_ip_model("GWN7610", "dynamic")
        result_7600lr = tmp.check_configure_ip_model("GWN7600LR", "dynamic")
        self.assertTrue(result_7600)
        self.assertTrue(result_7610)
        self.assertTrue(result_7600lr)
        print "check ip model displayed pass!"

    #正确显示固件版本
    def test_014_aps_configure_version(self):
        u"""正确显示固件版本(testlinkID:772)"""
        log.debug("014")
        #获取网络组的ssh密码
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        tmp = APSBusiness(self.s)
        result_7610 = tmp.check_configure_fw("GWN7610", data_basic['7610_ip'],
                    data_basic['sshUser'], ssh_pwd)
        result_7600 = tmp.check_configure_fw("GWN7600", data_basic['7600_ip'],
                    data_basic['sshUser'], ssh_pwd)
        result_7600lr = tmp.check_configure_fw("GWN7600LR", data_basic['7600lr_ip'],
                    data_basic['sshUser'], ssh_pwd)
        self.assertTrue(result_7600)
        self.assertTrue(result_7610)
        self.assertTrue(result_7600lr)
        print "check ap's version displayed pass!"

    #正确显示当前信道channel
    def test_015_aps_configure_channel(self):
        u"""正确显示当前信道channel(testlinkID:773)"""
        log.debug("015")
        tmp = APSBusiness(self.s)
        #修改7600信道：2.4g-1,5g-36
        tmp.edit_ap(data_ap['7600_mac'], {"ap_2g4_channel": "1", "ap_5g_channel": "36"})
        #修改7610信道：2.4g-1,5g-161
        tmp.edit_ap(data_ap['7610_mac'], {"ap_2g4_channel": "1", "ap_5g_channel": "161"})
        #修改7600lr信道：2.4g-11,5g-40
        tmp.edit_ap(data_ap['7600lr_mac'], {"ap_2g4_channel": "11", "ap_5g_channel": "40"})
        #等待6分钟，等ap将信息上报给cloud
        time.sleep(360)
        result_7600 = tmp.check_configure_channel("GWN7600", 1, 36)
        result_7610 = tmp.check_configure_channel("GWN7610", 1, 161)
        result_7600lr = tmp.check_configure_channel("GWN7600LR", 11, 40)
        self.assertTrue(result_7600)
        self.assertTrue(result_7610)
        self.assertTrue(result_7600lr)
        print "check ap's channel displayed pass!"

    #正确显示当前无线电传输功率
    def test_016_aps_configure_power(self):
        u"""正确显示当前无线电传输功率(testlinkID:774)"""
        log.debug("016")
        #获取网络组的ssh密码
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        tmp = APSBusiness(self.s)
        result_7610 = tmp.check_configure_power("GWN7610", data_basic['7610_ip'],
                    data_basic['sshUser'], ssh_pwd)
        result_7600 = tmp.check_configure_power("GWN7600", data_basic['7600_ip'],
                    data_basic['sshUser'], ssh_pwd)
        result_7600lr = tmp.check_configure_power("GWN7600LR", data_basic['7600lr_ip'],
                    data_basic['sshUser'], ssh_pwd)
        self.assertTrue(result_7600)
        self.assertTrue(result_7610)
        self.assertTrue(result_7600lr)
        print "check ap's power displayed pass!"

    #在线AP点击定位键
    def test_017_aps_configure_locate(self):
        u"""在线AP点击定位键(testlinkID:776)"""
        log.debug("017")
        tmp = APSBusiness(self.s)
        result_7610 = tmp.click_locate(data_ap['7610_mac'])
        result_7600 = tmp.click_locate(data_ap['7600_mac'])
        result_7600lr = tmp.click_locate(data_ap['7600lr_mac'])
        time.sleep(30)
        self.assertEqual(0, result_7610['retCode'])
        self.assertEqual(0, result_7600['retCode'])
        self.assertEqual(0, result_7600lr['retCode'])
        print "click ap locate button pass!"

    #重启单个在线AP
    def test_018_aps_configure_reboot_ap(self):
        u"""重启单个在线AP(testlinkID:783)"""
        log.debug("018")
        tmp = APSBusiness(self.s)
        #重启单个ap
        tmp.reboot_one_ap(data_ap['7610_mac'])
        result = tmp.check_ap_reboot([data_basic['7610_ip']])
        self.assertNotIn(False, result)
        print "check reboot one ap pass!"

    #重启多个在线AP
    def test_019_aps_configure_reboot_many_aps(self):
        u"""重启单个在线AP(testlinkID:784)"""
        log.debug("019")
        tmp = APSBusiness(self.s)
        #重启多个ap
        time.sleep(160)
        tmp.reboot_many_aps(data_ap['7610_mac'], data_ap['7600_mac'], data_ap['7600lr_mac'])
        result = tmp.check_ap_reboot([data_basic['7610_ip'],
                    data_basic['7600_ip'], data_basic['7600lr_ip']])
        self.assertNotIn(False, result)
        print "check reboot many aps pass!"

    #删除单个在线AP
    def test_020_aps_configure_delete_one_ap(self):
        u"""删除单个在线AP(testlinkID:787)"""
        log.debug("020")
        tmp = APSBusiness(self.s)
        time.sleep(160)
        #cloud删除ap
        tmp.delete_ap(data_ap['7600_mac'])
        time.sleep(360)
        result = tmp.check_ap_factory(data_basic['7600_ip'])
        self.assertTrue(result)
        print "check delete one ap pass!"

    #删除多个在线ap
    def test_021_aps_configure_delete_many_ap(self):
        u"""删除单个在线AP(testlinkID:788)"""
        log.debug("021")
        tmp = APSBusiness(self.s)
        #cloud删除ap
        tmp.delete_many_ap(data_ap['7610_mac'], data_ap['7600lr_mac'])
        time.sleep(360)
        result1 = tmp.check_ap_factory(data_basic['7610_ip'])
        result2 = tmp.check_ap_factory(data_basic['7600lr_ip'])
        self.assertTrue(result1)
        self.assertTrue(result2)
        print "check delete many aps pass!"

    #AP被删除之后，还可以重新添加到相同账号的相同网络组
    def test_022_aps_configure_add_ap_2_same_network(self):
        u"""AP被删除之后，还可以重新添加到相同账号的相同网络组(testlinkID:789)"""
        log.debug("022")
        tmp = APSBusiness(self.s)
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

    #配置参数正确的固定IP，网关，DNS
    def test_023_aps_configure_static_ip(self):
        u"""配置参数正确的固定IP，网关，DNS(testlinkID:832)"""
        log.debug("023")
        tmp = APSBusiness(self.s)
        time.sleep(180)
        #将ap改为静态ip
        tmp.edit_ap(data_ap['7600_mac'], {'ap_static': "1",
                                          'ap_ipv4_static': data_basic['7600_ip'],
                                          'ap_ipv4_static_mask': data_ap['fixed_netmask'],
                                          'ap_ipv4_route': data_basic['7000_ip'],
                                          'ap_preferred_dns': "180.76.76.76"
                                          })
        time.sleep(120)
        #判断是否能够ping通
        result = tmp.get_ping(data_basic['7600_ip'])
        #再将ap改回dhcp
        tmp.edit_ap(data_ap['7600_mac'], {'ap_static': "0"})
        time.sleep(120)
        self.assertEqual(0,result)
        print "check config ap static ip pass!"

    #频段切换配置-默认关闭
    def test_024_aps_configure_band_steering_default(self):
        u"""频段切换配置-默认关闭(testlinkID:833-1)"""
        log.debug("024")
        tmp = SettingsBusiness(self.s)
        ssh_pwd = tmp.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "ps")
        self.assertNotIn("lbd", result1)
        print "check band steering default is close pass!"

    #频段切换配置-选择均衡
    def test_025_aps_configure_band_steering_balance(self):
        u"""频段切换配置-选择均衡(testlinkID:833-2)--bug113938"""
        log.debug("025")
        #修改ap的频段切换为均衡
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'],{'ap_band_steering': "3"})
        time.sleep(120)
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        MAC = tmp1.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "ps")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.band_steering"%mac)
        self.assertIn("lbd", result1)
        self.assertIn("3", result2)
        print "check band steering is balance pass!"

    #重启ap后，频段切换配置-配置依然是均衡
    def test_026_aps_configure_band_steering_balance_after_reboot(self):
        u"""重启ap后，频段切换配置-配置依然是均衡(testlinkID:833-3)--bug113938"""
        log.debug("026")
        #reboot ap
        tmp = APSBusiness(self.s)
        tmp.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(420)
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        MAC = tmp1.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "ps")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.band_steering"%mac)
        self.assertIn("lbd", result1)
        self.assertIn("3", result2)
        print "check band steering is balance after rebooting pass!"

    #频段切换配置-选择2.4G优先
    def test_027_aps_configure_band_steering_2g4(self):
        u"""频段切换配置-选择2.4G优先(testlinkID:833-4)--bug113938"""
        log.debug("027")
        #修改ap的频段切换为均衡
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'],{'ap_band_steering': "1"})
        time.sleep(120)
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        MAC = tmp1.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "ps")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.band_steering"%mac)
        self.assertIn("lbd", result1)
        self.assertIn("1", result2)
        print "check band steering is 2.4G first pass!"

    #重启ap后，频段切换配置-配置依然是2.4G优先
    def test_028_aps_configure_band_steering_2g4_after_reboot(self):
        u"""重启ap后，频段切换配置-配置依然是2.4G优先(testlinkID:833-5)--bug113938"""
        log.debug("028")
        #reboot ap
        tmp = APSBusiness(self.s)
        tmp.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(420)
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        MAC = tmp1.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "ps")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.band_steering"%mac)
        self.assertIn("lbd", result1)
        self.assertIn("1", result2)
        print "check band steering is 2.4G first after rebooting pass!"

    #频段切换配置-选择5G优先
    def test_029_aps_configure_band_steering_5g(self):
        u"""频段切换配置-选择5G优先(testlinkID:833-6)--bug113938"""
        log.debug("029")
        #修改ap的频段切换为均衡
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'],{'ap_band_steering': "2"})
        time.sleep(120)
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        MAC = tmp1.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "ps")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.band_steering"%mac)
        self.assertIn("lbd", result1)
        self.assertIn("2", result2)
        print "check band steering is 5G first pass!"

    #重启ap后，频段切换配置-配置依然是5G优先
    def test_030_aps_configure_band_steering_5g_after_reboot(self):
        u"""重启ap后，频段切换配置-配置依然是5G优先(testlinkID:833-7)--bug113938"""
        log.debug("030")
        #reboot ap
        tmp = APSBusiness(self.s)
        tmp.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(420)
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        MAC = tmp1.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "ps")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.band_steering"%mac)
        self.assertIn("lbd", result1)
        self.assertIn("2", result2)
        print "check band steering is 5G first after rebooting pass!"

    #频段切换配置-关闭频段切换
    def test_031_aps_configure_band_steering_close(self):
        u"""频段切换配置-关闭频段切换(testlinkID:833-8)"""
        log.debug("031")
        #修改ap的频段切换为均衡
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'],{'ap_band_steering': "0"})
        time.sleep(120)
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        MAC = tmp1.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "ps")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.band_steering"%mac)
        self.assertNotIn("lbd", result1)
        self.assertIn("0", result2)
        print "check close band steering pass!"

    #重启ap后，频段切换配置-配置依然是关闭频段切换
    def test_032_aps_configure_band_steering_close_after_reboot(self):
        u"""重启ap后，频段切换配置-配置依然是关闭频段切换(testlinkID:833-9)"""
        log.debug("032")
        #reboot ap
        tmp = APSBusiness(self.s)
        tmp.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(420)
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        MAC = tmp1.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "ps")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.band_steering"%mac)
        self.assertNotIn("lbd", result1)
        self.assertIn("0", result2)
        print "check close band steering after rebooting pass!"

    #模式，2.4G，11b
    def test_033_aps_configure_2g4_11b(self):
        u"""模式，2.4G，11b(testlinkID:840-1)"""
        log.debug("033")
        #改变ssid为2.4G和ssid
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['all_ssid'],
                     'ssid_ssid_band': "2",
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7610_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(60)
        tmp = APSBusiness(self.s)
        #改变2.4G模式为11b
        tmp.edit_ap(data_ap['7610_mac'],{'ap_2g4_mode': "0"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath0 | grep Bit")
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid'],\
                        data_wireless["short_wpa"], data_basic["wlan_pc"])
        self.assertIn("11", result1)
        self.assertIn(data_wireless['all_ssid'], result2)
        print "check 2.4G and 11b pass!"

    #重启ap，模式，2.4G，11b结果不变
    def test_034_aps_configure_2g4_11b_after_reboot(self):
        u"""重启ap，模式，2.4G，11b结果不变(testlinkID:840-2)"""
        log.debug("034")
        #reboot ap
        tmp = APSBusiness(self.s)
        tmp.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(420)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath0 | grep Bit")
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid'],\
                        data_wireless["short_wpa"],data_basic["wlan_pc"])
        self.assertIn("11", result1)
        self.assertIn(data_wireless['all_ssid'], result2)
        print "check 2.4G and 11b after rebooting pass!"

    #模式，2.4G，11g
    def test_035_aps_configure_2g4_11g(self):
        u"""模式，2.4G，11b(testlinkID:841-1)"""
        log.debug("035")
        tmp = APSBusiness(self.s)
        #改变2.4G模式为11g
        tmp.edit_ap(data_ap['7610_mac'],{'ap_2g4_mode': "1"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath0 | grep Bit")
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid'],\
                        data_wireless["short_wpa"],data_basic["wlan_pc"])
        self.assertIn("54", result1)
        self.assertIn(data_wireless['all_ssid'], result2)
        print "check 2.4G and 11g pass!"

    #重启ap，模式，2.4G，11g结果不变
    def test_036_aps_configure_2g4_11g_after_reboot(self):
        u"""重启ap，模式，2.4G，11g结果不变(testlinkID:841-2)"""
        log.debug("036")
        #reboot ap
        tmp = APSBusiness(self.s)
        tmp.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(600)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath0 | grep Bit")
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid'],\
                        data_wireless["short_wpa"],data_basic["wlan_pc"])
        self.assertIn("54", result1)
        self.assertIn(data_wireless['all_ssid'], result2)
        print "check 2.4G and 11g after rebooting pass!"

    #模式，2.4G，11n
    def test_037_aps_configure_2g4_11n(self):
        u"""模式，2.4G，11n(testlinkID:842-1)"""
        log.debug("037")
        tmp = APSBusiness(self.s)
        #改变2.4G模式为11n
        tmp.edit_ap(data_ap['7610_mac'],{'ap_2g4_mode': "2"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath0 | grep Bit")
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid'],\
                        data_wireless["short_wpa"],data_basic["wlan_pc"])
        self.assertIn("216.7", result1)
        self.assertIn(data_wireless['all_ssid'], result2)
        print "check 2.4G and 11n pass!"

    #重启ap，模式，2.4G，11n结果不变
    def test_038_aps_configure_2g4_11n_after_reboot(self):
        u"""重启ap，模式，2.4G，11n结果不变(testlinkID:842-2)"""
        log.debug("038")
        #reboot ap
        tmp = APSBusiness(self.s)
        tmp.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(600)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath0 | grep Bit")
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid'],\
                        data_wireless["short_wpa"],data_basic["wlan_pc"])
        self.assertIn("216.7", result1)
        self.assertIn(data_wireless['all_ssid'], result2)
        print "check 2.4G and 11n after rebooting pass!"

    #模式，5G，11ac
    def test_039_aps_configure_5g_11ac(self):
        u"""模式，5G，11ac(testlinkID:843-1)"""
        log.debug("039")
        #改变ssid为5G
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath0 | grep Bit")
        result2 = tmp2.connect_WPA_AP(data_wireless['all_ssid'],\
                        data_wireless["short_wpa"],data_basic["wlan_pc"])
        self.assertIn("1.3", result1)
        self.assertIn(data_wireless['all_ssid'], result2)
        print "check 5G and 11ac pass!"

    #重启ap，模式，5G，11ac结果不变
    def test_040_aps_configure_5g_11ac_after_reboot(self):
        u"""重启ap，模式，5G，11ac结果不变(testlinkID:843-2)"""
        log.debug("040")
        #reboot ap
        tmp = APSBusiness(self.s)
        tmp.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(600)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath0 | grep Bit")
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid'],\
                        data_wireless["short_wpa"],data_basic["wlan_pc"])
        self.assertIn("1.3", result1)
        self.assertIn(data_wireless['all_ssid'], result2)
        print "check 5G and 11ac after rebooting pass!"

    #信道带宽，2.4G 20MHz
    def test_041_aps_configure_2g4_20MHz(self):
        u"""信道带宽，2.4G 20MHz(testlinkID:844)"""
        log.debug("041")
        #AP改为dual-band
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': ""}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.htmode")
        self.assertIn("HT20", result)
        print "check 2.4G 20MHz pass!"

    #信道带宽，2.4G 20MHz/40MHz
    def test_042_aps_configure_2g4_40MHz(self):
        u"""信道带宽，2.4G 20MHz/40MHz(testlinkID:845)"""
        log.debug("042")
        #修改ap信道带宽为40M
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_width': "1"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.htmode")
        self.assertIn("HT40", result)
        print "check 2.4G 40MHz pass!"

    #信道带宽，5G，20MHz
    def test_043_aps_configure_5g_20MHz(self):
        u"""信道带宽，5G，20MHz(testlinkID:846)"""
        log.debug("043")
        #修改ap信道带宽为20M
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_width': "0"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.htmode")
        self.assertIn("HT20", result)
        print "check 5G 20MHz pass!"

    #信道带宽，5G，40MHz
    def test_044_aps_configure_5g_40MHz(self):
        u"""信道带宽，5G，40MHz(testlinkID:847)"""
        log.debug("044")
        #修改ap信道带宽为40M
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_width': "1"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.htmode")
        self.assertIn("HT40", result)
        print "check 5G 40MHz pass!"

    #信道带宽，5G，80MHz
    def test_045_aps_configure_5g_80MHz(self):
        u"""信道带宽，5G，40MHz(testlinkID:848)"""
        log.debug("045")
        #修改ap信道带宽为40M
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_width': "2"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.htmode")
        self.assertIn("HT80", result)
        print "check 5G 80MHz pass!"

    #2.4G信道，固定信道1
    def test_046_aps_configure_2g4_chn_1(self):
        u"""2.4G信道，固定信道1(testlinkID:852-1)--#Bug 101797"""
        log.debug("046")
        #AP改为2.4G
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "2"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #修改信道为chn1
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_width': "0",
                                          'ap_2g4_channel': "1"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("1", result1)
        self.assertEqual(2412, result2)
        print "check 2.4G channel 1 pass!"

    #2.4G信道，固定信道2
    def test_047_aps_configure_2g4_chn_2(self):
        u"""2.4G信道，固定信道2(testlinkID:852-2)--#Bug 101797"""
        log.debug("047")
        #修改信道为chn2
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "2"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("2", result1)
        self.assertEqual(2417, result2)
        print "check 2.4G channel 2 pass!"

    #2.4G信道，固定信道3
    def test_048_aps_configure_2g4_chn_3(self):
        u"""2.4G信道，固定信道3(testlinkID:852-3)--#Bug 101797"""
        log.debug("048")
        #修改信道为chn3
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "3"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("3", result1)
        self.assertEqual(2422, result2)
        print "check 2.4G channel 3 pass!"

    #2.4G信道，固定信道4
    def test_049_aps_configure_2g4_chn_4(self):
        u"""2.4G信道，固定信道4(testlinkID:852-4)--#Bug 101797"""
        log.debug("049")
        #修改信道为chn4
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "4"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("4", result1)
        self.assertEqual(2427, result2)
        print "check 2.4G channel 4 pass!"

    #2.4G信道，固定信道5
    def test_050_aps_configure_2g4_chn_5(self):
        u"""2.4G信道，固定信道5(testlinkID:852-5)--#Bug 101797"""
        log.debug("050")
        #修改信道为chn5
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "5"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("5", result1)
        self.assertEqual(2432, result2)
        print "check 2.4G channel 5 pass!"

    #2.4G信道，固定信道6
    def test_051_aps_configure_2g4_chn_6(self):
        u"""2.4G信道，固定信道6(testlinkID:852-6)--#Bug 101797"""
        log.debug("051")
        #修改信道为chn6
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "6"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("6", result1)
        self.assertEqual(2437, result2)
        print "check 2.4G channel 6 pass!"

    #2.4G信道，固定信道7
    def test_052_aps_configure_2g4_chn_7(self):
        u"""2.4G信道，固定信道7(testlinkID:852-7)--#Bug 101797"""
        log.debug("052")
        #修改信道为chn7
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "7"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("7", result1)
        self.assertEqual(2442, result2)
        print "check 2.4G channel 7 pass!"

    #2.4G信道，固定信道8
    def test_053_aps_configure_2g4_chn_8(self):
        u"""2.4G信道，固定信道8(testlinkID:852-8)--#Bug 101797"""
        log.debug("053")
        #修改信道为chn8
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "8"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("8", result1)
        self.assertEqual(2447, result2)
        print "check 2.4G channel 8 pass!"

    #2.4G信道，固定信道9
    def test_054_aps_configure_2g4_chn_9(self):
        u"""2.4G信道，固定信道9(testlinkID:852-9)--#Bug 101797"""
        log.debug("054")
        #修改信道为chn9
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "9"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("9", result1)
        self.assertEqual(2452, result2)
        print "check 2.4G channel 9 pass!"

    #2.4G信道，固定信道10
    def test_055_aps_configure_2g4_chn_10(self):
        u"""2.4G信道，固定信道10(testlinkID:852-10)--#Bug 101797"""
        log.debug("055")
        #修改信道为chn10
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "10"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("10", result1)
        self.assertEqual(2457, result2)
        print "check 2.4G channel 10 pass!"

    #2.4G信道，固定信道11
    def test_056_aps_configure_2g4_chn_11(self):
        u"""2.4G信道，固定信道11(testlinkID:852-11)--#Bug 101797"""
        log.debug("056")
        #修改信道为chn11
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_channel': "11"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi0.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("11", result1)
        self.assertEqual(2462, result2)
        print "check 2.4G channel 11 pass!"

    #5G信道，固定信道36
    def test_057_aps_configure_5g_chn_36(self):
        u"""5G信道，固定信道36(testlinkID:853-1)--#Bug 101797"""
        log.debug("057")
        #AP改为5G
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #修改信道为chn36
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_channel': "36"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("36", result1)
        self.assertEqual(5180, result2)
        print "check 5G channel 36 pass!"

    #5G信道，固定信道40
    def test_058_aps_configure_5g_chn_40(self):
        u"""5G信道，固定信道40(testlinkID:853-2)--#Bug 101797"""
        log.debug("058")
        #修改信道为chn40
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_channel': "40"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("40", result1)
        self.assertEqual(5200, result2)
        print "check 5G channel 40 pass!"

    #5G信道，固定信道44
    def test_059_aps_configure_5g_chn_44(self):
        u"""5G信道，固定信道44(testlinkID:853-3)--#Bug 101797"""
        log.debug("059")
        #修改信道为chn44
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_channel': "44"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("44", result1)
        self.assertEqual(5220, result2)
        print "check 5G channel 44 pass!"

    #5G信道，固定信道48
    def test_060_aps_configure_5g_chn_48(self):
        u"""5G信道，固定信道48(testlinkID:853-4)--#Bug 101797"""
        log.debug("060")
        #修改信道为chn48
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_channel': "48"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("48", result1)
        self.assertEqual(5240, result2)
        print "check 5G channel 48 pass!"

    #5G信道，固定信道149
    def test_061_aps_configure_5g_chn_149(self):
        u"""5G信道，固定信道149(testlinkID:853-5)--#Bug 101797"""
        log.debug("061")
        #修改信道为chn149
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_channel': "149"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("149", result1)
        self.assertEqual(5745, result2)
        print "check 5G channel 149 pass!"

    #5G信道，固定信道153
    def test_062_aps_configure_5g_chn_153(self):
        u"""5G信道，固定信道153(testlinkID:853-6)--#Bug 101797"""
        log.debug("062")
        #修改信道为chn153
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_channel': "153"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("153", result1)
        self.assertEqual(5765, result2)
        print "check 5G channel 153 pass!"

    #5G信道，固定信道157
    def test_063_aps_configure_5g_chn_157(self):
        u"""5G信道，固定信道157(testlinkID:853-7)--#Bug 101797"""
        log.debug("063")
        #修改信道为chn157
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_channel': "157"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("157", result1)
        self.assertEqual(5785, result2)
        print "check 5G channel 157 pass!"

    #5G信道，固定信道161
    def test_064_aps_configure_5g_chn_161(self):
        u"""5G信道，固定信道157(testlinkID:853-8)--#Bug 101797"""
        log.debug("064")
        #修改信道为chn161
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_channel': "161"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.wifi1.channel")
        result2 = tmp.connected_AP_Freq(data_wireless['all_ssid'],
                                     data_wireless['short_wpa'],
                                     data_basic['wlan_pc'])
        self.assertIn("161", result1)
        self.assertEqual(5805, result2)
        print "check 5G channel 161 pass!"

    #2.4G激活空间流功能-默认自动
    def test_065_aps_configure_2g4_active_stream(self):
        u"""2.4G激活空间流功能-默认自动(testlinkID:857-1)"""
        log.debug("065")
        #AP改为dual-band
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': ""}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp1.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.2g4_active_streams"%mac)
        self.assertNotIn("='1'", result)
        self.assertNotIn("='2'", result)
        self.assertNotIn("='3'", result)
        print "check 2.4G default active stream pass!"

    #2.4G激活空间流功能-设置为1
    def test_066_aps_configure_2g4_active_stream_1(self):
        u"""2.4G激活空间流功能-设置为1(testlinkID:857-2)"""
        log.debug("066")
        #修改2.4G激活空间流为1
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_active_streams': "1"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.2g4_active_streams"%mac)
        self.assertIn("='1'", result)
        print "check 2.4G active stream is 1 pass!"

    #2.4G激活空间流功能-设置为2
    def test_067_aps_configure_2g4_active_stream_2(self):
        u"""2.4G激活空间流功能-设置为2(testlinkID:857-3)"""
        log.debug("067")
        #修改2.4G激活空间流为2
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_active_streams': "2"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.2g4_active_streams"%mac)
        self.assertIn("='2'", result)
        print "check 2.4G active stream is 2 pass!"

    #2.4G激活空间流功能-设置为3
    def test_068_aps_configure_2g4_active_stream_3(self):
        u"""2.4G激活空间流功能-设置为2(testlinkID:857-4)"""
        log.debug("068")
        #修改2.4G激活空间流为3
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_active_streams': "3"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.2g4_active_streams"%mac)
        self.assertIn("='3'", result)
        print "check 2.4G active stream is 3 pass!"

    #5G激活空间流功能-默认自动
    def test_069_aps_configure_5g_active_stream(self):
        u"""5G激活空间流功能-默认自动(testlinkID:858-1)"""
        log.debug("069")
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        time.sleep(120)
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.5g_active_streams"%mac)
        self.assertNotIn("='1'", result)
        self.assertNotIn("='2'", result)
        self.assertNotIn("='3'", result)
        print "check 5G default active stream pass!"

    #5G激活空间流功能-设置为1
    def test_070_aps_configure_5g_active_stream_1(self):
        u"""5G激活空间流功能-设置为1(testlinkID:858-2)"""
        log.debug("070")
        #修改5G激活空间流为1
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_active_streams': "1"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.5g_active_streams"%mac)
        self.assertIn("='1'", result)
        print "check 5G active stream is 1 pass!"

    #5G激活空间流功能-设置为2
    def test_071_aps_configure_5g_active_stream_2(self):
        u"""5G激活空间流功能-设置为2(testlinkID:858-3)"""
        log.debug("071")
        #修改5G激活空间流为2
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_active_streams': "2"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.5g_active_streams"%mac)
        self.assertIn("='2'", result)
        print "check 5G active stream is 2 pass!"

    #5G激活空间流功能-设置为3
    def test_072_aps_configure_5g_active_stream_3(self):
        u"""5G激活空间流功能-设置为3(testlinkID:858-4)"""
        log.debug("072")
        #修改5G激活空间流为3
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_active_streams': "3"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.5g_active_streams"%mac)
        self.assertIn("='3'", result)
        print "check 5G active stream is 3 pass!"

    #2.4G无线电传送功率-默认为高
    def test_073_aps_configure_2g4_power(self):
        u"""2.4G无线电传送功率-默认为高(testlinkID:859-1)"""
        log.debug("073")
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.2g4_power"%mac)
        self.assertIn("='2'", result)
        print "check 2.4G power default is high pass!"

    #2.4G无线电传送功率-设置低
    def test_074_aps_configure_2g4_power_low(self):
        u"""2.4G无线电传送功率-设置低(testlinkID:859-2)"""
        log.debug("074")
        #修改2.4G无线电传送功率为低
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_power': "0"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.2g4_power"%mac)
        self.assertIn("='0'", result)
        print "check 2.4G power is low pass!"

    #2.4G无线电传送功率-设置中
    def test_075_aps_configure_2g4_power_medium(self):
        u"""2.4G无线电传送功率-设置中(testlinkID:859-3)"""
        log.debug("075")
        #修改2.4G无线电传送功率为低
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_power': "1"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.2g4_power"%mac)
        self.assertIn("='1'", result)
        print "check 2.4G power is medium pass!"

    #5G无线电传送功率-默认为高
    def test_076_aps_configure_5g_power(self):
        u"""2.4G无线电传送功率-默认为高(testlinkID:860-1)"""
        log.debug("076")
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.5g_power"%mac)
        self.assertIn("='2'", result)
        print "check 5G power default is high pass!"

    #5G无线电传送功率-设置低
    def test_077_aps_configure_5g_power_low(self):
        u"""5G无线电传送功率-设置低(testlinkID:860-2)"""
        log.debug("077")
        #修改5G无线电传送功率为低
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_power': "0"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.5g_power"%mac)
        self.assertIn("='0'", result)
        print "check 5G power is low pass!"

    #5G无线电传送功率-设置中
    def test_078_aps_configure_5g_power_medium(self):
        u"""5G无线电传送功率-设置中(testlinkID:860-3)"""
        log.debug("078")
        #修改5G无线电传送功率为低
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_power': "1"})
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        MAC = tmp2.mac_drop(data_ap['7610_mac'])
        mac = MAC.lower()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.%s.5g_power"%mac)
        self.assertIn("='1'", result)
        print "check 5G power is medium pass!"

    #自定义2.4G无线电传送功率功能
    def test_079_aps_configure_2g4_custom_power(self):
        u"""自定义2.4G无线电传送功率功能(testlinkID:862)"""
        log.debug("079")
        #修改2.4G无线电传送功率为自定义10dbm
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_2g4_power': "3",
                                          'ap_custom_2g4_power': "10"})
        time.sleep(240)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath0 | grep Tx-Power")
        self.assertIn("Tx-Power=10 dBm", result)
        print "check 2.4G custom power is 10dbm pass!"

    #自定义5G无线电传送功率功能
    def test_080_aps_configure_5g_custom_power(self):
        u"""自定义5G无线电传送功率功能(testlinkID:863)"""
        log.debug("080")
        #修改5G无线电传送功率为自定义10dbm
        tmp = APSBusiness(self.s)
        tmp.edit_ap(data_ap['7610_mac'], {'ap_5g_power': "3",
                                          'ap_custom_5g_power': "10"})
        time.sleep(240)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result = ssh.ssh_cmd(data_basic['sshUser'], "iwconfig ath1 | grep Tx-Power")
        self.assertIn("Tx-Power=10 dBm", result)
        print "check 5G custom power is 10dbm pass!"

    #删除ap，并恢复cloud的初始环境
    def test_081_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("081")
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
