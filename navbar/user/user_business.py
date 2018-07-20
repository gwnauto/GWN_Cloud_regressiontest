#coding=utf-8
#作者：曾祥卫
#时间：2018.06.08
#描述：cloud导航-用户的业务层


from user_control import UserControl
from connect.ssh import SSH
from data import data
import time, subprocess

data_basic = data.data_basic()
data_ap = data.data_AP()

class UserBusiness(UserControl):

    def __init__(self, s):
        #继承UserControl类的属性和方法
        UserControl.__init__(self, s)

