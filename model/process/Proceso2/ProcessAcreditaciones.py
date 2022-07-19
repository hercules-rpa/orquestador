import os
from model.process.Proceso2.Entities.Comisiones.ComisionCienciasEconomicasYEmpresariales import ComisionCienciasEconomicasYEmpresariales
from model.process.Proceso2.Entities.Comisiones.ComisionOtrasEspecialidadesSanitarias import ComisionOtrasEspecialidadesSanitarias
from model.process.Proceso2.Entities.Evaluador import Evaluador
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion
from model.process.Proceso2.Entities.Comisiones.ComisionCienciasSociales import ComisionCienciasSociales
from model.process.Proceso2.Entities.Comisiones.ComisionFilologiaLinguistica import ComisionFilologiaLinguistica
from model.process.Proceso2.Entities.Comisiones.ComisionFisica import ComisionFisica
from model.process.Proceso2.Entities.Comisiones.ComisionInformatica import ComisionInformatica
from model.process.Proceso2.Entities.Comisiones.ComisionIngElectrica import ComisionIngElectrica
from model.process.Proceso2.Entities.Comisiones.ComisionMedicinaClinicaYEspecialidadesClinicas import ComisionMedicinaClinicaYespecialidadesClinicas
from model.process.Proceso2.Entities.Comisiones.ComisionQuimica import ComisionQuimica
from model.process.Proceso2.Entities.Comisiones.ComisionCienciasNaturaleza import ComisionCienciasNaturaleza
from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Comisiones.ComisionBiologiaCelularYMolecular import ComisionBiologiaCelularYMolecular
from model.process.Proceso2.Entities.Comisiones.ComisionCienciasComportamiento import ComisionCienciasComportamiento
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, CategoriaAcreditacion
from model.process.Proceso2.Entities.Informe import Informe
from model.process.Proceso2.ProcessSexenios import ProcessSexenios
from model.process.ProcessCommand import ProcessID, ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
import time
import json

VERSION = "1.0"
NAME = "Acreditaciones"
DESCRIPTION = "Proceso que genera un informe de ayuda al investigador para solicitar una acreditación de la ANECA"
REQUIREMENTS = ["python-docx", "pandas", "sparqlwrapper", "requests"]
ID = ProcessID.ACREDITACIONES.value


class ProcessAcreditaciones(ProcessSexenios):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def execute(self):
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.log.state = "OK"

        if not self.parameters:
            self.update_log("No se han establecido parámetros", True)
            self.log.state = "ERROR"
            self.log.end_log(time.time())
            self.state = pstatus.FINISHED
            return

        periodo = ''
        self.notificar_actualizacion('Obteniendo la comisión seleccionada.')
        comision: Comision = self.get_comision(
            self.parameters['comision'])

        self.notificar_actualizacion('Obteniendo el tipo de acreditación.')
        acreditacion = self.get_acreditacion(
            self.parameters['tipo_acreditacion'])
        if comision.id == "21":
            try:
                if 'categoria_acreditacion' in self.parameters:
                    if self.parameters['categoria_acreditacion']:
                        acreditacion.categoria = CategoriaAcreditacion(int(self.parameters['categoria_acreditacion']))
                else: 
                    self.notificar_actualizacion('ERROR no ha sido posible obtener la categoría de la acreditación, el proceso finalizará.')
                    self.log.state = "ERROR"
                    self.log.end_log(time.time())
                    self.state = pstatus.FINISHED
                    return
            except Exception as e:
                print(e)     
                self.notificar_actualizacion('ERROR al obtener la categoría de la acreditación')
                self.log.state = "ERROR"
                self.log.end_log(time.time())
                self.state = pstatus.FINISHED
                return


        if not acreditacion:
            self.notificar_actualizacion(
                'ERROR al obtener el tipo de acreditación.')
            self.log.state = "ERROR"
            self.log.end_log(time.time())
            self.state = pstatus.FINISHED
            return

        self.notificar_actualizacion(
            'Se ha escogido el tipo de acreditación: ' + acreditacion.nombre)

        self.notificar_actualizacion(
            'Obteniendo parámetros relacionados con el investigador.')
        infoInvestigador = self.get_param_investigador(self.parameters)

        self.notificar_actualizacion(
            'Obteniendo los datos del investigador utilizando Hércules-EDMA.')
        datosInvestigador = self.EDMA.get_datos_investigador(infoInvestigador)
        if not datosInvestigador:
                self.notificar_actualizacion(
                'ERROR no se ha podido obtener la información del investigador.')
                self.log.state = "ERROR"
                self.log.end_log(time.time())
                self.state = pstatus.FINISHED
                return
        self.log.completed = 10

        self.notificar_actualizacion(
            "Se procede a recuperar producción científica del investigador utilizando Hércules-EDMA")

        self.notificar_actualizacion(
            'Obteniendo la lista de artículos del investigador.')
        lista_articulos = self.get_articulos(
            infoInvestigador, periodo, comision.autoria_orden)
        print('Se han obtenido: ' + str(len(lista_articulos)) + ' artículos.')

        lista_capitulos_libros = None
        lista_libros = None
        if comision.libros_caps:
            self.notificar_actualizacion(
                'Obteniendo los capítulos de libros del investigador.')
            lista_capitulos_libros = self.EDMA.get_capitulos_libros(
                infoInvestigador, periodo)
            self.notificar_actualizacion(
                'Obteniendo los libros del investigador.')
            lista_libros = self.EDMA.get_libros(infoInvestigador, periodo)
        self.log.completed = 20

        lista_congresos:list = None
        if comision.congresos:
            self.notificar_actualizacion('Obteniendo los trabajos presentados en congresos por el investigador.')
            self.get_trabajos_congresos(infoInvestigador, periodo)

        lista_patentes:list = None
        if comision.patentes:
            pass

        self.log.completed = 40


        self.notificar_actualizacion(
            'Se procede a realizar la valoración de la solicitud de acreditación.')
        evaluacion: EvaluacionAcreditacion = comision.get_evaluacion_acreditacion(
            lista_articulos, acreditacion)

        self.notificar_actualizacion(
            "Se procederá a realizar el informe para solicitud de acreditación de la ANECA de "+datosInvestigador.nombreCompleto)

        informe = Informe()
        informe.insertar_titulo(
            'Informe de autoevaluación de la investigación para la preparación de solicitud de acreditación de la ANECA')
        document = informe.devolver_documento()

        p = document.add_paragraph('\n')

        self.notificar_actualizacion(
            'Insertando la información del investigador en el informe.')
        self.print_datos_investigador(
            p, datosInvestigador, infoInvestigador, comision, periodo, acreditacion)

        self.notificar_actualizacion(
            'Insertando la información de la evaluación de la solicitud en el informe.')
        self.print_evaluacion(document, evaluacion)
        
        #evaluacion.positiva = True
        
        if evaluacion.positiva:
            self.notificar_actualizacion('VALORACIÓN POSIT.')
            self.notificar_actualizacion(
                "Insertando en el informe la Producción científica principal")
           
            document.add_heading(
                'Ranking de Producción Científica : ', level=1)

            self.print_produccion_principal(document, comision, evaluacion)
            
            self.notificar_actualizacion(
                "Insertando en el informe la Producción científica sustitutoria.")
            self.print_produccion_cientifica(document, evaluacion.get_produccion_sustitutoria(), comision, 'sustitutoria')
        else:
            principales = []
            sustitutorios = []
            if lista_articulos:
                principales = lista_articulos[0:4]
                sustitutorios = lista_articulos[4:]

            document.add_heading(
                'Ranking de Producción Científica : Producción principal (4 contribuciones más relevantes)', level=1)

            self.notificar_actualizacion(
                "Insertando en el informe la Producción científica principal")
            
            self.print_produccion_cientifica(
                document, principales, comision, 'principal')
            self.log.completed = 60

            self.notificar_actualizacion(
                "Insertando en el informe la producción científica sustitutoria.")
            self.print_produccion_cientifica(
                document, sustitutorios, comision, 'sustitutoria')
            
            self.log.completed = 70


        if comision.alerta_autores:
            # LIBROS
            self.notificar_actualizacion(
                'Insertando en el informe los libros.')
            self.print_libros(document, lista_libros, comision)

            # CAPITULOS DE LIBROS
            self.notificar_actualizacion(
                'Insertando en el informe los capítulos de libros.')
            self.print_capitulos_libros(
                document, lista_capitulos_libros, comision)

        self.log.completed = 80

        if comision.congresos:
            self.notificar_actualizacion('Insertando en el informe los trabajos presentados en congresos.')
            self.print_trabajos_congresos(document, lista_congresos)

        if comision.patentes:
                pass
            
        
        self.log.completed = 90

        document.add_page_break()

        self.notificar_actualizacion("Persistiendo informe...")
        doc_name = self.save_informe(
            document, datosInvestigador.nombreCompleto, False)
        self.notificar_actualizacion(
            "Informe generado y guardado con el nombre "+doc_name + ".")
        self.log.completed = 90

        self.notificar_actualizacion("Subiendo informe al CDN...")
        #response = self.upload_file(doc_name)
        response = None
        if response and response.status_code == 201:
            json_dicti = json.loads(response.text)
            self.notificar_actualizacion(
                "Fichero subido correctamente, url de descarga: "+json_dicti["URL"])
        else:
            self.notificar_actualizacion('ERROR al subir el informe al CDN.')

        self.notificar_actualizacion(
            'Proceso de generación de informe de acreditación finalizado.')
        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass

    def get_comision(self, id: str) -> Comision:
        """
        Método que crea el comité que evalúa la solicitud del sexenio.
        """
        result: Comision = None
        currentdir = os.path.dirname(os.path.realpath(__file__))
        conf = self.get_configuraciones(
            currentdir+'/Configuraciones/comision.json')

        if id == "2":
            result = ComisionFisica(id, conf[id])
        elif id == "3":
            result = ComisionQuimica(id, conf[id])
        elif id == "4":  
            result = ComisionCienciasNaturaleza(id, conf[id])
        elif id == "5":
            result = ComisionBiologiaCelularYMolecular(id, conf[id])
        elif id == "7":
            result = ComisionMedicinaClinicaYespecialidadesClinicas(id, conf[id])
        elif id == "8": 
            result = ComisionOtrasEspecialidadesSanitarias(id, conf[id])
        elif id == "11":
            result = ComisionIngElectrica(id, conf[id])
        elif id == "12":
            result = ComisionInformatica(id, conf[id])
        elif id == "15" or id == "16":  
            result = ComisionCienciasEconomicasYEmpresariales(id,conf[id])
        elif id == "18": 
            result = ComisionCienciasComportamiento(id, conf[id])
        elif id == "19":
            result = ComisionCienciasSociales(id, conf[id])
        elif id == "21":
            result = ComisionFilologiaLinguistica(id, conf[id])

        if result:
            print('Se ha creado la comisión: ' + result.nombre)

        return result

    def get_acreditacion(self, id: str, categoria:CategoriaAcreditacion=CategoriaAcreditacion.NODEFINIDO) -> Acreditacion:
        """
        Método que obtiene el nombre del tipo de acreditación
        """
        result: Acreditacion = None
        conf = self.get_configuraciones(
            "Configuraciones/tipoAcreditacion.json")
        if conf and id in conf:
            result = Acreditacion(id, conf[id], categoria)
        else:
            self.notificar_actualizacion(
                'No ha sido posible obtener el tipo de acreditación.')
        return result

    def print_evaluacion(self, documento, evaluacion: EvaluacionAcreditacion):
        """
        Método que imprime la evaluación obtenida en base a la lista de artículos y los
        criterios del comité específico.
        """
        if evaluacion:
            documento.add_heading('Evaluación solicitud acreditación:')
            p = documento.add_paragraph('\n')

            p.add_run('En la evaluación que se ha realizado solo se ha tenido en cuenta los requisitos mínimos obligatorios ' + \
                'de cada comisión. \n\n')

            if evaluacion.positiva:
                p.add_run('Presentando la siguiente producción científica podría obtener una valoración ' +
                          evaluacion.valoracion_alcanzada + ' positiva. \n\n')
                if evaluacion.observaciones:
                    p.add_run('Se han obtenido las siguientes observaciones respecto a las evaluaciones que se han realizado: \n' +
                              evaluacion.observaciones + '\n')
            else:
                p.add_run(
                    'Se ha realizado la evaluación de la solicitud y puede que no cumpla los requisitos. \n\n')
                if evaluacion.observaciones:
                    p.add_run('     Los motivos de la evaluación negativa son los siguientes: \n ' +
                              evaluacion.observaciones + '\n')

    def print_produccion_principal(self, document, evaluador: Evaluador,
                                   evaluacion: EvaluacionAcreditacion):
        """
        Metodo para seleccionar la comision a imprimir
        """
        if evaluador:
            document.add_heading('Producción científica principal: ', level=1)

            if id == "2":  # fisica
                self.print_produccion_principal_comision2(
                    document, evaluador,evaluacion)
            elif evaluador.id == "3":  # quimica
                self.print_produccion_principal_comision3(
                    document, evaluador,evaluacion)
            elif evaluador.id == "4":  # ciencias naturaleza
                self.print_produccion_principal_comision4(
                    document, evaluador, evaluacion)
            elif evaluador.id == "5":  # biología celular y molecular
                self.print_produccion_principal_comision5(
                    document, evaluador, evaluacion)
            elif evaluador.id == "7":  # medicina clinica
                self.print_produccion_principal_comision7(
                    document, evaluador,evaluacion)
            elif evaluador.id == "8":  # otras especialidades médicas
                self.print_produccion_principal_comision8(
                    document, evaluador,evaluacion)
            elif evaluador.id == "11":  # ing. electrica
                self.print_produccion_principal_relevantes(
                    document, evaluador, evaluacion)
            elif evaluador.id == "12":  # informatica
                self.print_produccion_principal_relevantes(
                    document, evaluador, evaluacion)
            elif evaluador.id == "15" or evaluador.id == "16":
                # ciencias económicas y empresariales
                self.print_produccion_principal_comision_15_16(
                    document, evaluador, evaluacion)
            elif evaluador.id == "18":
                self.print_produccion_principal_comision18(
                    document, evaluador,evaluacion)
            elif evaluador.id == "19":
                self.print_produccion_principal_comision19(
                    document, evaluador,evaluacion)
            elif evaluador.id == "21":
                self.print_produccion_principal_comision21(
                    document, evaluador,evaluacion)

    def print_produccion_principal_comision2(self, document,evaluador: Evaluador,
                                            evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 2
        """
        self.print_seccion_articulos(
                self, document, evaluador, evaluacion.get_publicaciones_t1_t2(), 'Publicaciones en el primer y segundo tercil:')
    
    def print_produccion_principal_comision3(self, document,evaluador: Evaluador,
                                            evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 3
        """
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_t1(), 'Publicaciones en el primer tercil:')
            self.print_seccion_articulos(
                self, document, evaluador, evaluacion.get_publicaciones_primero(), 'Publicaciones como primer autor:')
    
    def print_produccion_principal_comision4(self, document,evaluador: Evaluador,
                                            evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 4
        """
        self.print_seccion_articulos(
                self, document, evaluador, evaluacion.get_publicaciones_t1(), 'Publicaciones en el primer tercil:')
        self.print_seccion_articulos(
                self, document, evaluador, evaluacion.get_publicaciones_t2(), 'Publicaciones en el segundo tercil:')
        self.print_seccion_articulos(
                self, document, evaluador, evaluacion.get_publicaciones_autor(), 'Publicaciones como autor principal:')

    def print_produccion_principal_comision5(self, document, evaluador: Evaluador,
                                             evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 5
        """
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_t1(), 'Publicaciones en el primer tercil:')
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_autoria_preferente(), 'Publicaciones con autoría preferente:')

    def print_produccion_principal_comision7(self, document,evaluador: Evaluador,
                                            evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 7
        """
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_t1(), 'Publicaciones en el primer tercil:')
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_autoria_preferente(), 'Publicaciones con autoría preferente:')
    
    def print_produccion_principal_comision8(self, document, evaluador: Evaluador,
                                                            evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 8
        """
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_autoria_preferente(), 'Publicaciones con autoria preferente:')
    def print_produccion_principal_comision_15_16(self, document, evaluador: Evaluador,
                                                            evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 15 y 16
        """
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_Q1_Q2(), 'Publicaciones en el primer y segundo cuartil:')
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_Q3_Q4(), 'Publicaciones en el tercer y cuarto cuartil:')
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_D1(), 'Publicaciones en el primer decil:')

    def print_produccion_principal_comision18(self, document, evaluador: Evaluador,
                                                            evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 18
        """
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_t1_t2(), 'Publicaciones en el primer y segundo tercil:')
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_autoria(), 'Publicaciones con autoria preferente:')
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_especificas(), 'Publicaciones con meritos especificas:')
    
    def print_produccion_principal_comision19(self, document, evaluador: Evaluador,
                                                            evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 19
        """
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_n1_n2(), 'Publicaciones de primer y segundo nivel:')

    def print_produccion_principal_comision21(self, document, evaluador: Evaluador,
                                                            evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones a imprimir de la comision 21
        """
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_publicaciones_n1(), 'Publicaciones de primer  nivel:')
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_monografias(), 'Publicaciones incluidas en monografías:')

    def print_produccion_principal_relevantes(self, document, evaluador: Evaluador,
                                              evaluacion: EvaluacionAcreditacion):
        """
        Método que obtiene las publicaciones relevantes y muy relevantes
        """
        if evaluacion:
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_articulos_muy_relevantes(), 'Publicaciones muy relevantes:')
            self.print_seccion_articulos(
                document, evaluador, evaluacion.get_articulos_relevantes(), 'Publicaciones relevantes:')

    def print_seccion_articulos(self, document, evaluador: Evaluador, elementos: list,
                                titulo_seccion: str):
        """
        Método que imprime los articulos seleccionados.
        """
        if elementos:
            roposition = 1
            document.add_heading(titulo_seccion, level=2)
            for element in elementos:
                if self.print_articulo(document, element, roposition, evaluador):
                    roposition += 1
        else:
            document.add_heading(
                ' No se encontraron elementos para insertar en este apartado.', level=3)
