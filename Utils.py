import time
import datetime
import json
import asyncio


def current_time_millis():
    return round(time.time() * 1000)

def time_to_str(timestamp):
    tstp = datetime.datetime.fromtimestamp(timestamp)
    #return tstp.strftime('%Y-%m-%d %H:%M:%S')
    return tstp.strftime("%d/%b/%Y %H:%M:%S")



