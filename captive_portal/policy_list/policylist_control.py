#coding=utf-8
#作者：曾祥卫
#时间：2018.07.10
#描述：captive portal--policy list的控制层

import time, subprocess
from data import data
from publicControl.public_control import PublicControl
from captive_portal.splash_page.splashpage_business import SplashPageBusiness

class PolicyListControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #增加一条list,返回这条list的id(int)
    def add_policylist(self, list_name, expiration_time, \
                                           splashpage_name, data_dict={}):
        #首先获取启动页的id
        tmp = SplashPageBusiness(self.s)
        splashpage_id = tmp.get_splashpage_id(splashpage_name)
        #接口的url
        api = self.loadApi()['portalConfigAdd']
        request = PublicControl(self.s)
        #替换数据字典
        pre_dict = {'name': list_name,
                    'splash_page': "0",
                    'expiration': expiration_time,
                    'portal_page_path': "{}".format(splashpage_id)}
        aft_dict = self.replaceConfig(pre_dict, data_dict)
        #发送接口请求
        recvdata = request.apiRequest(api, aft_dict)
        #返回list的id（int）
        list_id = recvdata['data']['value']
        return list_id

    #编辑一条policy list,返回这条list的id(int)
    def edit_policylist(self, list_name, expiration_time, \
                                           splashpage_name, data_dict={}):
        #首先获取启动页的id
        tmp = SplashPageBusiness(self.s)
        splashpage_id = tmp.get_splashpage_id(splashpage_name)
        #获取policy list的id
        policylist_id = self.get_policylist_id(list_name)
        #接口的url
        api = self.loadApi()['portalConfigEdit']
        request = PublicControl(self.s)
        #替换数据字典
        pre_dict = {'name': list_name,
                    'id': policylist_id,
                    'splash_page': "0",
                    'expiration': expiration_time,
                    'portal_page_path': "{}".format(splashpage_id)}
        aft_dict = self.replaceConfig(pre_dict, data_dict)
        #发送接口请求
        recvdata = request.apiRequest(api, aft_dict)
        #返回list的id（int）
        list_id = recvdata['data']['value']
        return list_id

    #根据policy list的名称，获取policy list的id
    def get_policylist_id(self, list_name):
        api = self.loadApi()['portalPolicyList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'pageNum': 1, 'pageSize': 10})
        policylist_lists = recvdata['data']['result']
        for i in range(len(policylist_lists)):
            if list_name == policylist_lists[i]['name']:
                policylist_id = policylist_lists[i]['id']
                print "policylist's id is %d"%policylist_id
                return policylist_id

    #删除policy list
    def delete_policylist(self, list_name):
        #获取listid
        list_id = self.get_policylist_id(list_name)
        api = self.loadApi()['portalPoilcyDelete']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'id': list_id})
        return recvdata
