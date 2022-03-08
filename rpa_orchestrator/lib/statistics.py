import pandas as pd
import calendar
from cassandra.protocol import PrepareMessage
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime
from datetime import timedelta
from rpa_orchestrator.lib.bi.dbcon import ControllerDBBI

dbi = ControllerDBBI()

def unix_time_millis(dt):
    return int(dt.timestamp() * 1000.0)

def get_robot_online(id_robot, id_orch, name_orch, company_orch):
    return __get_time_online(pd.DataFrame(list(dbi.get_robot_by_activity(id_robot, id_orch, name_orch, company_orch))))

def get_executions_mounthly_by_year(id_orch, name_orch, company_orch):
    x = unix_time_millis(datetime(datetime.now().year, 1, 1))
    y = unix_time_millis(datetime(datetime.now().year, 12, 31))
    months = [0] * 12
    labels_months = calendar.month_name[1:13]
    df = pd.DataFrame(list(dbi.get_executions_by_date( x, y, id_orch,name_orch,company_orch)))
    for i in df.to_records():
        month = datetime.fromtimestamp(i['time']/1000).month
        months[month-1]+=1
    return months

def get_executions_days_by_month(id_orch, name_orch, company_orch):
    x = unix_time_millis(datetime(datetime.now().year, datetime.now().month, 1))
    y = unix_time_millis(datetime(datetime.now().year, datetime.now().month,  calendar.monthrange(datetime.now().year, datetime.now().month)[1]))
    days = [0] * calendar.monthrange(datetime.now().year, datetime.now().month)[1]

    df = pd.DataFrame(list(dbi.get_executions_by_date( x, y, id_orch,name_orch,company_orch)))
    for i in df.to_records():
        day = datetime.fromtimestamp(i['time']/1000).day
        days[day-1]+=1
    return days

def get_executions_day_by_week(id_orch, name_orch, company_orch):
    dt = datetime.now()
    dt = dt.replace(hour=0, minute=0)
    x = dt - timedelta(days=dt.weekday())
    y = x + timedelta(days=6)

    days_of_week = [0] * 7
    df = pd.DataFrame(list(dbi.get_executions_by_date(unix_time_millis(x), unix_time_millis(y), id_orch,name_orch,company_orch,)))
    for i in df.to_records():
        day_of_week = datetime.fromtimestamp(i['time']/1000).weekday()
        days_of_week[day_of_week]+=1
    return days_of_week

def get_number_executions_completed(id_orch, name_orch, company_orch):
    return dbi.get_counts_executions_by_completed(id_orch, name_orch, company_orch)[0].count

def get_robot_performance(id_robot, id_orch, name_orch, company_orch):
    x = datetime.now() - timedelta(hours=1, minutes=1)  
    y = datetime.now()
    minutes_cpu  =  [0] * 60
    minutes_ram  =  [0] * 60
    minutes_disk =  [0] * 60
    index = 59
    df = pd.DataFrame(list(dbi.get_robot_by_performance_limit(id_robot, id_orch,name_orch,company_orch, unix_time_millis(x), unix_time_millis(y))))
    minute_aux = -1
    exit = False
    for i in df.to_records():
        minute = int(datetime.fromtimestamp(i['time']/1000).minute)
        if minute==minute_aux:
            minutes_cpu[index] = i['performance'][0]
            minutes_ram[index] = i['performance'][1]
            minutes_disk[index] = i['performance'][2]
            #Cogemos el mas nuevo
            continue
            
        else:
            if minute_aux != -1 and (minute_aux - 1)%60 != minute:
                while minute_aux != minute+1:
                    if exit:
                        break
                    minutes_cpu[index]  = 0
                    minutes_ram[index]  = 0
                    minutes_disk[index] = 0
                    minute_aux = (minute_aux -1) % 60
                    index = index - 1
                    if index <= -1:
                        exit = True
                if exit:
                    break
            
            minutes_cpu[index] = i['performance'][0]
            minutes_ram[index] = i['performance'][1]
            minutes_disk[index] = i['performance'][2]            
        minute_aux = minute
        index = index - 1        
        if index <= -1:
            break
    return minutes_cpu, minutes_ram, minutes_disk


def __get_time_online(df):
    df = pd.DataFrame(df)
    nprobot = df.to_records()
    time_disconnect = datetime.now().timestamp()
    time_connect = None
    index = 0
    robot = nprobot[index]
    if robot['online']:
        while robot['online'] and index < len(nprobot):
            time_connect = robot['time']
            index += 1
            if index < len(nprobot):
                robot = nprobot[index]
    else:
        return 0 
    return (time_disconnect - time_connect)
