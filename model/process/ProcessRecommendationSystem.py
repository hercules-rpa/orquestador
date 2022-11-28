import json

import model.process.Process4.model.ClassProcess4 as p4
import model.process.Process4.ProcessCollaborativeFiltering as FiltroColaborativo
import model.process.Process4.ProcessRSContent as ProcessSRContenido
import model.process.Process4.ProcessHybridEngine as ProcessMotorHibrido
import model.process.Process4.ProcessCollaborativeGraph as ProcessGrafoColaboracion
import pandas as pd
import model.SGI as SGI
import time
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from datetime import datetime
from rpa_robot.ControllerRobot import ControllerRobot
from model.process.UtilsProcess import UtilsProcess
from rpa_robot.ControllerSettings import ControllerSettings
from model.process.Process4.RSController import RSController

NAME = "Sistema de Recomendación"
DESCRIPTION = "Proceso que llama al sistema de recomendación híbrido. (Filtro Colaborativo, Contenido y Grafo Colaboración)"
REQUIREMENTS = ['pandas']
ID = ProcessID.RECOMMENDATION.value
URL_PROFILE = "/#/p/profilerecommendation/"
URL_SGI = "/csp/convocatoria/"
URL_FEEDBACK = "/#/p/feedback/"
cs = ControllerSettings()
controllerRobot = ControllerRobot()

class ProcessRecommendationSystem(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None, ip_api = None, port_api = None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)
        self.url_api = self.ip_api+":"+str(self.port_api)
        
    def execute(self):
        """
        Método encargado de la ejecución del proceso de recomendación
        """
        global rsController
        rsController = RSController(self.ip_api, self.port_api)
        print(self.parameters)
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.update_log("Proceso de recomendación ha empezado", True)
        self.log.completed = 5
        self.result = None
        self.update_log("Extraemos todas las áreas temáticas del SGI. ", True)
        rsController.post_areastematicas()
        self.update_log("Extraemos las convocatorias del SGI. ", True)
        convocatorias = self.get_convocatoria()
        if len(convocatorias) == 0:
            self.log.completed = 100
            self.state = pstatus.FINISHED
            self.update_log(
                "No hay convocatorias a notificar, el proceso ha terminado. ", True)
            self.log.end_log(time.time())
            return
        self.update_log(
            "Número de total de convocatorias a notificar: "+str(len(convocatorias)), True)

        for convocatoria in convocatorias:
            self.log.completed += 95/len(convocatorias)
            self.update_log("Convocatoria. Título: " +
                            convocatoria.titulo+" ID: "+str(convocatoria.id), True)
            self.update_log("Extraemos los investigadores. ", True)
            inv_sin_solicitud, inv_con_solicitud = self.process_investigadores(
                convocatoria)
            if not inv_sin_solicitud:
                self.update_log(
                    "No hay investigadores a notificar para esta convocatoria, han sido ya notificados o no es de interés. ", True)
            
            parameters_process = {}
            parameters_process['convocatoria'] = convocatoria
            parameters_process['investigadores'] = inv_sin_solicitud

            process_collaborativeFiltering = FiltroColaborativo.ProcessCollaborativeFiltering(
                self.log.id_schedule, self.log.id, self.id_robot, "1", None, parameters_process, self.ip_api, self.port_api)
            rs_content = ProcessSRContenido.ProcessRSContent(
                self.log.id_schedule, self.log.id, self.id_robot, "1", None, parameters_process, self.ip_api, self.port_api)
            collaboration_graph = ProcessGrafoColaboracion.ProcessCollaborativeGraph(
                self.log.id_schedule, self.log.id, self.id_robot, "1", None, parameters_process, self.ip_api, self.port_api)

            process_collaborativeFiltering.add_data_listener(self)
            rs_content.add_data_listener(self)
            collaboration_graph.add_data_listener(self)
            
            input_list = []
            
            threshold_score = float(self.parameters['threshold_score'])
            format_input = {}
            if self.parameters['fc_activo']:
                self.update_log("Se procede a llamar al sistema: FiltroColaborativo ", True)
                process_collaborativeFiltering.execute()
                format_input['SistemaRecomendacion'] = 'FiltroColaborativo'
                format_input['peso'] = float(self.parameters['fc_peso'])
                format_input['data'] = process_collaborativeFiltering.result
                input_list.append(format_input)
            elif self.parameters['sr_activo']:
                self.update_log("Se procede a llamar al sistema: Basado en Contenido ", True)
                rs_content.execute()
                format_input['SistemaRecomendacion'] = 'SRContenido'
                format_input['peso'] = self.parameters['sr_peso']
                format_input['data'] = rs_content.result
                input_list.append(format_input)
            elif self.parameters['gc_activo']:
                self.update_log("Se procede a llamar al sistema: Grafo Colaboración ", True)
                collaboration_graph.execute()
                format_input['SistemaRecomendacion'] = 'GrafoColaboracion'
                format_input['peso'] = self.parameters['gc_peso']
                format_input['data'] = collaboration_graph.result
                input_list.append(format_input)
        
            self.update_log(
                "Se procede a llamar al motor híbrido con todos los resultados de los sistemas", True)
            hybrid_engine = ProcessMotorHibrido.ProcessHybridEngine(
                self.log.id_schedule, self.log.id, self.id_robot, "1", None, input_list)
            hybrid_engine.add_data_listener(self)
            hybrid_engine.execute()

            if not self.notificacion(convocatoria, hybrid_engine.result, threshold_score):
                self.update_log("Proceso terminado con ERROR. No se han podido notificar", True)
                self.log.state = "ERROR"
                self.log.completed = 100
                self.state = pstatus.FINISHED
                self.log.end_log(time.time())
                return
                
        print("Proceso finalizado")
        self.update_log("Se han notificado correctamente. ", True)
        self.log.completed = 100
        self.state = pstatus.FINISHED
        self.log.end_log(time.time())
        

    def __get_solicitudes(self, idconvocatoria):
        """
        Método para obtener las solicitudes de una convocatoria
        :param idconvocatoria id de la convocatoria
        :return devuelve una lista con las solicitudes
        """
        sgi = cs.get_sgi(self.ip_api, self.port_api)
        r = sgi.get_forms("convocatoriaId=="+str(idconvocatoria))
        if r:
            solicitudes = json.loads(r)
            return solicitudes
        return []

    def __get_investigador_sgi(self, idpersona):
        """
        Método para obtener información de una persona
        :param idpersona id de la persona que queremos consultar
        :return clase investigador o nulo
        """
        sgi = cs.get_sgi(self.ip_api, self.port_api)
        r = sgi.get_person(idpersona)
        if r:
            investigador = json.loads(r)
            for email in investigador['emails']:
                if email['principal']:
                    inv = p4.Investigador(
                        nombre=investigador['nombre']+" "+investigador['apellidos'], email=email['email'])
                    return inv
        return None

    def get_convocatoria(self):
        """
        Método para obtener las convocatorias del SGI con Estado Registrada
        :return lista de clase convocatorias
        """
        sgi = cs.get_sgi(self.ip_api, self.port_api)
        r = sgi.get_calls('activo==true;estado==REGISTRADA')
        convocatorias_dict = json.loads(r)
        convocatorias = []
        convocatorias_sin_areatematica = []
        for conv in convocatorias_dict:
            convocatoria = p4.Convocatoria(
                conv['id'], conv['titulo'], None, conv['fechaPublicacion'])
            # Insertamos las areas tematicas a la convocatoria
            rsController.get_areamatica_sgi(convocatoria)
            if not convocatoria.areaTematica:
                #La convocatoria no tiene area tematica, se considera que no esta completa, por lo tanto no se tendra en cuenta
                convocatorias_sin_areatematica.append(convocatoria)
            else:
                convocatorias.append(convocatoria)
        return convocatorias

    def __drop_solicitudes(self, solicitudes: list) -> pd.DataFrame:
        """
        Método para separar del dataframe los investigadores que ya tienen una solicitud
        :param solicitudes lista de solicitudes de una convocatoria
        :return dataframe investigadores con solicitudes
        """
        investigadores_solicitud = pd.DataFrame({"nombre": [], "email": []})
        for solicitud in solicitudes:
            inv = self.__get_investigador_sgi(solicitud['solicitanteRef'])
            row = [inv.nombre, inv.email]
            investigadores_solicitud.loc[len(investigadores_solicitud)] = row
            # investigadores_solicitud.append(self.__get_investigador_sgi(solicitud['solicitanteRef']).email)
        # df_investigadores_con_solicitud = investigadores[investigadores['email'].isin(investigadores_solicitud)]
        return investigadores_solicitud
    
    def process_investigadores(self, convocatoria: p4.Convocatoria):
        """
        Método para obtener todos los investigadores tanto internos (almacenados en nuestra bbdd) como de EDMA 
        Los que no existan en la bbdd interna, se insertarán. En caso de que hubiesen nuevos, se almacenarian.
        :param convocatoria convocatoria que se quiere recomendar
        :return lista de investigadores con y sin solicitud
        """
        df_inv_interno = rsController.get_investigador_interno()
        if len(df_inv_interno) > 0:
            del df_inv_interno['id']
            del df_inv_interno['perfil']
        self.update_log(
            "Obtenemos los investigadores internos, total: "+str(len(df_inv_interno)), True)
        df_inv_edma = rsController.get_investigadores_ed()
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
                rsController.insert_investigadores(df_new_invs)
        elif len(df_inv_edma) == 0 and len(df_inv_interno) > 0:
            df_investigadores = df_inv_interno
        else:
            df_investigadores = df_inv_edma
            rsController.insert_investigadores(df_investigadores)
        # quitamos aquellos que ya han mandado la solicitud
        solicitudes = self.__get_solicitudes(convocatoria.id)
        if len(solicitudes) > 0:
            investigadores_con_solicitud = self.__drop_solicitudes(solicitudes)
            df_new_invs = investigadores_con_solicitud[~investigadores_con_solicitud['email'].isin(
                df_investigadores['email'])]
            if len(df_new_invs) > 0:  # Añadimos nuevos investigadores detectados
                self.update_log(
                    "En la solicitud del SGI se han encontrado investigadores que no estan ni en la BBDD interna ni en EDMA. Se proceden a insertar en la base de datos interna", True)
                rsController.insert_investigadores(df_new_invs)
            df_investigadores = df_investigadores[~df_investigadores.email.isin(
                investigadores_con_solicitud.email)]
            
        investigadores_listado_sin_solicitud = []
        investigadores_listado_con_solicitud = []

        for _, inv in df_investigadores.iterrows():
            #Si ya hemos notificado la convocatoria no lo volveremos a hacer
            inv_a_notificar = rsController.get_notificacion_interna(
                inv['email'], convocatoria)
            if inv_a_notificar and inv_a_notificar.is_config_perfil:
                rsController.cargar_perfil(inv_a_notificar) #Cargamos el perfil de las puntuaciones, si ya lo tuviera configurado no es necesario
                investigadores_listado_sin_solicitud.append(inv_a_notificar)

        for _, inv in investigadores_con_solicitud.iterrows():
            #Si ya hemos notificado la convocatoria no lo volveremos a hacer
            inv_a_notificar = rsController.get_notificacion_interna(
                inv['email'], convocatoria)
            if inv_a_notificar:
                investigadores_listado_con_solicitud.append(inv_a_notificar)
        
        self.update_log("Total de investigadores que NO han hecho la solicitud " +
                        str(len(investigadores_listado_sin_solicitud)), True)
        self.update_log("Total de investigadores que SI han hecho la solicitud " +
                        str(len(investigadores_listado_con_solicitud)), True)
        return investigadores_listado_sin_solicitud, investigadores_listado_con_solicitud

    def generar_correo(self, convocatoria: p4.Convocatoria, investigador: p4.Investigador):
        """
        Método para notificar por email la convocatoria.
        :param convocatoria convocatoria que se quiere recomendar
        :param investigador investigador a notificar
        :return bool si ha podido completarlo o no
        """
        token = rsController.generate_token(investigador.id, controllerRobot.robot.id, controllerRobot.robot.token)
        if not token:
            self.update_log(
                "No se pudo generar el token. No se puede enviar el correo al investigador "+investigador.nombre, True)
            return False

        sgi = cs.get_sgi(self.ip_api, self.port_api)
        convocatoria_base = json.loads(sgi.get_call(convocatoria.id))
        convocatoria_entidad_convo = sgi.get_conveners_call(
            convocatoria.id)
        convocatorias_entidad_finan = sgi.get_financing_entity_call(
            convocatoria.id)

        if convocatoria_entidad_convo and len(convocatoria_entidad_convo) > 0:
            convocatoria_entidad_convo = json.loads(
                convocatoria_entidad_convo)[0]

        if convocatorias_entidad_finan and len(convocatorias_entidad_finan) > 0:
            convocatorias_entidad_finan = json.loads(
                convocatorias_entidad_finan)
        
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
        url_sgi = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><a href="""+sgi.host + URL_SGI + \
            str(convocatoria.id) + '/datos-generales' + \
            """ style="color:#ee4c50;text-decoration:underline;">Enlace a la convocatoria</a></p>"""
        interes_conv = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>**¿Te ha resultado de interés esta convocatoria? </b> <a href="""+controllerRobot.robot.frontend+URL_FEEDBACK+token+"/" + \
            str(convocatoria.id)+"/si"+""" style="color:#ee4c50;text-decoration:underline;">Sí</a> / <a href="""+controllerRobot.robot.frontend+URL_FEEDBACK+ \
            token+"/"+str(convocatoria.id)+"/no" + \
            """ style="color:#ee4c50;text-decoration:underline;">No</a></p>"""
        url_perfil = """<tr><td><p style="margin-top:50px;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">Puedes obtener convocatorias más personalizadas configurando su perfil. </p>
                        <p style="margin-top:1px;font-size:16px;font-family:Arial,sans-serif;"><a href="""+controllerRobot.robot.frontend+URL_PROFILE+token+""" style="color:#ee4c50;text-decoration:underline;">Configurar mi perfil</a></p><p style="margin-top:30px;margin-bottom:5px;font-size:12px;line-height:24px;font-family:Arial,sans-serif;">**No comparta ningún enlance, son exclusivos para cada investigador.**</p></td></tr>"""

        html_body_convocatoria = []
        if convocatoria_entidad_convo:
            if convocatoria_entidad_convo['programa']:
                if sgi.get_company(convocatoria_entidad_convo['entidadRef']):
                    empresa_nombre = json.loads(sgi.get_company(
                        convocatoria_entidad_convo['entidadRef']))['nombre']
                else:
                    empresa_nombre = ""

                html_entidad_convo = """<p style="margin:20;font-size:16px;line-height:24px;font-family:Arial,sans-serif;"><b>Entidad Convocante:</b>"""+empresa_nombre+""" </p>"""
                html_body_convocatoria.append(html_entidad_convo)
                
        for convocatoria_entidad_finan in convocatorias_entidad_finan:
            if convocatoria_entidad_finan:
                if sgi.get_company(convocatoria_entidad_finan['entidadRef']):
                    empresa_nombre = json.loads(sgi.get_company(
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
                                <p style="margin:0 0 12px 0;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">En el SGI hay una convocatoria disponible, puede que sea de su interés.</p>
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
        utils = UtilsProcess(self.log.id_schedule, self.log.id, self.id_robot, self.priority, self.log.log_file_path)
        state = utils.send_email_html([{"receiver":investigador.email}], body, 'Convocatoria SGI', process=self)
        if state == "ERROR":
            self.update_log("No se pudo enviar el correo al investigador"+investigador.email, True)
            self.log.state = "ERROR"
            self.log.completed = 100
            return False

        if not rsController.post_notificacion(investigador, convocatoria):
            self.update_log("Error al insertar la notificación del investigador " +
                            investigador.nombre+" con ID "+str(investigador.id), True)
        return True

    def notificacion(self, convocatoria, investigadores, threshold_score=0.4):
        """
        Método que decide si una convocatoria se notifica o no.
        :param convocatoria convocatoria que se quiere recomendar
        :param investigador investigador a notificar
        :param threshold_score parametro que decide si se notifica o no la convocatoria
        :return bool si ha podido completarlo o no
        """
        self.update_log("Notificamos la convocatoria " +
                        convocatoria.titulo, True)
        for idInv, puntuacion in investigadores.items():
            if puntuacion > threshold_score:
                investigador = rsController.get_investigador_interno(idInv)
                self.update_log("Notificamos al investigador "+ investigador.email + " de la convocatoria "+
                        convocatoria.titulo, True)
                if not self.generar_correo(convocatoria, investigador):
                    return False
        return True

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
