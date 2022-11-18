\c rpa
INSERT INTO amqp_settings (id, "user",password,host,port,subscriptions,exchange_name,queue_name)
    VALUES (1,'admin','rpa123','10.208.99.12',5672,'{"rpa.orchestrator","rpa.orchestrator.*"}','rpa','orchestrator');

INSERT INTO dbprocess_settings (id, "user",password,host,port,database)
    VALUES (1,'postgres','docker','10.208.99.12',5432,'process');

INSERT INTO dbbi_settings (id, "user",password,host,port,keyspace)
    VALUES (1,'cassandra','cassandra','localhost',9042,'rpa_bi');

INSERT INTO orchestrator_settings (id, id_orch,name,company,pathlog_store, cdn_url)
    VALUES (1,'ORCH-REMOTE-1','ORCH-REMOTE-PLEIADES','UMU','/var/log/orchestrator/', 'http://10.208.99.12');

INSERT INTO process_settings (id, salaprensa_url,ucc_url,boe_url, bdns_url, bdns_search, europe_url,europe_link)
    VALUES (1, 'https://www.um.es/web/sala-prensa/notas-de-prensa?p_p_id=com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_GNs6DmEJkR1y&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getRSS&p_p_cacheability=cacheLevelPage&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_GNs6DmEJkR1y_currentURL=%2Fweb%2Fsala-prensa%2Fnotas-de-prensa&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_GNs6DmEJkR1y_portletAjaxable=true','https://www.um.es/web/ucc/inicio?p_p_id=com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_qQfO4ukErIc3&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getRSS&p_p_cacheability=cacheLevelPage&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_qQfO4ukErIc3_currentURL=%2Fweb%2Fucc%2F&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_qQfO4ukErIc3_portletAjaxable=true','https://boe.es/diario_boe/xml.php?id=','https://www.pap.hacienda.gob.es/bdnstrans/', 'https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias', 'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/', 'https://ec.europa.eu/info/funding-tenders/opportunities/data/referenceData/grantsTenders.json');

INSERT INTO global_settings (id, edma_host_sparql,edma_host_servicios, edma_port_sparql, sgi_ip, sgi_port, sgi_user, sgi_password, url_upload_cdn, url_release) 
    VALUES (1, 'http://82.223.242.49','https://serviciosedma.gnoss.com', 8890, 'https://salastest.um.es', 80, '10.208.99.12', 5432, 'gestor-rpa', 'gestor-rpa-2021', 'http://rpa-cdn-desa.um.es', 'https://github.com/hercules-rpa/robot/archive/refs/tags/v0.1.0-alpha.zip');

INSERT INTO users (username, password, token)
    VALUES ('admin',MD5('admin'), '');
