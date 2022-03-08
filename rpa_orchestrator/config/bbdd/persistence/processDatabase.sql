-- Database: process
CREATE DATABASE process
WITH
OWNER = postgres
ENCODING = 'UTF8'
--LC_COLLATE = 'en_US.utf8'
--LC_CTYPE = 'en_US.utf8'
TABLESPACE = pg_default
CONNECTION LIMIT = -1;
-- Database: process
\c process
--Tables
CREATE TABLE BaseReguladora (id SERIAL NOT NULL, id_base varchar(500) NOT NULL UNIQUE, fecha_creacion timestamp NOT NULL, titulo varchar(500) NOT NULL, url varchar(1000) NOT NULL, notificada bool, PRIMARY KEY (id));
CREATE TABLE Convocatoria (id SERIAL NOT NULL, fecha_creacion timestamp, fecha_publicacion timestamp, titulo varchar(500), _from varchar(255), url varchar(1000) UNIQUE, entidad_gestora varchar(1000), entidad_convocante varchar(1000), area_tematica varchar(1000), unidad_gestion varchar(1000), modelo_ejecucion varchar(1000) ,observaciones varchar(5000), SGIid int8, BaseReguladoraid int4, notificada bool DEFAULT FALSE, PRIMARY KEY (id));
CREATE TABLE SGI (id SERIAL NOT NULL, id_sgi varchar(255) NOT NULL, url varchar(255), fecha_creacion timestamp NOT NULL, PRIMARY KEY (id));
CREATE TABLE Solicitud (id SERIAL NOT NULL, id_solicitud varchar(255), email varchar(255), concesion bool, referencia_proyecto varchar(255), IP varchar(255), fecha_creacion timestamp, SGIid int8, PRIMARY KEY (id));
CREATE TABLE Noticia (id SERIAL NOT NULL, titulo varchar(500) NOT NULL, url varchar(1000) NOT NULL, autor varchar(500) NOT NULL, fecha timestamp NOT NULL, notificada bool, PRIMARY KEY (id));

--Relation
ALTER TABLE Convocatoria ADD CONSTRAINT FKConvocator63912 FOREIGN KEY (SGIid) REFERENCES SGI (id);
ALTER TABLE Solicitud ADD CONSTRAINT FKSolicitud363261 FOREIGN KEY (SGIid) REFERENCES SGI (id);
ALTER TABLE Convocatoria ADD CONSTRAINT FKConvocator971817 FOREIGN KEY (BaseReguladoraid) REFERENCES BaseReguladora (id);
