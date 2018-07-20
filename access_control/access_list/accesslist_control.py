#coding=utf-8
#作者：曾祥卫
#时间：2018.05.22
#描述：cloud 接入控制-接入列表的控制层


import time
from data import data
from publicControl.public_control import PublicControl




class AccessListControl(PublicControl):

    def __init__(self,s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #获取Global Blacklist中的mac地址
    def get_Global_Blacklist_mac(self):
        api = self.loadApi()['accessListInfo']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'name': "Global Blacklist"})
        Global_Blacklist = recvdata['data']['macs']
        print "Global Blacklist = %s"%Global_Blacklist
        return Global_Blacklist

    #把Global Blacklist中的mac地址清空
    def set_Global_Blacklist_blank(self):
        api = self.loadApi()['accessListEdit']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'name': "Global Blacklist",
                                            'macs': []})
        return recvdata

    #获取Global Blacklist中的mac地址的统计数量
    def get_Global_Blacklist_macCount(self):
        api = self.loadApi()['accessList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'type': "",
                                            'order': "",
                                            'pageNum': 1,
                                            'pageSize': 10})

        lists = recvdata['data']['result']
        for i in range(len(lists)):
            if lists[i]['name'] == "Global Blacklist":
                macCount = lists[i]['macCount']
                print "Global Blacklist mac Count = %s"%macCount
                return macCount


    #Global Blacklist中添加mac地址
    #输入：macs：为一个mac list
    def edit_Global_Blacklist_mac(self, macs):
        api = self.loadApi()['accessListEdit']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'name': "Global Blacklist",
                                            'macs': macs})
        return recvdata

    #接入控制-接入列表页面中,获取对应list的信息
    #输入：name：list的名称
    #输出：返回的是一个dict
    def get_list_info(self, name):
        api = self.loadApi()['accessList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'type': "",
                                            'order': "",
                                            'pageNum': 1,
                                            'pageSize': 10})

        lists = recvdata['data']['result']
        for i in range(len(lists)):
            if lists[i]['name'] == name:
                return lists[i]

    #接入控制-接入列表页面中,新增列表
    #输入：macs：为一个mac list
    def add_list(self, name, macs):
        api = self.loadApi()['accessListSave']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'name': name,
                                            'macs': macs})
        return recvdata

    #接入控制-接入列表页面中,编辑列表
    #输入：macs：为一个mac list
    def edit_list(self, name, macs):
        api = self.loadApi()['accessListEdit']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'name': name,
                                            'macs': macs})
        return recvdata

    ##接入控制-接入列表页面中,删除列表
    def delete_list(self, name):
        api = self.loadApi()['accessListDelete']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'name': name})
        return recvdata