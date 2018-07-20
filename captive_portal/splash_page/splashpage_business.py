#coding=utf-8
#作者：曾祥卫
#时间：2018.07.10
#描述：captive portal--splash page的业务逻辑层
from splashpage_control import SplashPageControl


class SplashPageBusiness(SplashPageControl):

    def __init__(self, s):
        #继承SplashPageControl类的属性和方法
        SplashPageControl.__init__(self, s)


