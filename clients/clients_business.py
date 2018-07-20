#coding=utf-8
#作者：曾祥卫
#时间：2018.05.03
#描述：cloud client的业务层


from clients_control import Clients_Control
from connect.ssh import SSH
from data import data
import time, subprocess

data_basic = data.data_basic()
data_ap = data.data_AP()

class Clients_Business(Clients_Control):

    def __init__(self, s):
        #继承Clients_Control类的属性和方法
        Clients_Control.__init__(self, s)

    #使用无线网卡ping internet 1分钟
    def set_wlan_ping_internet_1min(self, lan):
        #禁用有线网卡
        self.wlan_disable(lan)
        #ping internet 1分钟
        subprocess.call("ping 180.76.76.76 -c 60",shell=True)
        #启用有线网卡
        self.wlan_enable(lan)


    #判断bandwidth图表是否有流量
    def check_chart_ssid_bandwidth(self, time):
        #客户端-概要-速度图，获取上传下载的速率
        r = 0
        t = 0
        rx_bd, tx_bd = self.get_chart_ap_bandwidth(time)
        for rx in rx_bd:
            r = r + rx
        for rx in rx_bd:
            r = r + rx
        print r, t
        if (r+t) > 1000:
            return True
        else:
            return False