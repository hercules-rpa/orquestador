from cassandra.cqlengine.columns import *
from cassandra.cluster          import Cluster
from cassandra.auth             import PlainTextAuthProvider
from datetime                   import datetime


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ControllerDBBI(metaclass=Singleton):
    def __init__(self, user, password, host, port, keyspace):
        self.user           = user
        self.password       = password
        self.host           = host
        self.port           = port
        self.auth_provider = PlainTextAuthProvider(username=user, password=password)
        self.cluster = Cluster(contact_points=[host], port=port, auth_provider=self.auth_provider)
        self.session = self.cluster.connect(keyspace)

        self.insert_robot_by_activity = self.session.prepare("INSERT INTO rpa_bi.robot_by_activity (id, name, address, ip_address, online, state, process, process_queue, time, orch) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        self.insert_robot_by_performance = self.session.prepare("INSERT INTO rpa_bi.robot_by_performance (id, name, address, ip_address, process, time, orch, performance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
        self.insert_execution_by_process = self.session.prepare("INSERT INTO rpa_bi.execution_by_process (id, process, id_robot, active, schedule_json, created, time, log, orch) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
        self.select_robot_by_activiy  = self.session.prepare("SELECT * FROM robot_by_activity WHERE id=? and orch=?")
        self.select_robot_by_activiy_by_time  = self.session.prepare("SELECT * FROM robot_by_activity WHERE id=? and orch=? and time >= ? and time <= ? ALLOW FILTERING;")
        self.select_robot_by_performance_by_limit  = self.session.prepare("SELECT * FROM robot_by_performance WHERE id=? and orch=? and  time >= ? and time <= ? ALLOW FILTERING;")
        self.select_robots_by_activiy = self.session.prepare("SELECT * FROM robot_by_activity")
        self.select_executions_by_date  = self.session.prepare("SELECT * FROM execution_by_process WHERE orch=? and time >= ? and time <= ? ALLOW FILTERING;")
        self.counts_executions_by_completed = self.session.prepare("SELECT COUNT(*) FROM execution_by_process WHERE orch=? ALLOW FILTERING;")
        self.counts_executions_by_error = self.session.prepare("SELECT COUNT(*) FROM execution_by_process WHERE orch=? AND log=? ALLOW FILTERING;")

    def unix_time_millis(self,dt):
        return int(dt.timestamp() * 1000.0)

    def dump_robot(self, robot, orch_id, orch_name, orch_comp):
        process_running = (robot.process_running['id'], robot.process_running['name']) if robot.process_running else None
        process_queue = []
        if len(robot.process_list) > 0:
            for i in robot.process_list:
                process_queue.append((i['id'], i['name']))
        else:
            process_queue = None
        self.session.execute(self.insert_robot_by_activity, [robot.id, robot.name, robot.address, 
            robot.ip_address, robot.online, robot.state, process_running, process_queue, self.unix_time_millis(datetime.now()), (orch_id, orch_name, orch_comp)])

    def dump_robot_performance(self, robot, orch_id, orch_name, orch_comp):
        process_running = (robot.process_running['id'], robot.process_running['name']) if robot.process_running else None
        self.session.execute(self.insert_robot_by_performance, [robot.id, robot.name, robot.address, 
            robot.ip_address, process_running, self.unix_time_millis(datetime.now()), (orch_id, orch_name, orch_comp), (robot.performance[0], robot.performance[1], robot.performance[2])])

    def dump_execution(self, schedule, log, orch_id, orch_name, orch_comp):
        if log:
            self.session.execute(self.insert_execution_by_process, [schedule.id, (log.id_process, log.process_name), 
                log.id_robot, schedule.is_active(), schedule.schedule_json, self.unix_time_millis(schedule.created), self.unix_time_millis(datetime.now()),(log.id, self.unix_time_millis(datetime.fromtimestamp((log.start_time))), self.unix_time_millis(datetime.fromtimestamp((log.end_time))), log.state), (orch_id, orch_name, orch_comp)])
        else:
            self.session.execute(self.insert_execution_by_process, [schedule.id, None, 
                None, schedule.is_active(), schedule.schedule_json, self.unix_time_millis(schedule.created) , self.unix_time_millis(datetime.now()),None, (orch_id, orch_name, orch_comp)])

    def get_robot_by_activity(self, robot_id, orch_id, orch_name, orch_comp):
        if robot_id:
            result = self.session.execute(self.select_robot_by_activiy, [robot_id, (orch_id, orch_name, orch_comp)])
        result = self.session.execute(self.select_robots_by_activiy)
        return result

    def get_robot_by_activity_by_time(self, robot_id, orch_id, orch_name, orch_comp, date_x, date_y):
        result = self.session.execute(self.select_robot_by_activiy_by_time, [robot_id, (orch_id, orch_name, orch_comp), date_x, date_y])
        return result

    def get_robot_by_performance_limit(self, robot_id, orch_id, orch_name, orch_comp, date_x, date_y):
        result = self.session.execute(self.select_robot_by_performance_by_limit, [robot_id, (orch_id, orch_name, orch_comp), date_x, date_y])
        return result

    def get_executions_by_date(self,date_x, date_y, orch_id, orch_name, orch_comp):
        result = self.session.execute(self.select_executions_by_date, [(orch_id, orch_name, orch_comp), date_x, date_y])
        return result

    def get_counts_executions_by_completed(self,orch_id, orch_name, orch_comp):
        result = self.session.execute(self.counts_executions_by_completed, [(orch_id, orch_name, orch_comp)])
        return result



