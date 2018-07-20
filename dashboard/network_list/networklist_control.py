#coding=utf-8
#作者：曾祥卫
#时间：2018.06.08
#描述：cloud监控面板-网络列表的控制层


import time
from data import data
from publicControl.public_control import PublicControl




class NetworkListControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    ######################################################################
    #获取网络组对应的id--监控面板--网络列表
    def get_network_id(self, network_name):
        api = self.loadApi()['networkList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'pageNum':1,
                                            'pageSize':10})
        network_lists = recvdata['data']['result']
        for i in range(len(network_lists)):
            if network_name == network_lists[i]['name']:
                network_id = network_lists[i]['id']
                print "network's id is %d"%network_id
                return network_id

    #添加网络组
    def add_network(self, network_name, user_id, cloneNetwork_id):
        api = self.loadApi()['networkAdd']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,
                    {'cloneNetwork':cloneNetwork_id,
                     'country':"US",
                     'id':"",
                     'networkAdministrator':[user_id],
                     'networkName':network_name,
                     'timezone':"Etc/GMT"})
        return recvdata

    #删除网络组
    def delete_network(self, network_name):
        id = self.get_network_id(network_name)
        api = self.loadApi()['networkDelete']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,
                    {'id':id})
        return recvdata

    #选择进入哪个网络组
    def goin_network(self, network_name):
        id = self.get_network_id(network_name)
        api = self.loadApi()['networkChoose']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api+str(id))
        return recvdata

    #获取网络组对应的id--监控面板--网络列表
    def get_network_info(self):
        api = self.loadApi()['networkList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'pageNum':1,
                                            'pageSize':10})
        network_info = recvdata['data']['result']
        return network_info

    #根据网络组的id，获取对应的信息
    def get_networkitem_info(self,id):
        api = self.loadApi()['networkItem']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {"id":id})
        networkitem_info = recvdata['data']
        return networkitem_info



