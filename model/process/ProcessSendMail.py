from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

VERSION         = "1.0"
NAME            = "Send Mail"
DESCRIPTION     = "Proceso para enviar correo a uno o varios destinatarios"
REQUIREMENTS    = []
ID              = ProcessID.SEND_MAIL.value

class ProcessSendMail(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)
        
    def execute(self):
        """
        Método encargado de la construcción y envío del correo electrónico
        """
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.log.state = "OK"

        if not self.parameters:
            self.update_log("No se han establecido parámetros", True)
            self.log.state = "ERROR"
            self.log.end_log(time.time())
            self.state = pstatus.FINISHED
            return 

        smtp_server = self.parameters['smtp_server']

        try:
            mime_subtype = self.parameters['mime_subtype']
        except:
            mime_subtype = 'plain'

        try:
            port = self.parameters['port']
        except:
            port = 465

        completed_aux = 100/len(self.parameters['receivers'])
        for mail in self.parameters['receivers']:
            sender = mail['sender']
            receiver = mail['receiver']
            subject = mail['subject']
            body = mail['body']
            attached = mail['attached']
            msg =  self.create_message(sender,receiver,subject,body, mime_subtype,attached)
            self.update_log("Se ha creado el email para "+receiver+" desde "+sender+" con el contenido :"+ body+" y adjuntos : "+ ' '.join(attached if attached is not None else "[]"),True)
            try:
                if port == 465:
                    sender_email = self.parameters['user']
                    password = self.parameters['password']
                    server = smtplib.SMTP_SSL(smtp_server, port)
                    server.login(sender_email, password)
                else:
                    server = smtplib.SMTP(smtp_server, port)
                server.sendmail(sender, receiver, msg.as_string())
            except:
                self.update_log("Sending error: No se ha podido enviar el email a "+receiver+" desde "+sender+" con el contenido :"+ body+" y adjuntos : "+ ' '.join(attached if attached is not None else "[]"),True)
            else:
                self.log.completed += completed_aux
                self.update_log("Se ha enviado el email a "+receiver+" desde "+sender+" con el contenido :"+ body+" y adjuntos : "+ ' '.join(attached if attached is not None else "[]"),True)

                self.log.completed = 100
                self.log.end_log(time.time())
                self.state = pstatus.FINISHED

    def create_message(self,sender,receiver,subject,body,subtype, attached = None):
        """
        Método encargado de crear el mensaje 
        :param sender dirección de email que envía el correo
        :param receiver destinatarios
        :param subject asunto
        :param body cuerpo del mensaje
        :param subtype tipo que se utiliza para que el cuerpo del mensaje sea HTML
        :param attached adjuntos
        :return MIMEMultipart devuelve un objeto de tipo MIMEMultipart
        """
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = receiver
        message["Subject"] = subject
        message["Bcc"] = receiver # Recommended for mass emails
        message.attach(MIMEText(body, subtype))

        if (attached is not None):
            for att in attached:
                self.attach_file(att,message)

        return message


    def attach_file(self,filename,message):
        """
        Método para adjuntar ficheros a un mensaje
        :param filename ruta del fichero
        :param message mensaje en el que se adjunta el fichero
        """
        self.update_log("Se ha adjuntado al correo el documento "+filename,True)
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        # Add attachment to message and convert message to string
        message.attach(part)


    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass