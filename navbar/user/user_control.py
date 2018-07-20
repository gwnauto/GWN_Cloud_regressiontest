#coding=utf-8
#作者：曾祥卫
#时间：2018.06.08
#描述：cloud导航-用户的控制层


import time
from data import data
from publicControl.public_control import PublicControl




class UserControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    ######################################################################
    #获取登录名对应的id
    def get_network_id(self, user_name):
        api = self.loadApi()['usersList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api)
        user_lists = recvdata['data']['result']
        for i in range(len(user_lists)):
            if user_name == user_lists[i]['name']:
                user_id = user_lists[i]['id']
                print "user's id is %d"%user_id
                return user_id

    #修改用户权限
    #networkids:为网路组id的列表，元素都为int
    def set_user_authority(self, user_name, email, privilege, networkids):
        user_id = self.get_network_id(user_name)
        if privilege == "Network Administrator":
            roleId = 2
        elif privilege == "Platform Administrator":
            roleId = 5
        elif privilege == "Guest Editor":
            roleId = 3
        api = self.loadApi()['userSave']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'email': email,
                                            'roleId': roleId,
                                            'networkIds': networkids,
                                            'id': user_id})
        return recvdata




