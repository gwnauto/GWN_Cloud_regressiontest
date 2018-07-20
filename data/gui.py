#coding=utf-8
#作者：曾祥卫
#描述：执行测试用例前的准备工作
#时间：2018.3.21

import easygui,sys,time,subprocess, os


#开始欢迎确认框
def welcome():
    msg1="请先把路由,AP和PC按以下拓扑图连接好"
    msg2='请确定data.xlsx的数据是否正确'
    msg3='即将要开始GWN Cloud的自动化测试\n\n'\
         '1.请先修改路由的dns，将www.gwn.cloud指向本地服务器。\n\n'\
         '2.请先使用Cloud的admin帐号新建一个任意权限的帐号并激活。\n\n'\
         '3.portal启动页中新建的启动页，开启免费，密码，帐号，凭据，微信认证。\n\n'\
         '4.请先将AP恢复出厂设置，或者配置AP的admin用户的密码为data.xlsx中指定的密码。\n\n'
    title = '欢迎进行GWN Cloud的自动化测试'
    choice=["正确并继续","点击该按钮先去设置"]
    #欢迎页面拓扑图
    dirname = os.path.dirname(__file__)
    PATH_map = os.path.join(dirname, "topological_map.gif")
    image=PATH_map
    easygui.msgbox(msg3,title)
    easygui.msgbox(msg1,title,image=image)
    #欢迎页面确定data.xlsx数据正确
    welcome = easygui.ccbox(msg2,title,choices=choice)
    #点击"先去设置"，打开data.xlsx
    if welcome == 0:
        PATH_dataxlsx = os.path.join(dirname, "data.xlsx")
        subprocess.call("xdg-open %s"%PATH_dataxlsx,shell=True)
        print "退出自动化测试"
        sys.exit(0)

#选择测试用例框
def choice_case():
    case = []
    msg="请先选择需要执行的测试用例集"
    title="选择用例集"
    choices=[
             'A_ap_monitor',
             'B_ap_configure',
             'C_ssids',
             'D_clients',
             'E_access_list',
             'F_settings',
             'G_networklist',
             'H_upgrade',
             'I_user',
             'J_dashboard',
             'K_captiveportal',
            ]
    while True:
        #测试用例选择框
        case=easygui.multchoicebox(msg,title,choices)
        #点击取消退出测试
        if case == None :
            print "退出自动化测试"
            sys.exit(0)
        #不选择任何一个用例，提示
        elif len(case) ==0:
            easygui.msgbox("你没有选择任何一个测试用例集，请必须选择一个！","错误")
            continue
        else:
            msg1 = ""
            for i in range(len(case)):
                msg1 += ('%s\n'%case[i])
            #显示所选择的测试用例，并再次确认
            confirm_again=easygui.ccbox(msg=msg1,title="请确认所需测试集的用例是否正确：",\
                                        choices=("正确并继续","再去选择"))
            #点击再去选择，重新选择用例
            if confirm_again == 0:
                continue
            break
    return case




#输入发送测试报告的email地址和密码
def send_email():
    send_email = []
    msg='请输入你的eamil地址和密码'
    title="你的email"
    field = ["*email地址", "*密码"]
    while True:
        #输入用户名和密码框，密码为不显示明文
        send_email=easygui.multpasswordbox(msg, title,field)
        #点击取消退出测试
        if send_email == None :
            print "退出自动化测试"
            sys.exit(0)
        #地址和密码都不输入，提示
        elif send_email == ["",""]:
            easygui.msgbox("你必须输入email地址和密码！","错误")
            continue
        #地址为空，提示
        elif send_email[0].strip()=="":
            easygui.msgbox("你必须输入email地址！","错误")
            continue
        #密码为空，提示
        elif send_email[1].strip()=="":
            easygui.msgbox("你必须输入密码！","错误")
        else:
            break
    return send_email


#输入接收测试报告的email地址
def receive_email():
    receive_email = []
    msg="至少必须输入一个emai地址，多个email地址用逗号隔开"
    title="接收测试报告的email地址"
    fields=["email地址1","email地址2","email地址3","email地址4","email地址5","email地址6","email地址7","email地址8"]
    values = ["sz_gwntest@grandstream.cn",
              "wliu@grandstream.cn",
              "xwzeng@grandstream.cn",
              "tjiang@grandstream.cn"]
    values_self = ["xwzeng@grandstream.cn"]
    while True:
        #email地址输入框
        receive_email=easygui.multenterbox(msg,title,fields,values)
        #点击取消退出测试
        if receive_email == None:
            print "退出自动化测试"
            sys.exit(0)
        msg1 =""
        for i in range(len(fields)):
            msg1 +=(receive_email[i])
        #一个地址都不输入，提示
        if msg1 == '':
            easygui.msgbox("请至少必须输入一个emai地址！","错误")
            continue
        else:
            break
    return receive_email

#设置用例执行的次数
def loop_times():
    loop = easygui.ccbox('是否需要循环多次执行？','循环执行测试',choices=['否','是'])
    if loop == 0:
        times = easygui.enterbox(msg='格式如：5',title='请输入循环执行的次数')
        print "Run loop times is %s"%times
        return times
    return loop

#设置自动化执行人
def test_executor():
    while True:
        test_executor = easygui.enterbox(msg='中文英文皆可',title='请输入自动化执行人姓名')
        if (test_executor == "") or (test_executor == None):
            easygui.msgbox('必须要输入自动化执行人姓名才能继续开始测试','请输入自动化执行人姓名')
            continue
        else:
            return test_executor


#设置开始时间
def start_time():
    YN = easygui.ccbox('是否立刻开始测试？','开始测试',choices=['是','设置开始时间'])
    if YN == 0:
        start_time = easygui.enterbox(msg='格式如：18:30',title='请输入自动化测试开始的时间')
        timing=time.strftime('%H:%M',time.localtime(time.time()))
        print u"目前时间是：%s\n开始测试时间是：%s"%(timing,start_time)
        #是否需要从Internet上下载固件后，然后再进行测试
        #########控制什么时间脚本执行######
        while True:
            timing=time.strftime('%H:%M',time.localtime(time.time()))
            if timing != start_time:
                time.sleep(30)
                print u"目前时间是：%s，请等待..."%timing
            else:
                print u"开始执行自动化测试！"
                break

#设置每个用例集是否需要逐个测试并发送邮件
#输出：1：不需要;0：需要
def testcase_onebyone():
    msg='是否需要逐个测试并生成单独的测试报告'
    title='请确定每个用例集是否需要逐个测试并生成单独的测试报告'
    choice=["不需要","需要"]
    onebyone = easygui.ccbox(msg,title,choices=choice)
    return onebyone