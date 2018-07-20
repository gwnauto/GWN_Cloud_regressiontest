#coding=utf-8
#作者：曾祥卫
#时间：2018.05.03
#描述：cloud client的控制层


import time
from data import data
from publicControl.public_control import PublicControl




class Clients_Control(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #获取客户端-概要-客户端数量，最近5分钟的客户端数
    def get_current_5mins_clients_count(self, time):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['chartClientsCount']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': 2,
                                            'type': type,
                                            'ssidId': "all_ssid"})
        clientcounts = recvdata['data']['clientCounts'][-1]
        print "clients count = %s"%clientcounts
        return clientcounts

    #获取客户端-概要-客户端数量，某个ssid的最近5分钟的客户端数
    def get_one_ssid_current_5mins_clients_count(self, time, ssidid):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['chartClientsCount']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': 2,
                                            'type': type,
                                            'ssidId': "%s"%ssidid})
        clientcounts = recvdata['data']['clientCounts'][-1]
        print "clients count = %s"%clientcounts
        return clientcounts

    #客户端-概要-速度图，获取上传下载的速率
    def get_chart_ap_bandwidth(self, time):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['chartBandUsage']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'type': type,
                                            'ssidId': "all_ssid",
                                            'menu': 2})
        rx_bd = recvdata['data']['rxBandwidth']
        tx_bd = recvdata['data']['txBandwidth']
        return rx_bd, tx_bd

    #客户端-状态，获取第一个客户端的信息
    def get_first_client_info(self):
        api = self.loadApi()['clientsList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'pageNum': 1,
                                            'pageSize': 10,
                                            'filter': {'ssidId': "all_ssid"}})
        client_info = recvdata['data']['result'][0]
        print "client_info = %s"%client_info
        return client_info

    #客户端-状态，获取客户端的总数
    def get_client_total(self):
        api = self.loadApi()['clientsList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'pageNum': 1,
                                            'pageSize': 10,
                                            'filter': {'ssidId': "all_ssid"}})
        client_total = recvdata['data']['total']
        print "client_total = %s"%client_total
        return client_total

    #客户端-状态，点击block
    def set_client_block(self,client_mac):
        Client_MAC = client_mac.upper()
        api = self.loadApi()['clientsBlock']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'clientId': Client_MAC,
                                             'block': 0})
        return recvdata