#!/usr/bin/python
# _*_ coding:utf-8 _*_
__author__ = "dqz"
import string
import random
pwd = ''
all_choise = string.ascii_letters + string.digits

for i in range(8):
   pwd += random.choice(all_choise)

print(pwd)