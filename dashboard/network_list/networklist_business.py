#coding=utf-8
#作者：曾祥卫
#时间：2018.06.08
#描述：cloud监控面板-网络列表的业务层


from networklist_control import NetworkListControl
from connect.ssh import SSH
from data import data
import time, subprocess

data_basic = data.data_basic()
data_ap = data.data_AP()

class NetworkListBusiness(NetworkListControl):

    def __init__(self, s):
        #继承NetworkListControl类的属性和方法
        NetworkListControl.__init__(self, s)

    #network的个数
    def get_network_count(self):
        network_info = NetworkListControl.get_network_info(self)
        count = len(network_info)
        return count

    #network的名称
    def get_network_name(self):
        network_info = NetworkListControl.get_network_info(self)
        network_name =[]
        for i in range(len(network_info)):
            network_name.append(network_info[i]['name'])
        return network_name

     #每个network中ap的离线百分比
    def get_network_offiline(self):
        network_info = NetworkListControl.get_network_info(self)
        network_offiline = []
        for i in range(len(network_info)):
            offline = (network_info[i]['devices']-network_info[i]['onlineDevices'])\
            /network_info[i]['devices']
            network_offiline.append(offline)
        return network_offiline


    #每个network中ap的总数
    def get_network_ap_total(self):
        network_info = NetworkListControl.get_network_info(self)
        ap_total = []
        for i in range(len(network_info)):
            ap_total.append(network_info[i]['devices'])
        return ap_total

    #每个network中客户端数量
    def get_network_client(self):
        network_info = NetworkListControl.get_network_info(self)
        network_client = []
        for i in range(len(network_info)):
            network_client.append(network_info[i]['clients'])
        return network_client

     #根据网络组的id,获取network的country和timezone
    def get_networkitem_country_timezone(self,id):
        networkitem_info = NetworkListControl.get_networkitem_info(self,id)
        networkitem_country = networkitem_info['country']
        networkitem_timezone = networkitem_info['timezone']
        return networkitem_country,networkitem_timezone

    #获取该网络组的网络管理员
    def get_networkitem_all_user(self,id):
        networkitem_info = NetworkListControl.get_networkitem_info(self,id)
        networkitem_users = networkitem_info['selectUsers']
        user=[]
        count = len(networkitem_users)
        for i in range(count):
            user.append(networkitem_users[i]['username'])
        return count,user
