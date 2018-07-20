#coding=utf-8
#作者：曾祥卫
#时间：2018.03.19
#描述：cloud SSIDs的业务层


from ssids_control import SSIDSControl
from connect.ssh import SSH
from data import data
import time

data_basic = data.data_basic()

class SSIDSBusiness(SSIDSControl):

    def __init__(self, s):
        #继承SSIDSControl类的属性和方法
        SSIDSControl.__init__(self, s)

    #检查客户端隔离的结果
    def check_isolation(self):
        self.dhcp_wlan(data_basic['wlan_pc'])
        #禁用有线网卡
        self.wlan_disable(data_basic['lan_pc'])
        #无线ping网关
        result1 = self.get_ping(data_basic['7000_ip'])
        #无线ping wan
        result2 = self.get_ping("180.76.76.76")
        #释放无线网卡ip
        self.dhcp_release_wlan(data_basic['wlan_pc'])
        #启用有线网卡
        self.wlan_enable(data_basic['lan_pc'])
        return result1, result2

    #在2分钟内每隔0.5秒检查无线网卡是否一直保持和ap连接
    def check_wifi_client_connected_allthetime(self,wlan):
        result = []
        i = 0
        while (i<120):
            status = self.get_client_cmd_result("iw %s link"%wlan)
            result.append(status)
            time.sleep(0.5)
            i = i+0.5
        print "result = %s"%result
        return result

    #获取2小时，一天，一周，一个月的客户端图，并检查有无变化
    def check_ssids_summary_distribution_client_count(self):
        tmp = SSIDSBusiness(self.s)
        #获取2小时的客户端数图
        result_2h = tmp.get_ssids_summary_distribution_client_count("2h")
        #获取1天的客户端数图
        result_1d = tmp.get_ssids_summary_distribution_client_count("1d")
        #获取1周的客户端数图
        result_1w = tmp.get_ssids_summary_distribution_client_count("1w")
        #获取1月的客户端数图
        result_1m = tmp.get_ssids_summary_distribution_client_count("1m")
        if result_2h == result_1d == result_1w == result_1m :
            return False
        else:
            return True

    #获取2小时，一天，一周，一个月的速率图，并检查有无变化
    def check_ssids_summary_distribution_bandwidth(self):
        tmp = SSIDSBusiness(self.s)
        #获取2小时的速率图
        result_2h = tmp.get_ssids_summary_distribution_bandwidth("2h")
        #获取1天的速率图
        result_1d = tmp.get_ssids_summary_distribution_bandwidth("1d")
        #获取1周的速率图
        result_1w = tmp.get_ssids_summary_distribution_bandwidth("1w")
        #获取1个月的速率图
        result_1m = tmp.get_ssids_summary_distribution_bandwidth("1m")
        if result_2h == result_1d == result_1w == result_1m :
            return False
        else:
            return True