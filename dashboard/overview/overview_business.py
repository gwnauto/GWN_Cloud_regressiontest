#coding=utf-8
#作者：曾祥卫
#时间：2018.06.14
#描述：cloud监控面板-概览的业务层


from overview_control import OverViewControl
from connect.ssh import SSH
from data import data
import time, subprocess

data_basic = data.data_basic()
data_ap = data.data_AP()

class OverViewBusiness(OverViewControl):

    def __init__(self, s):
        #继承OverViewControl类的属性和方法
        OverViewControl.__init__(self, s)

    #判断bandwidth图表是否有流量
    def check_overview_bandwidth(self, time):
        #获取监控面板-概览-速率，获取上传下载的bandwidth
        r = 0
        t = 0
        rx_bd, tx_bd = self.get_overview_bandwidth(time)
        for rx in rx_bd:
            r = r + rx
        for rx in rx_bd:
            r = r + rx
        print r, t
        if (r+t) > 50000:
            return True
        else:
            return False

    #获取监控面板-概览-Top Aps，第一个ap的信息
    def get_overview_top_aps_count(self, time,menu=0):
        ap_info = OverViewControl.get_overview_top_aps_info(self,time,menu)
        count = len(ap_info)
        return count

        #获取监控面板-概览-Top Aps，第一个ap的信息
    def get_overview_top_aps_mac(self,time,menu=0):
        ap_info = OverViewControl.get_overview_top_aps_info(self,time,menu)
        count = len(ap_info)
        info = []
        for i in range(count):
            info.append(ap_info[i]['mac'])
        return info

     #获取监控面板-概览-Top Aps，输入ap的mac,查找对应的名称
    def get_overview_top_aps_name(self,time,mac,menu=0):
        ap_infos = OverViewControl.get_overview_top_aps_info(self,time,menu)
        # for i in range(len(ap_info)):
        #     if mac == ap_info[i]['mac']:
        #         result = ap_info[i]['name']
        #         return result
        for ap_info in ap_infos:
            if mac==ap_info['mac']:
                result = ap_info['name']
                return result

          #获取监控面板-概览-Top Aps，第一个ap的usage信息
    def get_overview_top_aps_usage(self,time,menu=0):
        ap_info = OverViewControl.get_overview_top_aps_info(self,time,menu)
        count = len(ap_info)
        info = []
        for i in range(count):
            info.append(ap_info[i]['usage'])
        return info

    #判断客户端是否在监控面板-概览-Top Clients中
    def check_overview_top_client(self, time, mac,menu=0):
        #获取监控面板-概览-Top Clients，client的所有信息
        clients_info = OverViewControl.get_overview_top_clients(self,time,menu)
        Mac = mac.upper()
        for client_info in clients_info:
            if client_info['mac'] == Mac:
                return True
        return False

    #客户端对应的usage不为0
    def check_overview_top_client_usage(self,time,menu=0):
        #获取监控面板-概览-Top Clients，client的所有信息
        clients_info = self.get_overview_top_clients(time,menu)
        if clients_info[0]['usage']:
            return True
        else:
            return False

    #获取监控面板-概览-Top SSIDs，输入ssid名称，返回network name
    def get_overview_top_ssids_network(self,time,ssid,menu=0):
        ssid_details = OverViewControl.get_overview_top_ssids_info(self,time,menu)
        # for i in range(len(ssid_detail)):
        #     if ssid == ssid_detail[i]['name']:
        #         result = ssid_detail[i]['network']
        #         return result
        for ssid_detail in ssid_details:
            if ssid == ssid_detail['name']:
                result = ssid_detail['network']
                return result

    #获取监控面板-概览-Top SSIDs，第一个SSID的name
    def get_overview_top_ssids_name(self,time,menu=0):
        #确定time选择的类型
        ssid_detail = OverViewControl.get_overview_top_ssids_info(self,time,menu)
        name=[]
        for i in range(len(ssid_detail)):
            name.append(ssid_detail[i]['name'])
        print(name)
        return name

    #获取监控面板-概览-Top SSIDs，第一个SSID的name
    def get_overview_top_ssids_usage(self, time,menu=0):
        ssid_detail = OverViewControl.get_overview_top_ssids_info(self,time,menu)
        usage=[]
        for i in range(len(ssid_detail)):
            usage.append(ssid_detail[i]['usage'])
        print(usage)
        return usage
