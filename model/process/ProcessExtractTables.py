from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessSendMail import ProcessSendMail
from model.process.ProcessDownload import ProcessDownload
import time
from tabula import read_pdf #pip install tabula-py
import pandas as pd
#IMPORTANTE sudo apt-get install -y icedtea-netx

NAME            = "Extract tables" 
DESCRIPTION     = "Proceso para extraer tablas y generar un excel a partir de un documento pdf"
REQUIREMENTS    = ['tabula','tabula-py','pandas','openpyxl']
ID              = ProcessID.EXTRACT_TABLES.value
DIRECTORY_FILES = "rpa_robot/files/"

class ProcessExtractTables(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)
        
    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())

        self.update_log("Proceso de extracción de tablas PDF ha empezado",True)
        self.log.completed = 10
        filename = self.parameters['file'][0]['name']
        fileformat = self.parameters['file'][0]['format']
        params_download = {}
        params_download['URL'] = [self.parameters['files'][0]['URL']]
        file_return_excel = 'extracttables2.xlsx'
        emails_address = self.parameters['receivers']
        psd = ProcessDownload(self.log.id_schedule, self.log.id,self.id_robot, "1", None, params_download)
        psd.add_data_listener(self)
        psd.execute()
        '''if psd.log.state == "ERROR":
            self.update_log("Error descargando el fichero", True)
            self.log.state = "ERROR"
            self.log.completed = 100
            end_time = time.time()
            self.log.end_log(end_time)
            return 
        '''

        try:
            print(DIRECTORY_FILES+filename+'.'+fileformat)
            self.update_log("Se procede a extraer las tablas del documento",True)
            df = self.read_doc(DIRECTORY_FILES+filename+'.'+fileformat)
            df.to_excel(file_return_excel, index = False)
            self.update_log("DataFrame guardado en formato Excel",True)

        except Exception as exc:
            print(exc)
            self.update_log("Error al convertir a tablas en excel",True)
            self.log.state = "ERROR"
            self.log.completed = 100
            self.log.end_log(time.time())
            self.state = pstatus.FINISHED
            #remove(DIRECTORY_FILES+filename+'.'+fileformat)
            return
                
        self.update_log("Tablas extraidas se procede a enviar correo a los destinatarios",True)
        self.log.completed = 60
         
        params_mail = {}
        params_mail["user"] = "epictesting21@gmail.com"
        params_mail["password"] = "epicrobot"
        params_mail["smtp_server"] = "smtp.gmail.com"
        params_mail["receivers"]= []
        for r in emails_address:
            user={}
            user["sender"] = "epictesting21@gmail.com"
            user["receiver"]= r['receiver']
            user["subject"]="Extracción de tablas del fichero "+filename
            user["body"]= "Email enviado con python Robot masivamente"
            user["attached"]= [file_return_excel]
            params_mail["receivers"].append(user)

        psm = ProcessSendMail(self.log.id_schedule, self.log.id, self.id_robot, "1", None, params_mail)
        psm.add_data_listener(self)
        psm.execute()

        if psm.log.state == "ERROR":
            self.log.state = "ERROR"
            self.update_log("El proceso ProcessSendMail terminó con error ",True)

        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED
        #remove(DIRECTORY_FILES+filename+'.'+fileformat)
        #remove(file_return_excel)
        



    def read_doc(self,doc):

        pdf_list = read_pdf(doc, multiple_tables=False, lattice=True, pages = 'all', pandas_options={'header':None})
        df_all = []
        df = None
        if len(pdf_list) > 0:
            self.update_log('DataFrames extraídas: %s'% len(pdf_list),True)
            for pdf in pdf_list:
                pdf.columns = ['Tipo', 'Concepto Factura', 'No.Factura', 'Gasto', 'Pago', 'Imputado', 'Cif Proveedor', 'Proveedor']
                pdf = pdf.fillna('')

                for column in pdf.columns:
                    pdf[column] = pdf[column].apply(lambda x: str(x).replace('\r', ' '))
                df_all.append(pdf)
            df = pd.concat(df_all, ignore_index=False)
            self.update_log('DataFrame final: %s filas' % len(df),True)

        else:
            print('No se ha podido detectar tablas en el documento')
            self.update_log("No se ha podido detectar tablas en el documento",True)
            self.log.state = "ERROR"

        return df


    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass
