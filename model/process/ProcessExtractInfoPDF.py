import pandas as pd
import numpy as np
import time
from RPA.PDF import PDF
import pandas as pd
import xlsxwriter
import os
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessPdfToTable import ProcessPdfToTable
import json
#conda install -c conda-forge/label/gcc7 ghostscript


#Posibles atributos
    # - pagina/s
    # - busqueda de un valor
    # - busqueda de una cabecera
    # - tipo, concensiones (contendrá 3 tablas?)


NAME            = "Extract tables" 
DESCRIPTION     = "Proceso para filtrar tablas y generar un excel a partir de un documento pdf"
REQUIREMENTS    = ['RPA','numpy','pandas','xlsxwriter']
ID              = ProcessID.EXTRACT_INFO_PDF.value
DIRECTORY_FILES = "rpa_robot/files/"
DIRECTORY_TEMP  = "rpa_robot/files/temp"
KEYWORDS_REFERENCIA = ['referencia','proyecto','referencia proyecto']

class ProcessExtractInfoPDF(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)


    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.update_log("Proceso de extracción de información PDF ha empezado",True)
        self.log.completed = 5
        try:
            paths            = self.parameters['paths']
            nif_universidad  = self.parameters['nif_universidad']
            solicitudes      = self.parameters['solicitudes']
            keys_solicitudes = [*solicitudes.keys()]
            value_search     = nif_universidad+keys_solicitudes
            excel_result     = []
            
            for f in paths:
                f_name, _ = os.path.splitext(f)
                name_file = f_name.split('/')[-1]
                #Tratamiento antes para ver las paginas
                dict_page, pages_set = self.get_page(f, value_search)
                self.update_log("El proceso ha encontrado en una primera búsqueda las paginas donde se encuentran los datos a buscar: "+json.dumps(dict_page),True)
                if len(pages_set) > 0:
                    pages = ",".join(map(str,pages_set))
                    parameters_pdf = {}
                    parameters_pdf['files'] = []
                    parameters_pdf['excel'] = False
                    parameters_pdf['files'].append({'path':f,'page':pages})
                    dfs = self.get_table(parameters_pdf)
                    if not dfs:
                        return 

                    self.log.completed = 50
                    self.update_log("Procedemos a exportar el dataframe a Excel",True)
                    try:
                        fichero, investigadores_desconocidos = self.to_excel(name_file, value_search, solicitudes, pages_set, dfs)
                    except Exception as e:
                        self.log.state = "ERROR"
                        self.log.completed = 100
                        self.state = pstatus.FINISHED
                        self.update_log("Error: "+str(e),True)
                        self.update_log("Proceso de extracción de información PDF ha finalizado con errores",True)
                        self.result = None
                        self.log.end_log(time.time())
                        return

                    excel_result.append(fichero)
                    if len(investigadores_desconocidos) > 0:
                        self.update_log("Referencias que se ha encontrado, pero no estaba en SGI: "+" ,".join(investigadores_desconocidos),True)
                        self.update_log("Se procede a hacer una segunda búsqueda para obtener datos faltantes",True)
                        dict_page, pages_set = self.get_page(f, investigadores_desconocidos)
                        self.update_log("El proceso ha encontrado en una segunda búsqueda las paginas donde se encuentran los datos que no coinciden con el SGI: "+json.dumps(dict_page),True)
                        if len(pages_set) > 0:
                            pages = ",".join(map(str,pages_set))
                            parameters_pdf = {}
                            parameters_pdf['files'] = []
                            parameters_pdf['excel'] = False
                            parameters_pdf['files'].append({'path':f,'page':pages})
                            dfs = self.get_table(parameters_pdf)
                            if not dfs:
                                return 
                            try:
                                fichero, investigadores_desconocidos = self.to_excel(name_file+"Desconocidos", value_search, solicitudes, pages_set, dfs)
                            except Exception as e:
                                self.log.state = "ERROR"
                                self.log.completed = 100
                                self.state = pstatus.FINISHED
                                self.update_log("Error: "+str(e),True)
                                self.update_log("Proceso de extracción de información PDF ha finalizado con errores",True)
                                self.result = None
                                self.log.end_log(time.time())
                                return



                
                    
                else:
                    self.update_log("No existen paginas con las "+",".join(map(str,value_search))+" en "+name_file,True)
            self.log.completed = 100
            self.state = pstatus.FINISHED
            self.update_log("Proceso finalizado correctamente. ",True)
            self.result = excel_result
            self.log.end_log(time.time())
            return

        except Exception as e:
            self.log.state = "ERROR"
            self.log.completed = 100
            self.state = pstatus.FINISHED
            print(str(e))
            self.update_log("Error: "+str(e),True)
            self.update_log("Proceso de extracción de información PDF ha finalizado con errores",True)
            self.result = None
            self.log.end_log(time.time())
            return


    def get_table(self, parameters):
        self.update_log("Llamamos a la librería de tecnologías cognitivas para obtener las tablas",True)
        pspdf = ProcessPdfToTable(self.log.id_schedule, self.log.id, self.id_robot, "1", None, parameters)
        pspdf.add_data_listener(self)
        pspdf.execute()
        dfs = pspdf.result[0]
        self.update_log("Llamada al módulo de tecnologias cognitivas terminada con ÉXITO",True)
        if pspdf.log.state == "ERROR":
            self.log.state = "ERROR"
            self.log.completed = 100
            self.state = pstatus.FINISHED
            self.log.end_log(time.time())
            
            self.result = None
            return None
        return dfs
        

    #Busca las paginas donde aparecen los valores a buscar
    def get_page(self, pdf, values):
        self.update_log("Buscamos las paginas necesarias. ",True)
        self.log.completed = 15
        pdf_preload = PDF()
        values_per_page = {}
        text = pdf_preload.get_text_from_pdf(pdf)
        total_pages = []
        for term in values:
            pages = []
            terms = []
            for (key, value) in text.items():
                if term in value:
                    if key in pages:
                        continue
                    pages.append(key)
                    total_pages.append(key)                
            terms.append(term)
            values_per_page[term] = pages
        self.update_log("Terminamos de buscar las paginas que necesitamos. ",True)
        self.log.completed = 25
        return values_per_page, sorted(set(total_pages))

    def to_excel(self, name, values_search, solicitudes, page_set, dfs):
        self.update_log("Creamos el fichero excel "+"resolucion_"+name+".xlsx",True)
        writer = pd.ExcelWriter(DIRECTORY_FILES+"resolucion_"+name+".xlsx", engine="xlsxwriter")
        workbook = writer.book
        startrow = 2
        startcol = 0
        referencias_investigadores = []
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
            'valign': 'center'}),
            workbook.add_format({
            'text_wrap': True,
            'border': 2,
            'border_color':'#538DD5',
            'fg_color': '#ffff00',
            'align': 'center',
            'valign': 'center'})]

        for i,df in enumerate(dfs):
            self.log.completed += 50/len(dfs)
            #Eliminamos filas que no necesitamos. Dejamos un margen de 5 por arriba y por abajo
            df_aux = []
            add_header = True
            indexes = []            
            for v in values_search:
                idx, columns = np.where(df == v)
                for x in idx:
                    indexes.append(x)
            indexes = sorted(set(indexes))
            if len(indexes) > 0:
                for idx in indexes:
                    #Añadimos las primeras 5 filas que incluyen tambien el header
                    if add_header:
                        for rownext in range(0,5): 
                            if rownext < idx and df.shape[0] > rownext:
                                df_aux.append(df.loc[[rownext]])
                        add_header = False
                    df_aux.append(df.loc[[idx]])
                #Añadimos las 5 filas despues de la ultima detección, por si acaso hay un "Total Universidad de Murcia" y no se cogería si solo cogemos por NIF y Referencia proyecto
                if indexes[-1]+1 < df.shape[0]:
                    for rownext in range(0,5):
                        if df.shape[0] > indexes[-1]+rownext:
                            df_aux.append(df.loc[[indexes[-1]+rownext]])

            df = pd.concat(df_aux)

            df.to_excel(writer,sheet_name="Page-"+str(page_set[i]),startrow=startrow, startcol=startcol)

            worksheet_result = writer.sheets["Page-"+str(page_set[i])]
            fila = 0
            color_index = 0
            df = df.replace(np.nan, " ")
            referencia_columna = ''
            
            #PONEMOS EL FORMATO EN LOS DIFERENTES DATOS QUE TENEMOS, COLOR ALTERNATIVO PARA CADA FILA, ETC..
            for f in range(startrow+1, startrow+1+df.shape[0]):
                columna = 0
                value_find = False
                first_time_find = True
                referencia_proyecto = None

                for c in range(startcol+1, startcol+df.shape[1]+1):
                    value = str(df.iloc[fila,columna]).replace("\r", " ")

                    if value in values_search:
                        value_find = True

                    if value.lower() in KEYWORDS_REFERENCIA:
                        referencia_columna = columna

                    if value_find:
                        if referencia_columna != '':
                            value_old = str(df.iloc[fila,referencia_columna]).replace("\r", " ")
                            if not referencia_proyecto and columna >= referencia_columna and not value_old in values_search:
                                if (value_old[0:3].lower()).strip() == (([*solicitudes.keys()][0][0:3]).lower()).strip(): #Comparamos si las 3 primeras letras coinciden para asegurarnos de que es una referencia (PID, PRE, RED...)
                                    referencias_investigadores.append(value_old)
                                    worksheet_result.write(f,df.shape[1]+startcol+1, 'Desconocido', format_colors[2])
                                    referencia_proyecto = value_old
                            elif not referencia_proyecto and columna >= referencia_columna and value_old in [*solicitudes.keys()]:
                                nombre_investigador = solicitudes[value_old]
                                referencia_proyecto = value_old
                                worksheet_result.write(f,df.shape[1]+startcol+1, nombre_investigador, format_colors[2])
                        #subrayamos en amarillo la fila encontrada           
                        worksheet_result.write(f,c, value, format_colors[2])
                        #subrayamos los valores anteriores de la columna, solo entramos una vez aqui por cada fila
                        if first_time_find:
                            for c_aux in range(columna, -1, -1):
                                value = str(df.iloc[fila,c_aux]).replace("\r", " ")
                                worksheet_result.write(f,c_aux+startcol+1, value, format_colors[2])
                            first_time_find = False
                        
                    else:
                        worksheet_result.write(f,c, value, format_colors[color_index])
                    columna = columna +1
                fila = fila +1
                color_index = (color_index+1)%2
            
            
            #Eliminamos la columna indice, noexiste otra forma de hacerlo
            # for c in range(startrow, startrow + df.shape[0]+10):
            #     worksheet_result.write(c,0,' ')
            worksheet_result.set_column('A:I',20)
        writer.save()
        return "resolucion_"+name+".xlsx", referencias_investigadores


    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass
