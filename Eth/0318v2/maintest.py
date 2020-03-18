import mysqltest
import pandas_main

l = ['雙北']
t = ['戶外玩樂', '自然', '朋友']

def do_compare(locationlist, taglist):
    k1 = locationlist
    k2 = taglist
    mysqltest.sqlcon(k1)
    pandas_main.pandascon(k2)

do_compare(l, t)