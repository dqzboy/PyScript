#!/usr/bin/python
# _*_ coding:utf-8 _*_
__author__ = "dqz"
#引用函数getpass 实现密码输入的隐藏
import getpass
name = input("输入用户名：")
password = input("输入密码：")
no = 0
while True:
    if name == 'tom' and password =='123':
        print("登入成功")
        break
    else:
        no += 1
        print("登入失败%s次" %no)
    name = input("用户输入错误，重新输入：")
    password = input("密码输入错误，重新输入：")

    if no == 2:
        print("登入失败")
        break