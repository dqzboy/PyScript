#!/usr/bin/python
# _*_ coding:utf-8 _*_
__author__ = "dqz"
file = input("请输入要统计的文件路径：")
def filezs(s):
    chare = len(s)  #统计有多少个字符
    words = len(s.split())  #以空格做分隔，统计单词数
    lines = s.count('\n')   #/n表示回车，统计出多少行
    print(lines,words,chare)
if __name__ == '__main__':
    s = open(file).read()   #open打开文件，read读取文件

filezs(s)
