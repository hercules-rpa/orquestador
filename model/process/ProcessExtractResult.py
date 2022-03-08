from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessSendMail import ProcessSendMail
from model.process.ProcessDownload import ProcessDownload
import Utils as Utils
from model.Log import Log

import time
import asyncio
import json
from urllib.parse import _DefragResultBase
from urllib.request import install_opener
from tabula import read_pdf #pip install tabula-py
from os.path import join, dirname, basename
from os import remove
from RPA.PDF import PDF
import pandas as pd
import numpy as np
#IMPORTANTE sudo apt-get install -y icedtea-netx
#pip install openpyxl
#pip install xlsxwriter

NAME            = "Extract Resultado Convocatoria" 
DESCRIPTION     = "Proceso para extraer los resultados de la convocatoria por NIF"
REQUIREMENTS    = ['tabula','tabula-py','pandas', 'openpyxl','xlsxwriter']
ID              = ProcessID.EXTRACT_TABLES.value
DIRECTORY_FILES = "rpa_robot/files/"


STRING_PRETERM      = 'RELACIÓN DE AYUDAS PROPUESTAS PARA FINANCIACIÓN - '
DATOS_GENERALES     = STRING_PRETERM+'DATOS GENERALES'
DATOS_ECONOMICOS    = STRING_PRETERM+'DATOS ECONÓMICOS'
DESESTIMADAS        = 'RELACIÓN DE AYUDAS DESESTIMADAS'
ACTUALIZADA         = 'RELACIÓN DE ENTIDADES A LAS QUE SE REQUIERE DOCUMENTACIÓN ACTUALIZADA'
KEY_TERMS = [DATOS_GENERALES,DATOS_ECONOMICOS,DESESTIMADAS,ACTUALIZADA]

class ProcessExtractResult(ProcessCommand):
    

    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)

        
    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())

        self.update_log("Proceso de extracción de resultado convocatoria ha empezado",True)
        self.log.completed = 10
        filename = self.parameters['files'][0]['name']
        fileformat = self.parameters['files'][0]['format']
        params_download = {}
        params_download['URL'] = [self.parameters['files'][0]['URL']]
        nifs = self.parameters['NIFs']
        documentos = []
        emails_address = self.parameters['receivers']
        if not isinstance(nifs, list):
            self.update_log("Error parametro NIFS no es un Array", True)
            self.log.state = "ERROR"
            self.log.completed = 100
            end_time = time.time()
            self.log.end_log(end_time)
            return

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

        for nif in nifs:
            print(nif)
            #try:
            self.update_log("Se procede a extraer las tablas del documento del NIF: "+nif['nif'],True)
            self.log.completed += 80/len(nifs)
            dfs_dict = self.read_doc(DIRECTORY_FILES+filename+'.'+fileformat, nif['nif'])
            documentos.append(self.export_excel(nif['nif'], dfs_dict))
            '''except Exception as e:
                self.update_log("Error extrayendo las tablas en el documento", True)
                self.update_log(e.message, True)
                self.log.state = "ERROR"
                self.log.completed = 100
                end_time = time.time()
                self.log.end_log(end_time)
                print(e.message, e.args)
                return 
            '''

        #ENVIAMOS EL RESULTADO POR CORREO
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
            user["attached"]= documentos
            params_mail["receivers"].append(user)

        psm = ProcessSendMail(self.log.id_schedule, self.log.id, self.id_robot, "1", None, params_mail)
        psm.add_data_listener(self)
        psm.execute()

        if psm.log.state == "ERROR":
            self.log.state = "ERROR"
            self.update_log("El proceso ProcessSendMail terminó con error ",True)

        self.log.completed = 100
        print("La extracción de resultado ha terminado")
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = pstatus.FINISHED
        
    def export_excel(self, name_export, dfs_dict):
        self.update_log("Se procede a dar formato al archivo "+name_export,True)
        #SE EMPIEZA EN LA COLUMNA 0, que posteriormente se vacíara porque al exportar usa la primera columna como indice y no lo queremos, en multiindex no se puede hacer
        #index=false por lo que se vacía de forma "manual"
        writer = pd.ExcelWriter("resolucion_"+name_export+".xlsx", engine="xlsxwriter")
        workbook = writer.book
        startrow = 2
        startwor_deses = 2
        startcol = 0
        format_header = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'border': 2,
            'border_color':'#538DD5',
            'fg_color': '#4f81bd',
            'align': 'center',
            'valign': 'center'}) 

        format_colors = [workbook.add_format({
            'text_wrap': True,
            'border': 2,
            'border_color':'#538DD5',
            'fg_color': '#c5d9f1',
            'align': 'center',
            'valign': 'center'}), 
            workbook.add_format({
            'text_wrap': True,
            'border': 2,
            'border_color':'#538DD5',
            'fg_color': '#ffffff',
            'align': 'center',
            'valign': 'center'})]

        for key, df in dfs_dict.items():
            if key == DATOS_GENERALES:
                df.to_excel(writer,sheet_name="Resultado",startrow=startrow, startcol=startcol)
                worksheet_result = writer.sheets['Resultado']
                df = df.rename(columns={'No':'Nº'})
                fila = 0
                color_index = 0
                #PONEMOS EL FORMATO EN LOS DIFERENTES DATOS QUE TENEMOS, COLOR ALTERNATIVO PARA CADA FILA, ETC..
                for f in range(startrow+1, startrow+1+df.shape[0]):
                    columna = 0
                    for c in range(startcol+1, startcol+df.shape[1]+1):
                        value = str(df.iloc[fila,columna]).replace("\r", " ")
                        worksheet_result.write(f,c, value, format_colors[color_index])
                        columna = columna +1
                    fila = fila +1
                    color_index = (color_index+1)%2
                #Añadimos background color al header
                for col_num, value in enumerate(df.columns.values):
                    worksheet_result.write(startrow, col_num+1, value, format_header)
                
                #Eliminamos la columna indice, noexiste otra forma de hacerlo
                for c in range(startrow, startrow + df.shape[0]+10):
                    worksheet_result.write(c,0,' ')
                worksheet_result.set_column('A:I',20)

                
            if key == DATOS_ECONOMICOS:
                df.to_excel(writer,sheet_name="Resultado",startrow=startrow, startcol=startcol)
                worksheet_result = writer.sheets['Resultado']
                df = df.rename(columns={'No':'Nº'})
                fila = 0
                color_index = 0
                #PONEMOS EL FORMATO EN LOS DIFERENTES DATOS QUE TENEMOS, COLOR ALTERNATIVO PARA CADA FILA, ETC..
                for f in range(startrow+3, startrow+3+df.shape[0]):
                    columna = 0
                    for c in range(startcol+1, startcol+df.shape[1]+1):
                        value = str(df.iloc[fila,columna]).replace("\r", " ")
                        worksheet_result.write(f,c,value, format_colors[color_index])
                        columna = columna + 1
                    color_index = (color_index + 1) % 2
                    fila = fila + 1

                worksheet_result.merge_range(startrow, 1, startrow+2, 1, 'Nº', format_header)
                worksheet_result.merge_range(startrow, 2, startrow+2, 2, 'REFERENCIA', format_header)
                worksheet_result.merge_range(startrow+1, 3, startrow+2, 3, 'PRESUPUESTO TOTAL CONCEDIDO', format_header)
                for c in range(df.shape[1]+1):
                    worksheet_result.write(startrow+3+df.shape[0],c,' ')

                for col_num, value in enumerate(df.columns.values):
                    worksheet_result.write(startrow, col_num+1, value[0], format_header)
                    worksheet_result.write(startrow+1, col_num+1, value[1], format_header)
                    worksheet_result.write(startrow+2, col_num+1, value[2], format_header)
                

                #Eliminamos la columna indice, noexiste otra forma de hacerlo
                for c in range(startrow, startrow + df.shape[0]+10):
                    worksheet_result.write(c,0,' ')
                worksheet_result.set_column('A:I',20)

                startrow = startrow + 3

            if key == ACTUALIZADA:
                df.to_excel(writer,sheet_name="Resultado",startrow=startrow, startcol=startcol)
                worksheet_result = writer.sheets['Resultado']
                df = df.rename(columns={'No':'Nº'})
                fila = 0
                color_index = 0
                #PONEMOS EL FORMATO EN LOS DIFERENTES DATOS QUE TENEMOS, COLOR ALTERNATIVO PARA CADA FILA, ETC..
                for f in range(startrow+1, startrow+1+df.shape[0]):
                    columna = 0
                    for c in range(startcol+1, startcol+df.shape[1]+1):
                        value = str(df.iloc[fila,columna]).replace("\r", " ")
                        worksheet_result.write(f,c,value, format_colors[color_index])
                        columna = columna +1
                    fila = fila +1
                    color_index = (color_index+1)%2
                #Añadimos background color al header
                for col_num, value in enumerate(df.columns.values):
                    worksheet_result.write(startrow, col_num+1, value, format_header)
                
                #Eliminamos la columna indice, noexiste otra forma de hacerlo
                for c in range(startrow, startrow + df.shape[0]+10):
                    worksheet_result.write(c,0,' ')
                worksheet_result.set_column('A:I',20)


            if key == DESESTIMADAS:
                
                df.to_excel(writer,sheet_name="Desestimada",startrow=startwor_deses, startcol=0)
                worksheet_desestimada = writer.sheets['Desestimada']
                df = df.rename(columns={'No':'Nº'})
                fila = 0
                color_index = 0
                #PONEMOS EL FORMATO EN LOS DIFERENTES DATOS QUE TENEMOS, COLOR ALTERNATIVO PARA CADA FILA, ETC..
                for f in range(startwor_deses+1, startwor_deses+1+df.shape[0]):
                    columna = 0
                    for c in range(startcol+1, startcol+df.shape[1]+1):
                        value = str(df.iloc[fila,columna]).replace("\r", " ")
                        worksheet_desestimada.write(f,c,value, format_colors[color_index])
                        columna = columna +1
                    fila = fila +1
                    color_index = (color_index+1)%2
                #Añadimos background color al header
                for col_num, value in enumerate(df.columns.values):
                    worksheet_desestimada.write(startwor_deses, col_num+1, value, format_header)
            
                #Eliminamos la columna indice, noexiste otra forma de hacerlo
                for c in range(startwor_deses, startwor_deses + df.shape[0]+10):
                    worksheet_desestimada.write(c,0,' ')
                worksheet_desestimada.set_column('A:I',20)
                startwor_deses = startwor_deses + df.shape[0] + 2


            #DESPLAZAMOS EL STARTROW PARA QUE NO HAYA SOLAPAMIENTO
            startrow = startrow + df.shape[0]+3
            startcol = 0
            
        writer.save()
        return "resolucion_"+name_export+".xlsx"



    def read_doc(self,doc,nif):
        pdf_preload = PDF()
        global KEY_TERMS, STRING_PRETERM
        text = pdf_preload.get_text_from_pdf(doc)
        dict_tables = {}
        for term in KEY_TERMS:
            pages = []
            for (key, value) in text.items():
                if term in value:
                    pages.append(key)
            dict_tables[term] = pages
         
        df_all = {}
        referencias = []

        for key, page in dict_tables.items():
            pdf_list = read_pdf(doc, multiple_tables=True, lattice=True, pages = page)
            for pdf in pdf_list:
                pdf = pdf.fillna('')
                #Eliminamos retornos de carro de windows, nos daría problemas en linux
                pdf.columns = pdf.columns.str.replace("\r", " ")

                if key == DATOS_GENERALES:
                    
                    pdf_filter = pdf.loc[pdf['NIF'] == nif]
                    if len(pdf_filter)>0:
                        referencias.append(pdf_filter['REFERENCIA'])
                        if not key in df_all:
                            dataframe_header = pdf_filter
                            
                        else:
                            dataframe_header = df_all[key]
                            dataframe_header = pd.concat([dataframe_header, pdf_filter])

                        df_all[key] = dataframe_header

                elif key == DESESTIMADAS:
                    pdf_filter = pdf.loc[pdf['NIF'] == nif]
                    if len(pdf_filter)>0:
                        if not key in df_all:
                            dataframe_header = pdf_filter
                            
                        else:
                            dataframe_header = df_all[key]
                            dataframe_header = pd.concat([dataframe_header, pdf_filter])

                        df_all[key] = dataframe_header
                
                elif key == ACTUALIZADA:
                    for r in referencias:
                        pdf_filter = pdf.loc[pdf['REFERENCIA'].isin(r.values)]
                        if len(pdf_filter) > 0:
                            if key in df_all:
                                df_all[key] = pd.concat([df_all[key], pdf])
                            else:
                                df_all[key] = pdf_filter
                        
                elif key == DATOS_ECONOMICOS:
                    #Depende de la pagina se mueve el nombre de la columna, hardcode hasta encontrar la solucion
                    if pdf.iloc[1,7] != '':
                        value_year = pdf.iloc[1,7]
                        value_last_year = pdf.iloc[1,9]
                    else:
                        value_year = pdf.iloc[1,8]
                        value_last_year = pdf.iloc[1,10]
                    for r in referencias:
                        #En esta tabla No coincide con las referencias
                        pdf_filter = pdf.loc[pdf['No'].isin(r.values)]
                        if len(pdf_filter) > 0:
                            pdf_filter.columns = range(pdf_filter.shape[1])
                            pdf_filter.dropna(how='all', axis=1, inplace=True)
                            #Tenemos que crear la cabecera multiindex a mano, tabula-py no es capaz de reconocerla al ser multinivel
                            if not key in df_all:
                                Final = pd.MultiIndex(levels=[['No','REFERENCIA','Propuesta de financiación (en euros)'],
                                        ['PRESUPUESTO TOTAL CONCEDIDO', 'Por concepto de gasto','Por anualidades','No', 'REFERENCIA'],
                                        ['COSTES DIRECTOS','COSTES INDIRECTOS',pdf.iloc[1,8],pdf.iloc[1,10],'No','REFERENCIA','PRESUPUESTO TOTAL CONCEDIDO']],
                                    codes= [[0,1,2,2,2,2,2],
                                            [3,4,0,1,1,2,2],
                                            [4,5,6,0,1,2,3]])
                                dataframe_header = pd.DataFrame(columns = Final)
                                
                                
                            else:
                                dataframe_header = df_all[key]

                            #Hacemos el append multitable
                            row = -1 if dataframe_header.shape[0] == 0 else dataframe_header.shape[0]
                            for c in range(pdf_filter.shape[0]):
                                dataframe_header.loc[row+1+c] = pdf_filter.iloc[c,:7].to_numpy()


                            df_all[key] = dataframe_header



        return df_all


    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass
