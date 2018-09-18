#!/usr/bin/python
# _*_ coding:utf-8 _*_
__author__ = "dqz"
x = ""
cd = """1、矿泉水
2、可口可乐
"""
while not x:
    print("请选择以下菜单内容：")
    x = input(cd)
    if x == "1":
        print("矿泉水：3.5元")
    elif x == "2":
        print("可口可乐：5元")
