-- Database: rpa
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

CREATE TABLE BaseReguladora (id SERIAL NOT NULL, id_base varchar(500) NOT NULL UNIQUE, fecha_creacion timestamp default CURRENT_TIMESTAMP NOT NULL, titulo varchar(500) NOT NULL, url varchar(1000) NOT NULL, notificada bool, seccion varchar(500), departamento varchar(500), PRIMARY KEY (id));
CREATE TABLE Convocatoria (id SERIAL NOT NULL,  id_sgi varchar(100), fecha_inicio timestamp default CURRENT_TIMESTAMP, fecha_fin timestamp default CURRENT_TIMESTAMP, fecha_definitiva timestamp default CURRENT_TIMESTAMP, fecha_creacion timestamp default CURRENT_TIMESTAMP, fecha_publicacion timestamp default CURRENT_TIMESTAMP, titulo varchar(500), _from varchar(255), url varchar(1000) UNIQUE, entidad_gestora varchar(1000), entidad_convocante varchar(1000), area_tematica varchar(1000), unidad_gestion varchar(1000), modelo_ejecucion varchar(1000) ,observaciones varchar(5000), notificada bool DEFAULT FALSE, PRIMARY KEY (id));
CREATE TABLE AreaTematica (id SERIAL NOT NULL, fuente varchar(255), nombre varchar(500) NOT NULL, descripcion varchar(500) NOT NULL, PRIMARY KEY (id));
CREATE TABLE AreaTematica_AreaTematica (AreaTematicaid int4 NOT NULL, AreaTematicaidhijo int4 NOT NULL, PRIMARY KEY (AreaTematicaid, AreaTematicaidhijo));
CREATE TABLE CalificacionArea (id SERIAL NOT NULL, idInvestigador int4 NOT NULL, idArea int4, puntuacion NUMERIC(3,2), PRIMARY KEY (id));
CREATE TABLE CalificacionConvocatoria (id SERIAL NOT NULL, idConvocatoriaSGI int4 NOT NULL, titulo varchar(1000) NOT NULL, idInvestigador int4 NOT NULL, puntuacion NUMERIC(3,2) NOT NULL, PRIMARY KEY (id));
CREATE TABLE Investigador (id SERIAL NOT NULL, nombre varchar(500), email varchar(800) NOT NULL UNIQUE, perfil bool, PRIMARY KEY (id));
CREATE TABLE NotificacionInvestigador (id SERIAL NOT NULL, idInvestigador int4 NOT NULL, idConvocatoriaSgi int4 NOT NULL, feedback bool NOT NULL, fechaCreacion timestamp NOT NULL, PRIMARY KEY (id));
CREATE TABLE Ejecucion_Boletin (id SERIAL NOT NULL, fecha_inicio timestamp default CURRENT_TIMESTAMP, fecha_fin timestamp default CURRENT_TIMESTAMP, fecha_ejecucion timestamp default CURRENT_TIMESTAMP, exito bool, PRIMARY KEY(id));


--Relation
ALTER TABLE NotificacionInvestigador ADD CONSTRAINT FKNotificaci864820 FOREIGN KEY (idInvestigador) REFERENCES Investigador (id);
ALTER TABLE CalificacionArea ADD CONSTRAINT FKCalificaci307021 FOREIGN KEY (idArea) REFERENCES AreaTematica (id);
ALTER TABLE CalificacionArea ADD CONSTRAINT FKCalificaci811380 FOREIGN KEY (idInvestigador) REFERENCES Investigador (id);
ALTER TABLE CalificacionConvocatoria ADD CONSTRAINT FKCalificaci175144 FOREIGN KEY (idInvestigador) REFERENCES Investigador (id);
ALTER TABLE AreaTematica_AreaTematica ADD CONSTRAINT FKAreaTemati19530 FOREIGN KEY (AreaTematicaid) REFERENCES AreaTematica (id);
ALTER TABLE AreaTematica_AreaTematica ADD CONSTRAINT FKAreaTemati109908 FOREIGN KEY (AreaTematicaidhijo) REFERENCES AreaTematica (id);


--INDEX--
CREATE UNIQUE INDEX CalificacionArea_id ON CalificacionArea (id);
CREATE INDEX CalificacionConvocatoria_idConvocatoriaSGI ON CalificacionConvocatoria (idConvocatoriaSGI);
CREATE UNIQUE INDEX Investigador_id ON Investigador (id);
CREATE UNIQUE INDEX NotificacionInvestigador_id ON NotificacionInvestigador (id);
CREATE INDEX NotificacionInvestigador_idInvestigador ON NotificacionInvestigador (idInvestigador);
CREATE INDEX NotificacionInvestigador_idConvocatoriaSgi ON NotificacionInvestigador (idConvocatoriaSgi);
