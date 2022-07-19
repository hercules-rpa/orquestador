from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessSendMail import ProcessSendMail
import Utils as Utils
from model.Log import Log

import time
import asyncio
import json
from tabula import read_pdf
from os.path import join, dirname, basename
from os import remove
import pandas as pd

NAME            = "Extract tables" 
DESCRIPTION     = "Proceso para extraer tablas y generar un excel a partir de un documento pdf"
REQUIREMENTS    = ['tabula','pandas']
ID              = ProcessID.EXTRACT_TABLES.value
class ProcessExtractTables(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)
        
    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())

        self.update_log("Proceso de extracción de tablas PDF ha empezado",True)
        self.log.completed = 10

        filename = 'requerimientodocumental.pdf'
        excel_file = 'extract_tables.xlsx'
        mail_address = 'eduardo.canovas1@um.es'
        try:
            self.update_log("Se procede a extraer las tablas del documento",True)
            df = self.read_doc(filename)
            df.to_excel(excel_file, index = False)
            self.update_log("DataFrame guardado en formato Excel",True)
            #send_mail(excel_name, mail_address)

            with open('mailtables.json') as f:
                params_mail = json.load(f)
        except Exception as exc:
            self.update_log("No se ha encontrado alguno de estos ficheros, requerimientodocumental.pdf, extract_tables.xlsx y mailtables.json",True)
            self.log.state = "ERROR"
            self.log.completed = 100
            self.log.end_log(time.time())
            self.state = pstatus.FINISHED
            return
                
        self.update_log("Tablas extraidas se procede a enviar correo a los destinatarios",True)
        self.log.completed = 60
        try: 
            psm = ProcessSendMail(self.log.id_schedule, self.log.id, self.id_robot, "1", None, params_mail)
            psm.add_data_listener(self)
            psm.execute()
        except:
            self.update_log("Ocurrio un problema con el proceso sendmail",True)
            self.log.state = "ERROR"
            self.log.completed = 100
            self.log.end_log(time.time())
            self.state = pstatus.FINISHED
            return

        self.update_log("Enviando el fichero excel por correo a "+mail_address,True)



        if psm.log.state == "ERROR":
            self.log.state = "ERROR"
            self.update_log("El proceso ProcessSendMail terminó con error "+mail_address,True)

        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED




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