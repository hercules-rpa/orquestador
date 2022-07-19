import model.process.Proceso4.SRControlador as SRControlador
import pandas as pd
import time
from model.process.ProcessSendMail import ProcessSendMail
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID




NAME = "Recordatorio Perfil"
DESCRIPTION = "Proceso que manda un correo electrónico recordatorio para que los investigadores configuren su perfil"
REQUIREMENTS = ['pandas']
ID = ProcessID.RECOMMENDATION.value
URL_API = "http://10.208.99.12:8080/#/p/profilerecommendation/"


class ProcessRecordatorioPerfil(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)
        
    
    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.update_log("Proceso de recordatorio perfil ha empezado", True)
        self.log.completed = 0
        self.result = None
        
        df_investigadores = SRControlador.get_investigador_interno()
        if len(df_investigadores) > 0:
            df_investigadores = df_investigadores[df_investigadores['perfil'] != True ]
            tam = len(df_investigadores)
            for _, inv in df_investigadores.iterrows():
                self.log.completed += 100/tam
                self.update_log("Mandamos correo para que configure su perfil al investigador: "+inv['email'], True)
                self.send_mail(inv['id'],inv['nombre'],inv['email'])
        
        self.update_log("Proceso finalizado correctamente. ", True)
        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED
            
    def send_mail(self, id, nombre, email):
        if email!="josemanuel.bernabe@um.es":
            return
        token = SRControlador.generate_token(id)
        print("Mandamos correo a "+email)
        hola_investigador = """<p style="margin:0 0 12px 0;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">Hola """ + \
            nombre+""",</p>"""
        url_perfil = """
                        <p style="margin-top:1px;font-size:16px;font-family:Arial,sans-serif;"><a href="""+URL_API+token+""" style="color:#ee4c50;text-decoration:underline;">Configurar mi perfil</a></p><tr><td><p style="margin-top:30px;margin-bottom:5px;font-size:12px;line-height:24px;font-family:Arial,sans-serif;">**No comparta ningún enlance, son exclusivos para cada investigador.**</p></td></tr>"""
                        
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
                                <p style="margin:0 0 12px 0;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">Le recordamos que puede configurar su perfil para recibir convocatorias personalizadas que esten disponibles en el SGI.</p>
                            </td>
                            </tr>

                            <tr>
                            <td style="padding:0 0 36px 0;color:#153643;  border: 0px solid black; background:#F8F7EA;">
                                <h1 style="font-size:26px;margin:0 0 20px 0;font-family:Arial,sans-serif;"> Configurar Perfil</h1>"""+url_perfil+"""   
                            </td>
                            </tr>
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
        # user["receiver"] = email
        # user["subject"] = "Convocatoria SGI"
        # user["body"] = body
        # user["attached"] = []
        # params["receivers"].append(user)
        # psm = ProcessSendMail(self.log.id_schedule,
        #                       self.log.id, self.id_robot, "1", None, params)
        # psm.add_data_listener(self)
        # psm.execute()
        # if psm.log.state == "ERROR":
        #     self.update_log("No se pudo enviar el correo al investigador"+email, True)
        #     self.log.state = "ERROR"
        #     self.log.completed = 100
        #     return False

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass