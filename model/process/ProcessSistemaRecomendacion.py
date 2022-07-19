import json
import model.process.Proceso4.model.ClassProcess4 as p4
import model.process.Proceso4.SRControlador as SRControlador
import model.process.Proceso4.ProcessFiltroColaborativo as FiltroColaborativo
import model.process.Proceso4.ProcessSRContenido as ProcessSRContenido
import model.process.Proceso4.ProcessMotorHibrido as ProcessMotorHibrido
import model.process.Proceso4.ProcessGrafoColaboracion as ProcessGrafoColaboracion
import pandas as pd
import model.SGI as SGI
import time
from model.process.ProcessSendMail import ProcessSendMail
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from datetime import datetime, timedelta

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText




NAME = "Sistema de Recomendación"
DESCRIPTION = "Proceso que llama al sistema de recomendación híbrido. (Filtro Colaborativo, Contenido y Grafo Colaboración)"
REQUIREMENTS = ['pandas']
ID = ProcessID.RECOMMENDATION.value
URL_API = "http://10.208.99.12:8080"

class ProcessSistemaRecomendacion(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.update_log("Proceso de recomendación ha empezado", True)
        self.log.completed = 5
        self.result = None
        self.update_log("Extraemos todas las áreas temáticas del SGI. ", True)
        SRControlador.post_areastematicas()
        self.update_log("Extraemos las convocatorias del SGI. ", True)
        convocatorias = self.get_convocatoria()
        if len(convocatorias) == 0:
            self.log.completed = 100
            self.log.end_log(time.time())
            self.state = pstatus.FINISHED
            self.update_log(
                "No hay convocatorias a notificar, el proceso ha terminado. ", True)
            return
        self.update_log(
            "Número de total de convocatorias a notificar: "+str(len(convocatorias)), True)
        # Cogemos una para q tarde menos solo PRUEBAS
        for convocatoria in convocatorias[0:2]:
            self.update_log("Convocatoria. Título: " +
                            convocatoria.titulo+" ID: "+str(convocatoria.id), True)
            self.update_log("Extraemos los investigadores. ", True)
            inv_sin_solicitud, inv_con_solicitud = self.process_investigadores(
                convocatoria)
            if not inv_sin_solicitud:
                self.log.completed = 100
                self.log.end_log(time.time())
                self.state = pstatus.FINISHED
                self.update_log(
                    "No hay investigadores a notificar, el proceso ha terminado. ", True)
                return
            
            parameters_process = {}
            parameters_process['convocatoria'] = convocatoria
            parameters_process['investigadores'] = [inv_sin_solicitud[-1]]

            process_filtroColaborativo = FiltroColaborativo.ProcessFiltroColaborativo(
                self.log.id_schedule, self.log.id, self.id_robot, "1", None, parameters_process)
            sr_contenido = ProcessSRContenido.ProcessSRContenido(
                self.log.id_schedule, self.log.id, self.id_robot, "1", None, parameters_process)
            grafo_colaboracion = ProcessGrafoColaboracion.ProcessGrafoColaboracion(
                self.log.id_schedule, self.log.id, self.id_robot, "1", None, parameters_process)

            process_filtroColaborativo.add_data_listener(self)
            sr_contenido.add_data_listener(self)
            grafo_colaboracion.add_data_listener(self)
            
            input_list = []
            
            for key, _ in self.parameters.items():
                self.log.completed += 75/len(self.parameters)
                format_input = {}
                if key == 'filtroColaborativo' and self.parameters[key]['activo']:
                    self.update_log("Se procede a llamar al sistema: FiltroColaborativo ", True)
                    process_filtroColaborativo.execute()
                    format_input['SistemaRecomendacion'] = 'FiltroColaborativo'
                    format_input['peso'] = self.parameters['filtroColaborativo']['peso']
                    format_input['data'] = process_filtroColaborativo.result
                    input_list.append(format_input)
                elif key == 'SRContenido' and self.parameters[key]['activo']:
                    self.update_log("Se procede a llamar al sistema: Basado en Contenido ", True)
                    sr_contenido.execute()
                    format_input['SistemaRecomendacion'] = 'SRContenido'
                    format_input['peso'] = self.parameters['SRContenido']['peso']
                    format_input['data'] = sr_contenido.result
                    input_list.append(format_input)
                elif key == 'GrafoColaboracion' and self.parameters[key]['activo']:
                    self.update_log("Se procede a llamar al sistema: Grafo Colaboración ", True)
                    grafo_colaboracion.execute()
                    format_input['SistemaRecomendacion'] = 'GrafoColaboracion'
                    format_input['peso'] = self.parameters['GrafoColaboracion']['peso']
                    format_input['data'] = grafo_colaboracion.result
                    input_list.append(format_input)
            
            self.update_log(
                "Se procede a llamar al motor híbrido con todos los resultados de los sistemas", True)
            motorHibrido = ProcessMotorHibrido.ProcessMotorHibrido(
                self.log.id_schedule, self.log.id, self.id_robot, "1", None, input_list)
            motorHibrido.add_data_listener(self)
            motorHibrido.execute()

            if not self.notificacion(convocatoria, motorHibrido.result):
                self.update_log("Proceso terminado con ERROR. No se han podido notificar", True)
                self.log.state = "ERROR"
                self.log.completed = 100
                self.log.end_log(time.time())
                self.state = pstatus.FINISHED
                
        print("Proceso finalizado")
        self.update_log("Se han notificado correctamente. ", True)
        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED

    def __get_solicitudes(self, idconvocatoria):
        sgi = SGI.SGI()
        r = sgi.get_solicitudes("convocatoriaId=="+str(idconvocatoria))
        if r:
            solicitudes = json.loads(r)
            return solicitudes
        return []

    def __get_investigador_sgi(self, idpersona):
        sgi = SGI.SGI()
        r = sgi.get_persona(idpersona)
        if r:
            investigador = json.loads(r)
            for email in investigador['emails']:
                if email['principal']:
                    inv = p4.Investigador(
                        nombre=investigador['nombre']+" "+investigador['apellidos'], email=email['email'])
                    return inv
        return None

    def get_convocatoria(self, fecha_inicial=None, fecha_fin=None):
        '''Obtenemos las convocatorias del SGI con Estado Registrada'''
        sgi = SGI.SGI()
        r = sgi.get_convocatorias()
        convocatorias_dict = json.loads(r)
        convocatorias = []
        convocatorias_sin_areatematica = []
        for conv in convocatorias_dict:
            # Tenemos que tener en cuenta la fecha de inicio y fin
            if conv['estado'] == "REGISTRADA":
                convocatoria = p4.Convocatoria(
                    conv['id'], conv['titulo'], None, conv['fechaPublicacion'])
                if convocatoria.creation_date:
                    convocatoria.creation_date = datetime.strptime(
                        convocatoria.creation_date.split('T')[0], '%Y-%m-%d')
                # Insertamos las areas tematicas a la convocatoria
                SRControlador.get_areamatica_sgi(convocatoria)
                if not convocatoria.areaTematica:
                    print(
                        "La convocatoria no tiene area tematica, se considera que no esta completa, por lo tanto no se tendra en cuenta")
                    convocatorias_sin_areatematica.append(convocatoria)
                else:
                    convocatorias.append(convocatoria)
        return convocatorias

    def __drop_solicitudes(self, solicitudes: list) -> pd.DataFrame:
        '''Quitamos del dataframe los investigadores que ya tienen una solicitud y generamos otro dataframe para comprobar que tengamos calificaciones de ellos'''
        # Comprobamos si ya ha solicitado esa convocatoria, y sino tenemos calificacion le mandamos un correo sabiendo
        # que ya ha solicitado la convocatoria, pero queremos saber como de interesado esta en ese area.
        investigadores_solicitud = pd.DataFrame({"nombre": [], "email": []})
        for solicitud in solicitudes:
            inv = self.__get_investigador_sgi(solicitud['solicitanteRef'])
            row = [inv.nombre, inv.email]
            investigadores_solicitud.loc[len(investigadores_solicitud)] = row
            # investigadores_solicitud.append(self.__get_investigador_sgi(solicitud['solicitanteRef']).email)
        # df_investigadores_con_solicitud = investigadores[investigadores['email'].isin(investigadores_solicitud)]
        return investigadores_solicitud  # comprobar si investigadores se ha actualizado

    def process_investigadores(self, convocatoria: p4.Convocatoria):
        '''Obtenemos todos los investigadores tanto internos (almacenados en nuestra bbdd) como de EDMA
            Los que no existan en la bbdd interna, se insertarán.
        '''
        # En caso de que hubiesen nuevos, se almacenarian.
        df_inv_interno = SRControlador.get_investigador_interno()
        if len(df_inv_interno) > 0:
            del df_inv_interno['id']
            del df_inv_interno['perfil']
        self.update_log(
            "Obtenemos los investigadores internos, total: "+str(len(df_inv_interno)), True)
        df_inv_edma = SRControlador.get_investigadores_ed()
        self.update_log(
            "Obtenemos los investigadores de EDMA, total: "+str(len(df_inv_edma)), True)
        investigadores_con_solicitud = pd.DataFrame()
        if len(df_inv_interno) == 0 and len(df_inv_edma) == 0:
            return None, None
        if len(df_inv_interno) > 0 and len(df_inv_edma) > 0:
            df_investigadores = pd.concat(
                [df_inv_interno, df_inv_edma]).drop_duplicates().reset_index(drop=True)
            # Obtenemos investigadores que no tenemos
            df_new_invs = df_inv_edma[~df_inv_edma['email'].isin(
                df_inv_interno['email'])]
            if len(df_new_invs) > 0:  # Añadimos nuevos investigadores detectados
                self.update_log(
                    "Se añaden nuevos investigadores a la base de datos interna", True)
                print("Se añaden nuevos investigadores a la base de datos interna")
                # print(df_new_invs)
                SRControlador.insert_investigadores(df_new_invs)
        elif len(df_inv_edma) == 0 and len(df_inv_interno) > 0:
            df_investigadores = df_inv_interno
        else:
            df_investigadores = df_inv_edma
            SRControlador.insert_investigadores(df_investigadores)
        # quitamos aquellos que ya han mandado la solicitud
        solicitudes = self.__get_solicitudes(convocatoria.id)
        if len(solicitudes) > 0:
            # TODO Coger los investigadores que devuelve para notificar que califiquen ese area y ese idsgi
            investigadores_con_solicitud = self.__drop_solicitudes(solicitudes)
            df_new_invs = investigadores_con_solicitud[~investigadores_con_solicitud['email'].isin(
                df_investigadores['email'])]
            if len(df_new_invs) > 0:  # Añadimos nuevos investigadores detectados
                self.update_log(
                    "En la solicitud del SGI se han encontrado investigadores que no estan ni en la BBDD interna ni en EDMA. Se proceden a insertar en la base de datos interna", True)
                print("En la solicitud del SGI se han encontrado investigadores que no estan ni en la BBDD interna ni en EDMA. Se proceden a insertar en la base de datos interna")
                print(df_new_invs)
                SRControlador.insert_investigadores(df_new_invs)
            df_investigadores = df_investigadores[~df_investigadores.email.isin(
                investigadores_con_solicitud.email)]
        # faltaria comprobar si esa convocatoria la tienen notificada o no
        investigadores_listado_sin_solicitud = []
        investigadores_listado_con_solicitud = []

        #print("Investigadores 0: ",df_investigadores.shape, investigadores_con_solicitud.shape)
        for _, inv in df_investigadores.iterrows():
            inv_a_notificar = SRControlador.get_notificacion_interna(
                inv['email'], convocatoria)
            if inv_a_notificar:
                SRControlador.cargar_perfil(inv_a_notificar) #Cargamos el perfil de las puntuaciones, si ya lo tuviera configurado no es necesario
                investigadores_listado_sin_solicitud.append(inv_a_notificar)

        for _, inv in investigadores_con_solicitud.iterrows():
            inv_a_notificar = SRControlador.get_notificacion_interna(
                inv['email'], convocatoria)
            if inv_a_notificar:
                investigadores_listado_con_solicitud.append(inv_a_notificar)
        #print("Investigadores: ",len(investigadores_listado_sin_solicitud), len(investigadores_listado_con_solicitud))
        self.update_log("Total de investigadores que NO han hecho la solicitud " +
                        str(len(investigadores_listado_sin_solicitud)), True)
        self.update_log("Total de investigadores que SI han hecho la solicitud " +
                        str(len(investigadores_listado_con_solicitud)), True)
        return investigadores_listado_sin_solicitud, investigadores_listado_con_solicitud

    def generar_correo(self, convocatoria: p4.Convocatoria, investigador: p4.Investigador):
        token = SRControlador.generate_token(investigador.id)
        if not token:
            self.update_log(
                "No se pudo generar el token. No se puede enviar el correo al investigador "+investigador.nombre, True)
            return False

        sgi = SGI.SGI()
        convocatoria_base = json.loads(sgi.get_convocatoria(convocatoria.id))
        convocatoria_entidad_convo = sgi.get_entidades_convocantes_convocatoria(
            convocatoria.id)
        convocatoria_entidad_finan = sgi.get_entidades_financiadora_convocatoria(
            convocatoria.id)

        if convocatoria_entidad_convo and len(convocatoria_entidad_convo) > 0:
            convocatoria_entidad_convo = json.loads(
                convocatoria_entidad_convo)[0]

        if convocatoria_entidad_finan and len(convocatoria_entidad_finan) > 0:
            convocatoria_entidad_finan = json.loads(
                convocatoria_entidad_finan)[0]
        
        if convocatoria_base['fechaConcesion']:  
            fecha_concesion = datetime.strptime(convocatoria_base['fechaConcesion'], "%Y-%m-%dT%H:%M:%SZ")
            fecha_concesion = datetime.strftime(fecha_concesion, "%d/%m/%Y")
        else:
            fecha_concesion = "Desconocida"
            
        if convocatoria_base['fechaPublicacion']:
            fecha_publicacion = datetime.strptime(convocatoria_base['fechaPublicacion'], "%Y-%m-%dT%H:%M:%SZ")
            fecha_publicacion = datetime.strftime(fecha_publicacion, "%d/%m/%Y")
        else:
            fecha_publicacion = "Desconocida"

        hola_investigador = """<p style="margin:0 0 12px 0;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">Hola """ + \
            investigador.nombre+""",</p>"""
        html_titulo = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Título: </b>""" + \
            convocatoria_base['titulo']+""" </p>"""
        html_descripcion = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Descripción: </b>""" + \
            convocatoria_base['objeto']+""" </p>"""
        html_observaciones = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Observaciones: </b>""" + \
            convocatoria_base['observaciones']+""" </p>"""
        html_ambito_geografico = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Ámbito Geográfico: </b>""" + \
            convocatoria_base['ambitoGeografico']['nombre']+""" </p>"""
        html_fpublicacion = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Fecha publicación: </b>""" + \
            fecha_publicacion+""" </p>"""
        html_fconcesion = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Fecha de concesión: </b>""" + \
            fecha_concesion+""" </p>"""
        html_url_sgi_detalle = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">Consulta la convocatoria en el SGI para más detalles </p>"""
        url_sgi = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><a href="""+sgi.host + '/csp/convocatoria/' + \
            str(convocatoria.id) + '/datos-generales' + \
            """ style="color:#ee4c50;text-decoration:underline;">Enlace a la convocatoria</a></p>"""
        interes_conv = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>**¿Te ha resultado de interés esta convocatoria? </b> <a href="""+URL_API+"/#/p/feedback/"+token+"/" + \
            str(convocatoria.id)+"/si"+""" style="color:#ee4c50;text-decoration:underline;">Si</a> / <a href="""+URL_API+"/#/p/feedback/" + \
            token+"/"+str(convocatoria.id)+"/no" + \
            """ style="color:#ee4c50;text-decoration:underline;">No</a></p>"""
        url_perfil = """<tr><td><p style="margin-top:50px;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">Puedes obtener convocatorias más personalizadas configurando su perfil. </p>
                        <p style="margin-top:1px;font-size:16px;font-family:Arial,sans-serif;"><a href="""+URL_API+"/#/p/profilerecommendation/"+token+""" style="color:#ee4c50;text-decoration:underline;">Configurar mi perfil</a></p><p style="margin-top:30px;margin-bottom:5px;font-size:12px;line-height:24px;font-family:Arial,sans-serif;">**No comparta ningún enlance, son exclusivos para cada investigador.**</p></td></tr>"""

        html_body_convocatoria = []
        if convocatoria_entidad_convo:
            if convocatoria_entidad_convo['programa']:
                if sgi.get_empresa(convocatoria_entidad_convo['entidadRef']):
                    empresa_nombre = json.loads(sgi.get_empresa(
                        convocatoria_entidad_convo['entidadRef']))['nombre']
                else:
                    empresa_nombre = ""

                html_entidad_convo = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Entidad Convocante:</b>"""+empresa_nombre+""" </p>"""
                html_body_convocatoria.append(html_entidad_convo)

        if convocatoria_entidad_finan:
            print(convocatoria_entidad_finan)
            if sgi.get_empresa(convocatoria_entidad_finan['entidadRef']):
                empresa_nombre = json.loads(sgi.get_empresa(
                    convocatoria_entidad_finan['entidadRef']))['nombre']
            else:
                empresa_nombre = ""
            html_entidad_finan = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Entidad Financiadora:</b>"""+empresa_nombre+""" </p>"""
            html_body_convocatoria.append(html_entidad_finan)

            if convocatoria_entidad_finan['tipoFinanciacion']:
                html_entidad_finan = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Tipo Financiación:</b>"""+convocatoria_entidad_finan['tipoFinanciacion']['nombre']+""" </p>"""
                html_body_convocatoria.append(html_entidad_finan)
            
            if convocatoria_entidad_finan['porcentajeFinanciacion']:
                html_entidad_finan = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Porcentaje de Financiación:</b>"""+str(convocatoria_entidad_finan['porcentajeFinanciacion'])+""" </p>"""
                html_body_convocatoria.append(html_entidad_finan)
            
            if convocatoria_entidad_finan['importeFinanciacion']:
                html_entidad_finan = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Importe de Financiación:</b>"""+str(convocatoria_entidad_finan['importeFinanciacion'])+""" </p>"""
                html_body_convocatoria.append(html_entidad_finan)

        html_body_convocatoria.append(html_titulo)
        html_body_convocatoria.append(html_descripcion)
        html_body_convocatoria.append(html_observaciones)
        html_body_convocatoria.append(html_ambito_geografico)
        html_body_convocatoria.append(html_fpublicacion)
        html_body_convocatoria.append(html_fconcesion)
        html_body_convocatoria.append(html_url_sgi_detalle)
        html_body_convocatoria.append(url_sgi)
        html_body_convocatoria.append(interes_conv)

        body = """
            <!DOCTYPE html>
            <html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">

            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <meta name="x-apple-disable-message-reformatting">
            <title></title>
            <!--[if mso]>
                <noscript>
                    <xml>
                        <o:OfficeDocumentSettings>
                            <o:PixelsPerInch>96</o:PixelsPerInch>
                        </o:OfficeDocumentSettings>
                    </xml>
                </noscript>
                <![endif]-->
            <style>
                table,
                td,
                div,
                h1,
                p {
                font-family: Arial, sans-serif;
                }

                ,
            </style>
            </head>

            <body style="margin:0;padding:0;">
            <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:#ffffff;">
                <tr>
                <td align="center" style="padding:0;">
                    <table role="presentation" style="width:602px;border-collapse:collapse;border:1px solid #cccccc;border-spacing:0;text-align:left;">
                    <tr>
                        <td style="padding:36px 30px 42px 30px;">
                        <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;">
                            <tr>
                            <td style="padding:0 0 36px 0;color:#153643;">
                                """+hola_investigador+"""
                                <p style="margin:0 0 12px 0;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">En el SGI hay una convocatoria disponisble, pensamos que te puede interesar.</p>
                            </td>
                            </tr>

                            <tr>
                            <td style="padding:0 0 36px 0;color:#153643;  border: 0px solid black; background:#F8F7EA;">
                                <h1 style="font-size:26px;margin:0 0 20px 0;font-family:Arial,sans-serif;"> Convocatoria</h1>"""+' '.join(html_body_convocatoria)+"""   
                            </td>
                            </tr>"""+url_perfil+"""
                        </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:30px;background:#ff0000;">
                        <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;font-size:9px;font-family:Arial,sans-serif;">
                            <tr>
                            <td style="padding:0;width:50%;" align="left">
                                <p style="margin:0;font-size:14px;line-height:16px;font-family:Arial,sans-serif;color:#ffffff;">
                                &reg; Hercules-RPA<br />
                                </p>
                            </td>

                            </tr>
                        </table>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>
            </table>
            </body>

            </html>
        """
        print(body)
        # params = {}
        # params["user"] = ""
        # params["password"] = ""
        # params["smtp_server"] = "smtp.um.es"
        # params["receivers"] = []
        # user = {}
        # user["sender"] = "noreply@um.es"
        # user["receiver"] = investigador.email
        # user["subject"] = "Convocatoria SGI"
        # user["body"] = body
        # user["attached"] = []
        # params["receivers"].append(user)
        # psm = ProcessSendMail(self.log.id_schedule,
        #                       self.log.id, self.id_robot, "1", None, params)
        # psm.add_data_listener(self)
        # psm.execute()
        # if psm.log.state == "ERROR":
        #     self.update_log("No se pudo enviar el correo al investigador"+investigador.email, True)
        #     self.log.state = "ERROR"
        #     self.log.completed = 100
        #     return False

        # Create message container - the correct MIME type is multipart/alternative.
        # msg = MIMEMultipart('alternative')
        # msg['Subject'] = "Link"
        # msg['From'] = "noreply@um.es"
        # msg['To'] = investigador.email
        # part2 = MIMEText(body, 'html')

        # # Attach parts into message container.
        # # According to RFC 2046, the last part of a multipart message, in this case
        # # the HTML message, is best and preferred.
        # msg.attach(part2)

        # # Send the message via local SMTP server.
        # s = smtplib.SMTP('smtp.um.es')
        # # sendmail function takes 3 arguments: sender's address, recipient's address
        # # and message to send - here it is sent as one string.
        # s.sendmail("", investigador.email, msg.as_string())
        # s.quit()

        # if correo funcionó:
        if not SRControlador.post_notificacion(investigador, convocatoria):
            self.update_log("Error al insertar la notificación del investigador " +
                            investigador.nombre+" con ID "+str(investigador.id), True)
            print("Error al insertar la notificación en BBDD")
        return True

    def test_process_filtro_colaborativo(self, threshold_count=150):
        inputAreas = [
            {'areaId': 4, 'nombre': 'TOS'},
            {'areaId': 6, 'nombre': 'TIC'}

        ]
        inputAreas = pd.DataFrame(inputAreas)
        df_inv = pd.read_csv('hercules-rpa/test/process4/testRecomendacionFC.csv')
        investigadores_ids = df_inv.loc[~df_inv['invId'].duplicated()]
        investigadores_ids = investigadores_ids['invId'].tolist()
        investigadores = []
        for investigador in investigadores_ids:
            investigadores.append(p4.Investigador(
                id=investigador, nombre="test", email="test@um.es"))

        parameters = {}
        parameters['investigadores'] = investigadores

        filtroColaborativo = FiltroColaborativo.SRFiltroColaborativo(
            parameters)
        result = filtroColaborativo.recomedacion_filtro_colaborativo(
            inputAreas, df_inv, investigadores, threshold_count=threshold_count)
        print(result)
        return result

    def test_process_contenido(self, idconvocatoria=2):
        areaTematica1 = p4.AreaTematica(id=4, areaPadre=None, nombre="TOS")
        areaTematica2 = p4.AreaTematica(
            id=6, areaPadre=areaTematica1, nombre="TIC")
        areaTematica1.areaHijo = areaTematica2
        convocatoria = p4.Convocatoria(2, "test", [areaTematica1], None)
        parameters = {}
        parameters['convocatoria'] = convocatoria
        sr_contenido = ProcessSRContenido.ProcessSRContenido(parameters)
        convo_input_format = sr_contenido.get_format_convocatoria(
            idconvocatoria)
        investigadores = {}
        df_inv = pd.read_csv(
            'hercules-rpa/test/process4/testRecomendacionContenido.csv')
        for idx, id_inv in enumerate(df_inv['invId'].tolist()):
            if not id_inv in investigadores:
                investigadores[id_inv] = []
            word = df_inv['words'][idx]
            investigadores[id_inv].append(word)
        # print(investigadores)
        print("Convocatoria input")
        print(convo_input_format)
        result = sr_contenido.SR_contenido(
            convo_input_format, investigadores, threshold_count=3, test=True)
        print(result)
        return result

    def test_grafo_colaboracion(self):
        parameters_input = {}
        investigadores = []
        convocatoria = p4.Convocatoria(2, "test", None, None)
        investigadores.append(p4.Investigador(
            id=1, nombre=None, email="skarmeta@um.es"))
        investigadores.append(p4.Investigador(
            id=2, nombre=None, email="jmjuarez@um.es"))
        investigadores.append(p4.Investigador(
            id=3, nombre=None, email="jtpalma@um.es"))
        investigadores.append(p4.Investigador(
            id=4, nombre=None, email="oscar.navarrot@um.es"))
        parameters_input['convocatoria'] = convocatoria
        parameters_input['investigadores'] = investigadores
        gc = ProcessGrafoColaboracion.ProcessGrafoColaboracion(
            parameters_input)
        gc.exec_process()
        return gc.result

    def test_motor_hibrido(self):
        test_fc = self.test_process_filtro_colaborativo()
        test_c = self.test_process_contenido()
        test_gc = self.test_grafo_colaboracion()
        input_list = []
        format_input = {}
        format_input['SistemaRecomendacion'] = 'FiltroColaborativo'
        format_input['peso'] = 0.70
        format_input['data'] = test_fc
        input_list.append(format_input)
        format_input = {}
        format_input['SistemaRecomendacion'] = 'SRContenido'
        format_input['peso'] = 0.2
        format_input['data'] = test_c
        input_list.append(format_input)
        format_input = {}
        format_input['SistemaRecomendacion'] = 'GrafoColaboracion'
        format_input['peso'] = 0.1
        format_input['data'] = test_gc
        input_list.append(format_input)
        motorHibrido = ProcessMotorHibrido.ProcessMotorHibrido(input_list)
        motorHibrido.exec_process()
        print(motorHibrido.result)
        return motorHibrido.result

    def notificacion(self, convocatoria, investigadores, threshold_puntuacion=0.4):
        self.update_log("Notificamos la convocatoria " +
                        convocatoria.titulo, True)
        for idInv, puntuacion in investigadores.items():
            if puntuacion > threshold_puntuacion:
                investigador = SRControlador.get_investigador_interno(idInv)
                print("Investigador: ", investigador.email)
                if investigador.email == "josemanuel.bernabe@um.es":
                    if not self.generar_correo(convocatoria, investigador):
                        return False
        return True

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
