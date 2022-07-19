\c rpa
INSERT INTO public.PROCESS (id, class, name, requirements, description) VALUES
    (1,'ProcessHolaMundo','Hola Mundo', '', 'Proceso que envía una serie de mensajes a la salida estándar para utilizarlos como prueba'),
    (3,'ProcessSendMail','Process Send Mail', '', 'Proceso para enviar correo a uno o varios destinatarios'),
    (9,'ProcessExtractConvocatoria','Process Extract Convocatorias de la BDNS, CAIXA y Europa','selenium bs4 playwright', 'Proceso para extraer las convocatorias de las páginas BDNS y CAIXA para su inyección en el SGI y el envío de las convocatorias de Europa por correo.'),
    (10,'ProcessExtractBasesReguladoras', 'Process Extract Bases Reguladoras', '','Proceso que extrae las bases reguladoras del BOE seleccionando un rango de fechas y envía los resultados por correo electrónico.'),
    (11,'ProcessExtractXml', 'Process Extract Xml', '','Proceso que extrae información de un fichero xml.'),
    (12,'ProcessExtractNews', 'Process Extract News', '','Proceso que extrae las noticias de la UCC y SALA DE PRENSA de la Universidad de Murcia.'),
    (13,'ProcessGenerateTransferReport', 'Process Generate Transfer Report', '','Proceso que genera un informe para el boletín de transferencia.'),
    (14,'ProcessPdfToTable', 'Pdf to table', '','Proceso para filtrar tablas y generar un excel a partir de un documento pdf.'),
    (15,'ProcessExtractInfoPDF', 'Process Tabla a Excel', '','Proceso para filtrar tablas y generar un excel a partir de un documento pdf.'),
    (16,'ProcessExtractConcesion', 'Process Extract Concesion', '','Proceso para ver las solicitudes que han concedido.'),
    (18,'ProcessSexenios', 'Process Informe Sexenios', '','Proceso que genera un informe de ayuda al investigador para preparar un sexenio.'),
    (22,'ProcessAcreditaciones', 'Process Informe Acreditaciones', '','Proceso que genera un informe de ayuda al investigador para solicitar una acreditación de la ANECA.'),
    (25,'ProcessSistemaRecomendacion', 'Process Sistema de Recomendación', 'pandas','Proceso que llama al sistema de recomendación híbrido. (Filtro Colaborativo, Contenido y Grafo Colaboración).'),
    (26,'ProcessRecordatorioPerfil', 'Process Recordatorio Perfil', 'pandas','Proceso que manda un correo electrónico recordatorio para que los investigadores configuren su perfil.'),
    (99,'ProcessTranviaDaily','Process Tranvia Daily', 'pandas numpy', 'Proceso para extraer los datos diarios del blockchain del tranvia');
