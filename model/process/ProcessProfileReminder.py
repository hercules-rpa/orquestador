import time
from model.process.UtilsProcess import UtilsProcess
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from rpa_robot.ControllerRobot import ControllerRobot
from model.process.Process4.RSController import RSController
import pandas as pd

NAME = "Recordatorio Perfil"
DESCRIPTION = "Proceso que manda un correo electrónico recordatorio para que los investigadores configuren su perfil"
REQUIREMENTS = ['pandas']
ID = ProcessID.RECOMMENDATION.value
URL_PROFILE = "/#/p/profilerecommendation/"

class ProcessProfileReminder(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None, ip_api = None, port_api = None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)
        
    
    def execute(self):
        global rsController
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.update_log("Proceso de recordatorio perfil ha empezado", True)
        self.log.completed = 0
        self.result = None
        rsController = RSController(self.ip_api, self.port_api)
        df_investigadores = rsController.get_investigador_interno()
        test_email = self.parameters['test_email']

        if len(test_email) > 0 and len(test_email[0]) > 0:
            for email in test_email:
                email = email['receiver']
                data = {'nombre': ["Jane Doe"], "email":[email]}
                df_inv = pd.DataFrame(data)
                rsController.insert_investigadores(df_inv)
                inv = rsController.get_investigador_email(email)
                self.send_mail(inv.id, inv.nombre, inv.email)


        elif len(df_investigadores) > 0:
            df_investigadores = df_investigadores[df_investigadores['perfil'] != True ]
            tam = len(df_investigadores)
            for _, inv in df_investigadores.iterrows():
                self.log.completed += 100/tam
                self.update_log("Mandamos correo para que configure su perfil al investigador: "+inv['email'], True)
                self.send_mail(inv['id'],inv['nombre'],inv['email'])
                
        self.log.completed = 100
        self.state = pstatus.FINISHED
        if self.log.state == "ERROR":
            return
        else:
            self.update_log("Proceso finalizado correctamente. ", True)
        self.log.end_log(time.time())
        
            
    def send_mail(self, id, nombre, email):
        controllerRobot = ControllerRobot()
        token = rsController.generate_token(id, controllerRobot.robot.id, controllerRobot.robot.token)
        if not token:
            self.update_log(
                "No se pudo generar el token. No se puede enviar el correo al investigador "+investigador.nombre, True)
            return False

        hola_investigador = """<p style="margin:0 0 12px 0;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">Hola """ + \
            nombre+""",</p>"""
        url_perfil = """
                        <p style="margin-top:1px;font-size:16px;font-family:Arial,sans-serif;"><a href="""+controllerRobot.robot.frontend+URL_PROFILE+token+""" style="color:#ee4c50;text-decoration:underline;">Configurar mi perfil</a></p><tr><td><p style="margin-top:30px;margin-bottom:5px;font-size:12px;line-height:24px;font-family:Arial,sans-serif;">**No comparta ningún enlance, son exclusivos para cada investigador.**</p></td></tr>"""
                        
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
        utils = UtilsProcess(self.log.id_schedule, self.log.id, self.id_robot, self.priority, self.log.log_file_path)
        state = utils.send_email_html([{"receiver":email}], body,"Configuración de perfil para el envío de convocatorias", process=self)

        if state == "ERROR":
            self.notify_update("No se pudo enviar el correo al investigador "+email)
            self.log.state = "ERROR"

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass