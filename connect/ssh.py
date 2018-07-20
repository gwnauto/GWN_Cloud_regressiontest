#coding=utf-8
#作者：曾祥卫
#时间：2017.03.09
#描述：GWN76xx进行ssh登录

import pexpect,subprocess,codecs
import datetime,time, os


class SSH:

    #自己SSH类的属性:host-远程登录主机名，pwd-密码
    def __init__(self,host,pwd):
        self.host = host
        self.pwd = pwd

    #描述:首先使用 dbclient host -l user -i dropbear_rsa_client_key cmd登录ssh,在确定是否是首次登录，再输出结果
    #输入：user-登录用户名,cmd-命令
    #输出:命令返回的结果，同时将结果存放在同目录的log.txt文件中
    def ssh_cmd(self,user,cmd):
        try:
            #远程主机输入后出现的字符串
            ssh_newkey = "(?i)Do you want to continue connecting? (y/n)"
            # 为 ssh 命令生成一个 spawn 类的子程序对象.
            dirname = os.path.dirname(__file__)
            PATH = os.path.join(dirname, "dropbear_rsa_client_key")
            child = pexpect.spawn('dbclient %s -l %s -i %s %s' \
                                  %(self.host, user, PATH, cmd), timeout=8)
            i = child.expect(['password: ',pexpect.TIMEOUT,pexpect.EOF, ssh_newkey])
            # 如果登录超时，打印出错信息，并退出.
            # if i == 0:
            #     print u"1错误，ssh 登录超时:"
            #     print child.before, child.after
            #     return None
            # 如果 登录超时或ssh 没有 public key，接受它.
            # 这里有问题：第一次登录ssh时是超时，但实际上是能响应的，这里先这样处理，后面再研究
            if i != 0:
                child.sendline('y')
                child.expect(['password: ',pexpect.TIMEOUT,pexpect.EOF])
                # if i != 0:
                #     print u"2错误，ssh 登录超时:"
                #     print child.before, child.after
                #     return None
            # 输入密码.
            child.sendline(self.pwd)

            # 列出输入密码后期望出现的字符串，'password',EOF，超时
            i = child.expect(['password: ', pexpect.EOF, pexpect.TIMEOUT])
            # 匹配到字符'password: '，打印密码错误
            if i == 0:
                print u'密码输入错误！'
            # 匹配到了EOF，打印ssh登录成功，并输入命令后成功退出
            elif i == 1:
                print u'恭喜,ssh登录输入%s命令成功！' %cmd
            # 匹配到了超时，打印超时
            else:
                print u'输入命令后等待超时！'

            # 将执行命令的时间和结果以追加的形式保存到log.txt文件中备份文件
            dirname1 = os.path.dirname(os.path.dirname(__file__))
            PATH_data = os.path.join(dirname1, "data")
            PATH_ssh_log = os.path.join(PATH_data, "testresultdata", "ssh_log.txt")
            f = codecs.open(PATH_ssh_log, 'a',encoding='utf-8')
            str1 = str(datetime.datetime.now()) + ' command:' + cmd
            f.writelines(str1 + child.before)
            f.close()

            result = child.before
            print result
            return result
        except pexpect.ExceptionPexpect, e:
            print u"ssh连接失败，正在重启进程"
            result2 = subprocess.call("rm -rf ~/.ssh",shell=True)
            print result2

            time.sleep(10)
            print "delete ssh"
            print e


    def ssh_cmd_noKey(self,user,cmd):
        try:
            ssh_newkey = "Are you sure you want to continue connecting(yes/no)?"
            # 为 ssh 命令生成一个 spawn 类的子程序对象.
            child = pexpect.spawn('ssh -l %s %s %s'%(user, self.host, cmd))
            i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
            # 如果登录超时，打印出错信息，并退出.
            if i == 0:
                print u"错误，ssh 登录超时:"
                print child.before, child.after
                return None
            # 如果 ssh 没有 public key，接受它.
            if i == 1: # ssh does not have the public key. Just accept it.
                child.sendline ('yes')
                i = child.expect([pexpect.TIMEOUT, 'password: '])
                if i == 0:
                    print u"错误，ssh 登录超时:"
                    print child.before, child.after
                    return None
            # 输入密码.
            child.sendline(self.pwd)

            #列出输入密码后期望出现的字符串，'password',EOF，超时
            i = child.expect(['password: ',pexpect.EOF,pexpect.TIMEOUT])
            #匹配到字符'password: '，打印密码错误
            if i == 0:
                print u'密码输入错误！'
            #匹配到了EOF，打印ssh登录成功，并输入命令后成功退出
            elif i == 1:
                print u'恭喜,ssh登录输入%s命令成功！'%cmd
            #匹配到了超时，打印超时
            else:
                print u'输入命令后等待超时！'

            #将执行命令的时间和结果以追加的形式保存到log.txt文件中备份文件
            dirname1 = os.path.dirname(os.path.dirname(__file__))
            PATH_data = os.path.join(dirname1, "data")
            PATH_ssh_log = os.path.join(PATH_data, "testresultdata", "ssh_log.txt")
            f = open(PATH_ssh_log,'a')
            str1 = str(datetime.datetime.now())+' command:'+cmd
            f.writelines(str1+child.before)
            f.close()

            result = child.before
            print result
            return result
        except pexpect.ExceptionPexpect, e:
            print u"ssh连接失败，正在重启进程"
            result2 = subprocess.call("rm -rf ~/.ssh",shell=True)
            print result2

            time.sleep(10)
            print "delete ssh"
            print e