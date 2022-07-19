-- Database: rpa
CREATE DATABASE rpa
WITH
OWNER = postgres
ENCODING = 'UTF8'
--LC_COLLATE = 'en_US.utf8'
--LC_CTYPE = 'en_US.utf8'
TABLESPACE = pg_default
CONNECTION LIMIT = -1;
-- Database: rpa
\c rpa
-- Tables
CREATE TABLE public.ROBOT (id varchar(255) NOT NULL, name varchar(255) NOT NULL, ip_address varchar(255) NOT NULL, address varchar(255), registrations varchar(255), mac varchar(255), python_version varchar(255), os varchar(255), features TEXT, connected timestamp NOT NULL, last_seen timestamp NOT NULL, created timestamp NOT NULL,  PRIMARY KEY (id));
CREATE TABLE public.SCHEDULE (id SERIAL, id_robot VARCHAR(255), schedule_json TEXT NOT NULL, active bool NOT NULL, created timestamp, next_run timestamp, PRIMARY KEY (id));
CREATE TABLE public.PROCESS (id int4 NOT NULL, class varchar(255), name varchar(255) NOT NULL, requirements varchar(255), description varchar(255) NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.LOG (id SERIAL, id_schedule int4 NOT NULL, id_process int4 NOT NULL, id_robot varchar(255) NOT NULL, log_file_path varchar(255) NOT NULL, data TEXT, start_time timestamp, end_time timestamp, state varchar(255), finished bool NOT NULL, completed int4 NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.EVENT (id SERIAL, body varchar(255) NOT NULL, msgtype varchar(255) NOT NULL, time timestamp NOT NULL, sender varchar(255) NOT NULL, read bool NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.FILE (id SERIAL, name varchar(255) NOT NULL, absolute_path varchar(255) NOT NULL, url varchar(255), directory varchar(255) NOT NULL, time timestamp NOT NULL, PRIMARY KEY (id));
CREATE TABLE public.ROBOT_SCHEDULE (Robotid varchar(255) NOT NULL, Scheduleid int4 NOT NULL, PRIMARY KEY (Robotid, Scheduleid));


-- Relation
ALTER TABLE public.LOG ADD CONSTRAINT FKLog555362 FOREIGN KEY (id_schedule) REFERENCES public.SCHEDULE (id) on DELETE CASCADE;
ALTER TABLE public.ROBOT_SCHEDULE ADD CONSTRAINT FKRobot_Sche385328 FOREIGN KEY (Scheduleid) REFERENCES Schedule (id) on DELETE CASCADE;
ALTER TABLE public.LOG ADD CONSTRAINT FKLog948797 FOREIGN KEY (id_process) REFERENCES public.PROCESS (id);
\! echo $(pwd)
--\i inserts.sql
