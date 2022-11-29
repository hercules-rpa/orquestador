\c rpa
INSERT INTO public.PROCESS (id, class, name, requirements, description, visible, setting) VALUES
    (1,'ProcessHolaMundo','Hola Mundo', '', 'Proceso que envía una serie de mensajes a la salida estándar para utilizarlos como prueba',true,false),
    (3,'ProcessSendMail','Proceso de envío de correos electrónicos', '', 'Proceso para enviar correo a uno o varios destinatarios', false, false),
    (9,'ProcessExtractCall','Proceso de extracción convocatorias','selenium bs4 playwright', 'Proceso para extraer las convocatorias de las páginas BDNS para su inyección en el SGI y el envío de las convocatorias de Europa por correo.', true, true),
    (10,'ProcessExtractRegulatoryBases', 'Proceso de extracción de bases reguladoras', 'module-cognitive-treelogic','Proceso que extrae las bases reguladoras del BOE seleccionando un rango de fechas y envía los resultados por correo electrónico.', true, false),
    (13,'ProcessGenerateTransferReport', 'Proceso de generación de informe de transferencia', 'module-cognitive-treelogic','Proceso que genera un informe para el boletín de transferencia.', true, false),
    (14,'ProcessPdfToTable', 'Pdf to table', '','Proceso para filtrar tablas y generar un excel a partir de un documento pdf.', false, false),
    (15,'ProcessExtractInfoPDF', 'Process Tabla a Excel', 'module-cognitive-treelogic RPA numpy pandas','Proceso para filtrar tablas y generar un excel a partir de un documento pdf.', false, false),
    (16,'ProcessExtractAward', 'Proceso extracción de concesiones', 'module-cognitive-treelogic RPA numpy pandas','Proceso para ver las solicitudes que han concedido.', true, true),
    (18,'ProcessSexenios', 'Proceso de generación de informe de un sexenio', 'docx','Proceso que genera un informe de ayuda al investigador para preparar un sexenio.', true, true),
    (22,'ProcessAcreditaciones', 'Proceso de generación de informe de una acreditación', 'docx','Proceso que genera un informe de ayuda al investigador para solicitar una acreditación de la ANECA.', true, true),
    (25,'ProcessRecommendationSystem', 'Proceso de encaje de convocatorias e investigadores', 'pandas numpy sklearn','Proceso que llama al sistema de recomendación híbrido. (Filtro Colaborativo, Contenido y Grafo Colaboración).', true, false),
    (26,'ProcessProfileReminder', 'Proceso de recordatorio de perfil de investigador', 'pandas','Proceso que manda un correo electrónico recordatorio para que los investigadores configuren su perfil.', true, false),
    (97,'ProcessExecuteCommand', 'Process Execute Robot', '', 'Proceso para ejecutar comandos en la maquina donde se ejecuta el robot', false, false),
    (98,'ProcessRestartRobot', 'Process Restart Robot', '', 'Proceso que reinicia el robot en el que se ejecuta', false, false);
