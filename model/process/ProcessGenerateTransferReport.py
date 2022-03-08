import time
from datetime import datetime

from sqlalchemy import true
from model.process.ProcessExtractNews import ProcessExtractNews
from model.process.ProcessSendMail import ProcessSendMail
from model.process.ProcessCommand import ProcessCommand, ProcessID, Pstatus

NAME = "Process Generate Transfer Report"
DESCRIPTION = "Proceso que genera un informe para el boletín de transferencia."
REQUIREMENTS = []
ID = ProcessID.GENERATETRANSFERREPORT.value

class ProcessGenerateTransferReport(ProcessCommand):

    URL_NEWS = "http://10.208.99.12:5000/api/orchestrator/register/noticia"
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, DESCRIPTION, REQUIREMENTS,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def enviar_email(self, emails, body, subject):
        params = {}
        params["user"] = "epictesting21@gmail.com"
        params["password"] = "epicrobot"
        params["smtp_server"] = "smtp.gmail.com"
        params["receivers"] = []
        for r in emails:
            user = {}
            user["sender"] = "epictesting21@gmail.com"
            user["receiver"] = r['receiver']
            user["subject"] = subject
            user["body"] = body
            user["attached"] = []
            params["receivers"].append(user)
        
        psm = ProcessSendMail(self.log.id_schedule,
                              self.log.id, self.id_robot, "1", None, params)
        psm.add_data_listener(self)
        psm.execute()
        return psm.log.state                

    def execute(self):
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0
        self.notificar_actualizacion("El proceso de generación del informe del boletín de transferencia ha comenzado.")

        msg:str = ''

        try:
            start_date = self.parameters['start_date']
            if not start_date:
                start_date = self.formatear_fecha(datetime.today())
        except:
            start_date = self.formatear_fecha(datetime.today())

        try:
            end_date = self.parameters['end_date']
            if not end_date:
                end_date = self.formatear_fecha(datetime.today())
        except:
            end_date = self.formatear_fecha(datetime.today())

        try:
            receivers = self.parameters['receivers']
        except:
            self.notificar_actualizacion('ERROR: para ejecutar el proceso debe indicar destinatarios.')
            self.log.state = "ERROR"
        
        if receivers:

            params = {}
            params["start_date"] = start_date
            params["end_date"] = end_date
            try:
                pextractnews = ProcessExtractNews(self.log.id_schedule,
                                        self.log.id, self.id_robot, "1", None, params)
                pextractnews.add_data_listener(self)
                pextractnews.execute()
                news = pextractnews.result
            except:
                self.notificar_actualizacion("Error al obtener las noticias.")
                self.log.state = "ERROR"
                news = []

            if news:
                num = len(news)
                if num > 1:
                    msg += 'Se han obtenido ' + str(num) + ' noticias.' + '\n'
                else:
                    msg += 'Se ha obtenido 1 noticia. \n'
                
                cont = 1
                for new in news:
                    msg += 'NOTICIA ' + str(cont) + ': \n' 
                    msg += 'Título: ' + new.title + '\n'
                    msg += 'Autor: ' + new.author + '\n'
                    msg += 'Fecha: ' + new.date + '\n'
                    msg += 'Url: ' + new.url + '\n'
                    cont += 1
                
            if msg:
                state = self.enviar_email(receivers, msg, "RPA: Infome boletín de transferencia.")
                print(str(state))
                if state == "ERROR":
                    self.log.state = "ERROR"
                else:
                    #actualizar news
                    self.update_element(news,self.URL_NEWS, True)
                        

        self.log.completed = 100
        self.notificar_actualizacion("El proceso de generación del informe del boletín de transferencia ha finalizado.")
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED


    def kill(self):
        pass

    def pause(self):
        pass
    def resume(self):
        pass
