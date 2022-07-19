import json
import os
from model.process.Proceso2.Entities.Evaluaciones.Evaluacion import Evaluacion
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion
from model.process.Proceso2.Entities.Evaluador import Evaluador
from abc import abstractmethod

"""
Una comisión es el organismo encargado de evaluar las solicitudes de acreditaciones
de los investigadores
"""
class Comision(Evaluador):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)

    @abstractmethod
    def get_evaluacion_acreditacion(self, produccion_cientifica, tipo:Acreditacion) -> Evaluacion:
        pass

    def get_criterio_acreditacion(self, tipo_acreditacion:TipoAcreditacion, valoracion:str=''):
        """
        Método que obtiene los parámetros a utilizar en la evaluación de un tipo de
        acreditación, utilizando si es necesario el tipo de valoración que se va a comprobar.
        :param tipo_acreditacion Enumerado que define el tipo de acreditación
        :valoracion letra de la valoración que se evaluará (A,B,C...)

        :return si lo encuentra devuelve los parámetros que se deben utilizar, en caso contrario
        no devolverá nada.
        """
        criterio = self.get_criterio()
        if criterio:
            nodo_tipo = ''
            if tipo_acreditacion == TipoAcreditacion.CATEDRA:
                nodo_tipo = 'catedra'
            elif tipo_acreditacion == TipoAcreditacion.TITULARIDAD:
                nodo_tipo = 'titularidad'

            if nodo_tipo:
                result = criterio[nodo_tipo]
                if result and valoracion and valoracion in result:
                    result = result[valoracion]                        
                return result
        return None
                
    






    