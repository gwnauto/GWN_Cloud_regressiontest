#coding=utf-8
#作者：曾祥卫
#时间：2018.07.13
#描述：captive portal--vouchers的控制层

import time, subprocess, random
from data import data
from publicControl.public_control import PublicControl



class VouchersControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #新增凭据组--默认20个密码
    def add_vouchers_list(self, voucher_name, data_dict={}):
        #接口的url
        api = self.loadApi()['portalVoucherSave']
        request = PublicControl(self.s)
        #替换数据字典
        pre_dict = {'name': voucher_name,
                    'vocherNum': 20,
                    'deviceNum': 1,
                    'expiration': 90,
                    'effectDurationMap':{'d': 0, 'h': 0, 'm': "2"}}
        aft_dict = self.replaceConfig(pre_dict, data_dict)
        #发送接口请求
        recvdata = request.apiRequest(api, aft_dict)
        return recvdata

    #根据凭据组的名称，获取凭据组的id
    def get_vouchers_list_id(self, list_name):
        api = self.loadApi()['portalVoucherList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'pageNum': 1, 'pageSize': 10})
        vouchers_lists = recvdata['data']['result']
        for i in range(len(vouchers_lists)):
            if list_name == vouchers_lists[i]['name']:
                voucherslist_id = vouchers_lists[i]['id']
                print "voucherslist's id is %d"%voucherslist_id
                return voucherslist_id

    #根据凭据组的名称，获取未使用的密码
    def get_vouchers_not_used_password(self, list_name):
        api = self.loadApi()['portalVoucherPasswordList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'name': list_name,
                                           'filter': {'state': "0"},
                                           'pageNum': 1,
                                           'pageSize': 10})
        password_lists = recvdata['data']['result']
        password_list = random.choice(password_lists)
        Voucher_password = password_list['password']
        print("Voucher_password is %s"%Voucher_password)
        return Voucher_password

    #根据凭据组的名称，删除凭据组
    def delete_vouchers_list(self, list_name):
        api = self.loadApi()['portalVoucherDelete']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'name': list_name})
        return recvdata