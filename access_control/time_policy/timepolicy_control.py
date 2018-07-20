#coding=utf-8
#作者：曾祥卫
#时间：2018.05.31
#描述：cloud 接入控制-时间策略的控制层


import time
from data import data
from publicControl.public_control import PublicControl




class TimePolicyControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)


    #新增添加 time policy
    #输入：name：策略名;data_dict:规则dict,信息如下:
                    # {'status': 1,
                    # 'reconnectType': 1,
                    #  'resetDay': 1,
                    #  'resetHour': "23",
                    #  'hour': "24",
                    #  'resetTimeType': "AM",
                    #  'timezone': "Etc/GMT",
                    #  'connectionTimeMap': {'d': "0", 'h': "0", 'm': "2"},
                    #  'connectionTimeoutMap': {'d': "", 'h': "", 'm': ""}
                    #  }
    def add_timepolicy(self, name, data_dict):
        #配置替换
        dict1 = self.replaceConfig({'name': name}, data_dict)
        api = self.loadApi()['timePolicySave']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, dict1)
        time.sleep(5)
        return recvdata

    #编辑time policy
    def edit_timepolicy(self, name, data_dict):
        timepolicy_id = self.get_timepolicy_id(name)
        #配置替换
        dict1 = self.replaceConfig({'id': timepolicy_id,'name': name}, data_dict)
        api = self.loadApi()['timePolicySave']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, dict1)
        time.sleep(5)
        return recvdata

    #获取时间策略的id
    def get_timepolicy_id(self, name):
        api = self.loadApi()['timePolicyList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'pageNum': 1, 'pageSize': 10})
        timepolicy_lists = recvdata['data']['result']
        for i in range(len(timepolicy_lists)):
            if name == timepolicy_lists[i]['name']:
                timepolicy_id = timepolicy_lists[i]['id']
                print "timepolicy's id is %d"%timepolicy_id
                return timepolicy_id

    #获取被禁客户端id
    def get_restrict_id(self, mac):
        Mac = mac.upper()
        api = self.loadApi()['clientsBandList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'pageNum': 1, 'pageSize': 10})
        restrict_lists = recvdata['data']['result']
        for i in range(len(restrict_lists)):
            if Mac == restrict_lists[i]['clientId']:
                restrict_id = restrict_lists[i]['id']
                print "restrict's id is %d"%restrict_id
                return restrict_id

    #释放被禁的客户端
    def release_restrict_mac(self, mac):
        restrict_id = self.get_restrict_id(mac)
        api = self.loadApi()['clientsBandRelease']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'id': restrict_id})
        time.sleep(5)
        return recvdata



