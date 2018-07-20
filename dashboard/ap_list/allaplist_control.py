#coding=utf-8
#作者：曾祥卫
#时间：2018.06.11
#描述：cloud监控面板-ap列表的控制层


import time
from data import data
from publicControl.public_control import PublicControl




class AllApListControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    ######################################################################
    #获取ap列表ap的具体信息
    def get_ap_info(self, ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['allApList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'filter': {'deviceType': "all"},
                                            'pageNum':1,
                                            'pageSize':10})
        ap_lists = recvdata['data']['result']
        for i in range(len(ap_lists)):
            if AP_MAC == ap_lists[i]['mac']:
                return ap_lists[i]



