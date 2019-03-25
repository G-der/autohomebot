import re
import time
from datetime import datetime


def time_change():
    print(time.strftime("%Y/%m/%d", time.localtime(time.time())))
    pushtime_str = ' 发表于：2019/2/12 11:15:00   '

    pushtime = pushtime_str.replace(' 发表于：', '')
    if re.search("昨天", pushtime):
        yestoday = time.strftime("%Y/%m/%d", time.localtime(time.time() - 86400))
        pushtime = pushtime.replace('昨天', yestoday)
    if re.search('前天', pushtime):
        Byestoday = time.strftime("%Y/%m/%d", time.localtime(time.time() - 172800))
        pushtime = pushtime.replace('前天', Byestoday)
    if re.search('今天', pushtime):
        Byestoday = time.strftime("%Y/%m/%d", time.localtime(time.time()))
        pushtime = pushtime.replace('今天', Byestoday)
    if re.search('小时前', pushtime):
        NUM = int(re.search('\d+', pushtime).group())
        sec = NUM * 60 * 60
        today = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time() - sec))
        pushtime = pushtime.replace("{} 小时前".format(NUM), today)
    if re.search('分钟前', pushtime):
        NUM = int(re.search('\d+', pushtime).group())
        sec = NUM * 60
        today = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time() - sec))
        pushtime = pushtime.replace("{} 分钟前".format(NUM), today)
    print(pushtime)


# 把datetime转成字符串
def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d")  # "%Y-%m-%d-%H"


# 把字符串转成datetime
def string_toDatetime(string):
    return datetime.strptime(string, "%Y-%m-%d")


# 把字符串转成时间戳形式
def string_toTimestamp(strTime):
    return time.mktime(string_toDatetime(strTime).timetuple())


# 把时间戳转成字符串形式
def timestamp_toString(stamp):
    return time.strftime("%Y-%m-%d-%H", time.localtime(stamp))


# 把datetime类型转外时间戳形式
def datetime_toTimestamp(dateTim):
    return time.mktime(dateTim.timetuple())


def time_compare():
    start_time = '2019年03月01日'
    push_time = '2019年02月14日07:37'
    if push_time >= start_time:
        print(True)
    else:
        print(False)


if __name__ == '__main__':
    # if string_toDatetime('2019-3-4') <= string_toDatetime('2019-3-1'):
    #     print(True)
    # else:
    #     print(False)
    # time_compare()
    # start_time = '2019-1-1'
    # start_time = datetime.strptime(start_time, "%Y-%m-%d")
    # else_time = '												发表于 2009-12-16 10:19 																					'.strip()
    # else_time = else_time.replace("发表于 ",'')
    # push_time = datetime.strptime(else_time, "%Y-%m-%d %H:%S")
    # print(start_time)
    # print(push_time)
    # if push_time > start_time:
    #     print(True)
    # str = 1551260953
    # timeArray = time.localtime(str)  # 秒数
    # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # print(otherStyleTime)

    time1 = str(string_toDatetime("2017-01-22"))
    tiem2 = '2017-01-02'
    if time1 > tiem2:
        print(True)
    else:
        print(False)
    time1 = datetime.date()
