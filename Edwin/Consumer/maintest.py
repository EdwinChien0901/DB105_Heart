import mysqltest
import pandas_main

#l = ['雙北']
#t = ['戶外玩樂', '自然', '朋友']

def do_compare(locationlist, taglist):
    k1 = locationlist
    k2 = taglist
    mysqltest.sqlcon(k1)
    return pandas_main.pandascon(k2)

#do_compare(l, t)


if __name__ == "__main__":
    k1 = ['雙北']
    k2 = ['自然風格','家人','雨天備案']
    rlist = do_compare(k1,k2)
    print("rlist:", rlist)
