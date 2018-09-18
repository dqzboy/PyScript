#!/usr/bin/python
# _*_ coding:utf-8 _*_
__author__ = "dqz"
#让用户输入的备份的路径和存放的路径
yuan = input("请输入备份的路径：")
mubiao = input("请输入目标路径：")

#定义个函数
def bf(x,y):
    s = open(yuan,'r')
    d = open(mubiao,'w')
    for i in s:
        d.write(i)
    d.flush()
    s.close()
    d.close()

#调用函数
bf(x=yuan,y=mubiao)
