-- Database: rpa
CREATE DATABASE rpa
WITH
ENCODING = 'UTF8'
--LC_COLLATE = 'en_US.utf8'
--LC_CTYPE = 'en_US.utf8'
TABLESPACE = pg_default
CONNECTION LIMIT = -1;
-- Database: rpa
\c rpa
-- Tables
CREATE TABLE public.ROBOT (id varchar(255) NOT NULL, name varchar(255) NOT NULL, ip_address varchar(255), address varchar(255), registrations varchar(255), mac varchar(255), python_version varchar(255), os varchar(255), features TEXT, connected timestamp NOT NULL, last_seen timestamp NOT NULL, created timestamp NOT NULL,  PRIMARY KEY (id));
CREATE TABLE public.SCHEDULE (id SERIAL, id_robot VARCHAR(255), schedule_json TEXT NOT NULL, active bool NOT NULL, created timestamp, next_run timestamp, PRIMARY KEY (id));
CREATE TABLE public.PROCESS (id int4 NOT NULL, class varchar(255), name varchar(255) NOT NULL, requirements varchar(255), description varchar(255) NOT NULL, visible bool NOT NULL, setting bool NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.LOG (id SERIAL, id_schedule int4 NOT NULL, id_process int4 NOT NULL, id_robot varchar(255) NOT NULL, log_file_path varchar(255) NOT NULL, data TEXT, start_time timestamp, end_time timestamp, state varchar(255), finished bool NOT NULL, completed int4 NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.EVENT (id SERIAL, body varchar(255) NOT NULL, msgtype varchar(255) NOT NULL, time timestamp NOT NULL, sender varchar(255) NOT NULL, read bool NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.FILE (id SERIAL, name varchar(255) NOT NULL, absolute_path varchar(255) NOT NULL, url varchar(255), directory varchar(255) NOT NULL, time timestamp NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.FILE_CDN (id SERIAL, name varchar(255) NOT NULL, url_cdn varchar(255));
CREATE TABLE public.ROBOT_SCHEDULE (Robotid varchar(255) NOT NULL, Scheduleid int4 NOT NULL, PRIMARY KEY (Robotid, Scheduleid));

-- SETTINGS
CREATE TABLE public.AMQP_SETTINGS (id int4 NOT NULL, "user" varchar(255) NOT NULL,password varchar(255) NOT NULL, host varchar(255) NOT NULL, port int8 NOT NULL,subscriptions text[], exchange_name varchar(255) NOT NULL, queue_name varchar(255) NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.DBPROCESS_SETTINGS (id int4 NOT NULL, "user" varchar(255) NOT NULL,password varchar(255) NOT NULL, host varchar(255) NOT NULL, port int8 NOT NULL,database varchar(255) NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.DBBI_SETTINGS (id int4 NOT NULL, "user" varchar(255) NOT NULL,password varchar(255) NOT NULL, host varchar(255) NOT NULL, port int8 NOT NULL,keyspace varchar(255) NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.ORCHESTRATOR_SETTINGS (id int4 NOT NULL, id_orch varchar(1000) NOT NULL,name varchar(1000) NOT NULL,company varchar(1000) NOT NULL, pathlog_store varchar(1000) NOT NULL, cdn_url varchar(1000) NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.PROCESS_SETTINGS (id int4 NOT NULL, salaprensa_url varchar(1024) NOT NULL,ucc_url varchar(1024) NOT NULL,boe_url varchar(1024) NOT NULL, bdns_url varchar(1024) NOT NULL, bdns_search varchar(1024) NOT NULL, europe_url varchar(1024) NOT NULL, europe_link varchar(1024) NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.GLOBAL_SETTINGS (id int4 NOT NULL, edma_host_sparql varchar(255) NOT NULL,edma_host_servicios varchar(255) NOT NULL,edma_port_sparql bigint NOT NULL, sgi_ip varchar(255) NOT NULL,sgi_port bigint NOT NULL,database_ip varchar(255) NOT NULL,database_port bigint NOT NULL,sgi_user varchar(255),sgi_password varchar(1024),ftp_user varchar(255),ftp_password varchar(1024), ftp_port int4,PRIMARY KEY (id));


-- Relation
ALTER TABLE public.LOG ADD CONSTRAINT FKLog555362 FOREIGN KEY (id_schedule) REFERENCES public.SCHEDULE (id) on DELETE CASCADE;
ALTER TABLE public.ROBOT_SCHEDULE ADD CONSTRAINT FKRobot_Sche385328 FOREIGN KEY (Scheduleid) REFERENCES Schedule (id) on DELETE CASCADE;
ALTER TABLE public.ROBOT_SCHEDULE ADD CONSTRAINT FKRobot_Sche396439 FOREIGN KEY (Robotid) REFERENCES ROBOT (id) on DELETE CASCADE;
ALTER TABLE public.LOG ADD CONSTRAINT FKLog948797 FOREIGN KEY (id_process) REFERENCES public.PROCESS (id);


-- Index
CREATE UNIQUE INDEX ROBOT_id ON ROBOT (id);
CREATE UNIQUE INDEX SCHEDULE_id ON SCHEDULE (id);
CREATE UNIQUE INDEX PROCESS_ID on PROCESS (id);
CREATE UNIQUE INDEX LOG_id on LOG (id);
CREATE UNIQUE INDEX FILE_id on FILE (id);
CREATE UNIQUE INDEX FILE_id_cdn on FILE_CDN (id);
CREATE UNIQUE INDEX EVENT_id on EVENT (id);
CREATE INDEX LOG_idschedule ON LOG (id_schedule);
CREATE INDEX LOG_idprocess ON LOG (id_process);
CREATE INDEX LOG_idrobot ON LOG (id_robot);

\! echo $(pwd)



--\i inserts.sql
