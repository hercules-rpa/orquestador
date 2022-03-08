CREATE KEYSPACE rpa_bi
WITH replication = {
    'class':'SimpleStrategy',
    'replication_factor':1
};

CREATE TYPE rpa_bi.orchestrator(
    id text,
    name text,
    company text
);

CREATE TYPE rpa_bi.process(
    id int,
    name text
);

CREATE TYPE rpa_bi.robot_performance(
    cpu float,
    ram float,
    disk float
);

CREATE TYPE rpa_bi.log(
    id int,
    start_time bigint,
    end_time bigint,
    state text
);

CREATE TABLE rpa_bi.robot_by_activity (
    id text,
    name text,
    address text,
    ip_address text,
    online boolean,
    state text,
    process FROZEN<process>,
    process_queue list<FROZEN<process>>,
    time bigint,
    orch FROZEN<orchestrator>,
    PRIMARY KEY ((id,orch),time)
) WITH CLUSTERING ORDER BY (time DESC);


CREATE TABLE rpa_bi.robot_by_performance (
    id text,
    name text,
    address text,
    ip_address text,
    time bigint,
    orch FROZEN<orchestrator>,
    process FROZEN<process>,
    performance FROZEN<robot_performance>,
    PRIMARY KEY ((id,orch),time)
) WITH CLUSTERING ORDER BY (time DESC);


CREATE TABLE rpa_bi.execution_by_process (
    id int,
    process FROZEN<process>,
    id_robot text,
    active boolean,
    schedule_json text,
    created bigint,
    time bigint,
    log FROZEN<log>,
    orch FROZEN<orchestrator>,
    PRIMARY KEY ((id,orch), time, active)
) WITH CLUSTERING ORDER BY (time DESC);


CREATE INDEX IF NOT EXISTS index_id_robotbyactivity ON rpa_bi.robot_by_activity (id);
CREATE INDEX IF NOT EXISTS index_orch_robotbyactivity ON rpa_bi.robot_by_activity (orch);
CREATE INDEX IF NOT EXISTS index_name_robotbyactivity ON rpa_bi.robot_by_activity (name);
CREATE INDEX IF NOT EXISTS index_id_execution ON rpa_bi.execution_by_process (id);
CREATE INDEX IF NOT EXISTS index_orch_execution ON rpa_bi.execution_by_process (orch);
CREATE INDEX IF NOT EXISTS index_time_execution ON rpa_bi.execution_by_process (time);
CREATE INDEX IF NOT EXISTS active_time_execution ON rpa_bi.execution_by_process (active);