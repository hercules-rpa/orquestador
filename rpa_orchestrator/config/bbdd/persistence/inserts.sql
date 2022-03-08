\c rpa
INSERT INTO public.PROCESS (id, class, name, requirements, description) VALUES
    (1,'ProcessHolaMundo','Hola Mundo', '', 'Proceso que envía una serie de mensajes a la salida estándar para utilizarlos como prueba'),
    (9,'ProcessExtractConvocatoria','Process Extract Convocatorias de la BDNS y la CAIXA','selenium bs4 playwright', 'Proceso para extraer las convocatorias de las páginas BDNS y la CAIXA para su inyección en el SGI'),
    (10,'ProcessExtractBasesReguladoras', 'Process Extract Bases Reguladoras', '','Proceso que extrae las bases reguladoras del BOE seleccionando un rango de fechas y envía los resultados por correo electrónico.'),
    (11,'ProcessExtractXml', 'Process Extract Xml', '','Proceso que extrae información de un fichero xml.'),
    (12,'ProcessExtractNews', 'Process Extract News', '','Proceso que extrae las noticias de la UCC y SALA DE PRENSA de la Universidad de Murcia.'),
    (13,'ProcessGenerateTransferReport', 'Process Generate Transfer Report', '','Proceso que genera un informe para el boletín de transferencia.'),
    (15,'ProcessExtractInfoPDF', 'Process Tabla a Excel', '','Proceso para filtrar tablas y generar un excel a partir de un documento pdf.');
