import os
from rpa_robot.ControllerSettings import ControllerSettings
from model.EDMA import EDMA
from model.process.UtilsProcess import UtilsProcess
from model.process.Process2.Entities.Commissions.CommissionCienciasEconomicasYEmpresariales import CommissionCienciasEconomicasYEmpresariales
from model.process.Process2.Entities.Commissions.CommissionOtrasEspecialidadesSanitarias import CommissionOtrasEspecialidadesSanitarias
from model.process.Process2.Entities.Evaluator import Evaluator
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation
from model.process.Process2.Entities.Commissions.CommissionCienciasSociales import CommissionCienciasSociales
from model.process.Process2.Entities.Commissions.CommissionFilologiaLinguistica import CommissionFilologiaLinguistica
from model.process.Process2.Entities.Commissions.CommissionFisica import CommissionFisica
from model.process.Process2.Entities.Commissions.CommissionInformatica import CommissionInformatica
from model.process.Process2.Entities.Commissions.CommissionIngElectrica import CommissionIngElectrica
from model.process.Process2.Entities.Commissions.CommissionMedicinaClinicaYespecialidadesClinicas import CommissionMedicinaClinicaYespecialidadesClinicas
from model.process.Process2.Entities.Commissions.CommissionQuimica import CommissionQuimica
from model.process.Process2.Entities.Commissions.CommissionCienciasNaturaleza import CommissionCienciasNaturaleza
from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Commissions.CommisionBiologiaCelularYMolecular import CommissionBiologiaCelularYMolecular
from model.process.Process2.Entities.Commissions.CommissionCienciasComportamiento import CommissionCienciasComportamiento
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationCategory
from model.process.Process2.Entities.Report import Report
from model.process.ProcessSexenios import ProcessSexenios
from model.process.ProcessCommand import ProcessID, ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
import time
import json

VERSION = "1.0"
NAME = "Acreditaciones"
DESCRIPTION = "Proceso que genera un informe de ayuda al investigador para solicitar una acreditación de la ANECA"
REQUIREMENTS = ["python-docx", "pandas", "sparqlwrapper", "requests"]
ID = ProcessID.GENERATE_ACCREDITATION.value
cs = ControllerSettings()

class ProcessAcreditaciones(ProcessSexenios):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None, ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    def execute(self):
        """
        Método encargado de la ejecución del proceso de acreditacione
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

        period = ''
        self.notify_update('Obteniendo la comisión seleccionada.')
        commission: Commission = self.get_commission(
            self.parameters['comision'])

        self.notify_update('Obteniendo el tipo de acreditación.')
        accreditation = self.get_accreditation(
            self.parameters['tipo_acreditacion'])
        if commission.id == "21":
            try:
                if 'categoria_acreditacion' in self.parameters:
                    if self.parameters['categoria_acreditacion']:
                        accreditation.category = AccreditationCategory(
                            int(self.parameters['categoria_acreditacion']))
                else:
                    self.notify_update(
                        'ERROR no ha sido posible obtener la categoría de la acreditación, el proceso finalizará.')
                    self.log.state = "ERROR"
                    self.log.end_log(time.time())
                    self.state = pstatus.FINISHED
                    return
            except Exception as e:
                print(e)
                self.notify_update(
                    'ERROR al obtener la categoría de la acreditación')
                self.log.state = "ERROR"
                self.log.end_log(time.time())
                self.state = pstatus.FINISHED
                return

        if not accreditation:
            self.notify_update(
                'ERROR al obtener el tipo de acreditación.')
            self.log.state = "ERROR"
            self.log.end_log(time.time())
            self.state = pstatus.FINISHED
            return

        self.notify_update(
            'Se ha escogido el tipo de acreditación: ' + accreditation.name)

        self.notify_update(
            'Obteniendo parámetros relacionados con el investigador.')
        researcherInfo = self.get_researcher_info(self.parameters)

        self.notify_update(
            'Obteniendo los datos del investigador utilizando Hércules-EDMA.')

        edma: EDMA = cs.get_edma(self.ip_api, self.port_api)
        if edma:
            researcherData = edma.get_researcher_data(researcherInfo)
            if not researcherData:
                self.notify_update(
                    'ERROR no se ha podido obtener la información del investigador.')
                self.log.state = "ERROR"
                self.log.end_log(time.time())
                self.state = pstatus.FINISHED
                return
            self.log.completed = 10

            self.notify_update(
                "Se procede a recuperar producción científica del investigador utilizando Hércules-EDMA")

            self.notify_update(
                'Obteniendo la lista de artículos del investigador.')
            articles = self.get_articles(
                researcherInfo, period, commission.authorship_order, edma)
            print('Se han obtenido: ' + str(len(articles)) + ' artículos.')

            charters_book = None
            books = None
            if commission.books_caps:
                self.notify_update(
                    'Obteniendo los capítulos de libros del investigador.')
                charters_book = edma.get_chapters_books(
                    researcherInfo, period)

                self.notify_update(
                    'Obteniendo los libros del investigador.')
                books = edma.get_books(researcherInfo, period)
            self.log.completed = 20

            conferences: list = None
            if commission.conferences:
                self.notify_update(
                    'Obteniendo los trabajos presentados en congresos por el investigador.')
                self.get_conferences(researcherInfo, period, edma)

            patents: list = None
            if commission.patents:
                self.notify_update(
                    'Obteniendo las patentes del investigador.')
                patents = self.get_patents(researcherInfo, edma)

            self.log.completed = 40

            self.notify_update(
                'Se procede a realizar la valoración de la solicitud de acreditación.')
            evaluation: AccreditationEvaluation = commission.get_accreditation_evaluation(
                articles, accreditation)

            self.notify_update(
                "Se procederá a realizar el informe para solicitud de acreditación de la ANECA de "+researcherData.name)

            informe = Report()
            informe.add_title(
                'Informe de autoevaluación de la investigación para la preparación de solicitud de acreditación de la ANECA')
            document = informe.get_document()

            self.notify_update(
                'Insertando la información del investigador en el informe.')
            self.print_researcher_data(
                document, researcherData, researcherInfo, commission, period, accreditation)

            self.notify_update(
                'Insertando la información de la evaluación de la solicitud en el informe.')
            self.print_evaluation(document, evaluation, 1)

            if evaluation.positive:
                self.notify_update(
                    "Insertando en el informe la producción científica principal")

                self.print_main_production(
                    document, commission, evaluation, 2.1)

                self.notify_update(
                    "Insertando en el informe la producción científica sustitutoria.")
                self.print_scientific_production(
                    document, evaluation.get_substitute_production(), commission, 'sustitutoria', 2.2)
            else:
                main = []
                substitutes = []
                if articles:
                    main = articles[0:4]
                    substitutes = articles[4:]

                self.notify_update(
                    "Insertando en el informe la Producción científica principal")

                self.print_scientific_production(
                    document, main, commission, 'principal', 2.1)
                self.log.completed = 60

                self.notify_update(
                    "Insertando en el informe la producción científica sustitutoria.")
                self.print_scientific_production(
                    document, substitutes, commission, 'sustitutoria', 2.2)

                self.log.completed = 70

            if commission.authors_alert:
                # LIBROS
                self.notify_update(
                    'Insertando en el informe los libros.')
                self.print_books(document, books, commission, 3)

                # CAPITULOS DE LIBROS
                self.notify_update(
                    'Insertando en el informe los capítulos de libros.')
                self.print_chapter_books(
                    document, charters_book, commission, 4)

            self.log.completed = 80

            self.print_conferences_patents(
                document, commission, conferences, patents, 5)

            self.log.completed = 90

            document.add_page_break()

            self.notify_update("Persistiendo informe...")
            doc_name = self.save_report(
                document, researcherData.name, False)
            self.notify_update(
                "Informe generado y guardado con el nombre "+doc_name + ".")
            self.log.completed = 90

            self.notify_update("Subiendo informe al CDN...")
            url_cdn = cs.get_url_upload_cdn(self.ip_api, self.port_api)
            response = self.upload_file(doc_name, url_cdn)
            
            status_send = None

            if response and response.status_code == 200:
                upload_response = json.loads(response.text)
                self.notify_update(
                    "Fichero subido correctamente, url de descarga: "+upload_response["url_cdn"])

                config = cs.get_globals_settings(self.ip_api, self.port_api)
                if config:
                    json_dicti = json.loads(config)
                    if json_dicti:
                        url = json_dicti['edma_host_servicios'] + \
                            '/editorcv/Sexenios/Notify'
                        response = self.send_report(
                            upload_response["url_cdn"], researcherInfo[1], url)

                        if response:
                            status_send = response.status_code
                        self.result = upload_response["url_cdn"]

            if status_send == 200:
                self.notify_update("Informe notificado correctamente")
            else:
                self.notify_update(
                            "ERROR en la notificación del informe")
                self.log.state = "ERROR"
                

            if os.path.exists(doc_name):
                os.remove(doc_name)
        else:
            self.notify_update(
                'ERROR en la obtención de parámetros para la consulta a Hércules-EDMA.')
            self.log.state = "ERROR"

        self.notify_update(
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

    def get_commission(self, id: str) -> Commission:
        """
        Método que crea la comisión que evalúa la solicitud de la acreditación.
        :param id identificador de la comisión evaluatora
        :return Commission objeto que contiene los datos de la comisión
        """
        result: Commission = None
        currentdir = os.path.dirname(os.path.realpath(__file__))
        utils = UtilsProcess()
        conf = utils.get_configurations(
            currentdir+'/Process2/Configurations/comision.json')
        if id == "2":
            result = CommissionFisica(id, conf[id])
        elif id == "3":
            result = CommissionQuimica(id, conf[id])
        elif id == "4":
            result = CommissionCienciasNaturaleza(id, conf[id])
        elif id == "5":
            result = CommissionBiologiaCelularYMolecular(id, conf[id])
        elif id == "7":
            result = CommissionMedicinaClinicaYespecialidadesClinicas(
                id, conf[id])
        elif id == "8":
            result = CommissionOtrasEspecialidadesSanitarias(id, conf[id])
        elif id == "11":
            result = CommissionIngElectrica(id, conf[id])
        elif id == "12":
            result = CommissionInformatica(id, conf[id])
        elif id == "15" or id == "16":
            result = CommissionCienciasEconomicasYEmpresariales(id, conf[id])
        elif id == "18":
            result = CommissionCienciasComportamiento(id, conf[id])
        elif id == "19":
            result = CommissionCienciasSociales(id, conf[id])
        elif id == "21":
            result = CommissionFilologiaLinguistica(id, conf[id])

        if result:
            print('Se ha creado la comisión: ' + result.name)

        return result

    def get_accreditation(self, id: str,
                          category: AccreditationCategory = AccreditationCategory.NODEFINIDO) -> Accreditation:
        """
        Método que obtiene el nombre del tipo de acreditación
        :param id identificador del tipo de acreditación
        :param category categoría del tipo de acreditación (docencia, investigación)
        """
        result: Accreditation = None
        currentdir = os.path.dirname(os.path.realpath(__file__))
        utils = UtilsProcess()
        conf = utils.get_configurations(
            currentdir+'/Process2/Configurations/tipoAcreditacion.json')
        if conf and id in conf:
            result = Accreditation(id, conf[id], category)
        else:
            self.notify_update(
                'No ha sido posible obtener el tipo de acreditación.')
        return result

    def print_evaluation(self, document, evaluation: AccreditationEvaluation, bookmark: int):
        """
        Método que imprime la evaluación obtenida en base a la lista de artículos y los
        criterios del comité específico.
        :param document documento sobre el que se insertará el resultado de la evaluación
        :param evaluator objeto que tiene el resultado de la evaluación
        :param bookmark marcador que se utiliza para la numeración de la sección
        """
        if evaluation:
            document.add_heading(
                str(bookmark)+'. Evaluación solicitud acreditación', level=1)
            p = document.add_paragraph('En la evaluación que se ha realizado solo se ha tenido en cuenta los requisitos mínimos obligatorios ' +
                                       'de cada comisión. \n')

            if evaluation.positive:
                p.add_run('Presentando la siguiente producción científica podría obtener una valoración ' +
                          evaluation.assessment + ' positiva.')
                if evaluation.observation:
                    p.add_run('\n\nSe han obtenido las siguientes observaciones respecto a las evaluationes que se han realizado: \n\n' +
                              evaluation.observation)
            else:
                p.add_run(
                    'Se ha realizado la evaluación de la solicitud y puede que no cumpla los requisitos.')
                if evaluation.observation:
                    p.add_run('\n\nLos motivos de la evaluación negativa son los siguientes: \n' +
                              evaluation.observation)

    def print_main_production(self, document, evaluator: Evaluator,
                              evaluation: AccreditationEvaluation, bookmark: int):
        """
        Método encargado de la impresión de la producción principal.
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        :param bookmark número que determina la sección en el documento       
        """
        document.add_heading('2. Ranking de Producción Científica\n' +
                             str(bookmark) + '. Producción principal', level=1)
        if evaluator:
            if evaluator.id == "2":  # fisica
                self.print_main_production_commission2(
                    document, evaluator, evaluation)
            elif evaluator.id == "3":  # quimica
                self.print_main_production_commission3(
                    document, evaluator, evaluation)
            elif evaluator.id == "4":  # ciencias naturaleza
                self.print_main_production_commission4(
                    document, evaluator, evaluation)
            elif evaluator.id == "5":  # biología celular y molecular
                self.print_main_production_commission5(
                    document, evaluator, evaluation)
            elif evaluator.id == "7":  # medicina clinica
                self.print_main_production_commission7(
                    document, evaluator, evaluation)
            elif evaluator.id == "8":  # otras especialidades médicas
                self.print_main_production_commission8(
                    document, evaluator, evaluation)
            elif evaluator.id == "11":  # ing. electrica
                self.print_produccion_principal_relevantes(
                    document, evaluator, evaluation)
            elif evaluator.id == "12":  # informatica
                self.print_produccion_principal_relevantes(
                    document, evaluator, evaluation)
            elif evaluator.id == "15" or evaluator.id == "16":
                # ciencias económicas y empresariales
                self.print_main_production_commission_15_16(
                    document, evaluator, evaluation)
            elif evaluator.id == "18":
                self.print_main_production_commission18(
                    document, evaluator, evaluation)
            elif evaluator.id == "19":
                self.print_main_production_commission19(
                    document, evaluator, evaluation)
            elif evaluator.id == "21":
                self.print_main_production_commission21(
                    document, evaluator, evaluation)

    def print_main_production_commission2(self, document, evaluator: Evaluator,
                                          evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 2
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        self.print_articles(document, evaluator, evaluation.get_publications_t1_t2(
        ), 'Publicaciones en el primer y segundo tercil', '2.1.1')

    def print_main_production_commission3(self, document, evaluator: Evaluator,
                                          evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 3
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_t1(), 'Publicaciones en el primer tercil', '2.1.1')
            self.print_articles(document, evaluator, evaluation.get_publications_first_author(
            ), 'Publicaciones como primer autor', '2.1.2')

    def print_main_production_commission4(self, document, evaluator: Evaluator,
                                          evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 4
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        self.print_articles(document, evaluator, evaluation.get_publications_t1(
        ), 'Publicaciones en el primer tercil', '2.1.1')
        self.print_articles(document, evaluator, evaluation.get_publications_t2(
        ), 'Publicaciones en el segundo tercil', '2.1.2')
        self.print_articles(document, evaluator, evaluation.get_publications_author(
        ), 'Publicaciones como autor principal,', '2.1.3')

    def print_main_production_commission5(self, document, evaluator: Evaluator,
                                          evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 5
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_t1(), 'Publicaciones en el primer tercil', '2.1.1')
            self.print_articles(
                document, evaluator, evaluation.get_publications_authorship(), 'Publicaciones con autoría preferente', '2.1.2')

    def print_main_production_commission7(self, document, evaluator: Evaluator,
                                          evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 7
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_t1(), 'Publicaciones en el primer tercil', '2.1.1')
            self.print_articles(
                document, evaluator, evaluation.get_publications_authorship(), 'Publicaciones con autoría preferente', '2.1.2')

    def print_main_production_commission8(self, document, evaluator: Evaluator,
                                          evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 8
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_authorship(), 'Publicaciones con autoria preferente', '2.1.1')

    def print_main_production_commission_15_16(self, document, evaluator: Evaluator,
                                               evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 15 y 16
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_Q1_Q2(), 'Publicaciones en el primer y segundo cuartil', '2.1.1')
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_Q3_Q4(), 'Publicaciones en el tercer y cuarto cuartil', '2.1.2')
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_D1(), 'Publicaciones en el primer decil', '2.1.3')

    def print_main_production_commission18(self, document, evaluator: Evaluator,
                                           evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 18
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_t1_t2(), 'Publicaciones en el primer y segundo tercil', '2.1.1')
            self.print_articles(
                document, evaluator, evaluation.get_publications_authorship(), 'Publicaciones con autoria preferente', '2.1.2')

    def print_main_production_commission19(self, document, evaluator: Evaluator,
                                           evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 19
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_n1_n2(), 'Publicaciones de primer y segundo nivel', '2.1.1')

    def print_main_production_commission21(self, document, evaluator: Evaluator,
                                           evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones a imprimir de la comision 21
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_publications_n1(), 'Publicaciones de primer nivel', '2.1.1')

    def print_produccion_principal_relevantes(self, document, evaluator: Evaluator,
                                              evaluation: AccreditationEvaluation):
        """
        Método que obtiene las publicaciones relevantes y muy relevantes
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param evaluation objeto que contiene la lista de elementos de producción principal
        """
        if evaluation:
            self.print_articles(
                document, evaluator, evaluation.get_articles_m_relevant(), 'Publicaciones muy relevantes', '2.1.1')
            self.print_articles(
                document, evaluator, evaluation.get_articles_relevant(), 'Publicaciones relevantes', '2.1.2')

    def print_articles(self, document, evaluator: Evaluator, elements: list,
                       title: str, bookmark):
        """
        Método que imprime los articulos seleccionados.
        :param document documento sobre el que se imprimirá
        :param evaluator comisión que evalúa la acreditación
        :param elementos elementos que se insertarán en la sección
        :param title título que se le asignará a la sección insertada en el documento
        :param bookmark número que determina la sección en el documento 
        """
        document.add_heading(bookmark + '. ' + title, level=2)
        if elements:
            roposition = 1
            for element in elements:
                if self.print_article(document, element, roposition, evaluator):
                    roposition += 1
        else:
            document.add_paragraph(
                'No se encontraron elementos para insertar en este apartado.')
