from model.process.UtilsProcess import UtilsProcess


class ValidEvaluators():
    def __init__(self):
        super().__init__()

    def get_valid_evaluators(self, filename:str) -> dict:
        """
        Método que obtiene del configurador de los comités los que están implementados.
        :param filename nombre del fichero de configuración
        :return diccionario con los comités implementados
        """
        result:dict = {}
        utils = UtilsProcess()
        conf = utils.get_configurations(filename)
        if conf:
            for key in conf:
                if 'evaluacion' in conf[key] and conf[key]['evaluacion']:
                    evaluator = {}
                    evaluator['name'] = conf[key]['name']
                    result[key] = evaluator
        return result

    def get_valid_committee(self):
        """
        Método que obtiene del configurador de los comités los que están implementados.
        :param filename nombre del fichero de configuración
        :return diccionario con los comités implementados
        """
        return self.get_valid_evaluators('model/process/Process2/Configurations/comite.json')

    def get_valid_commissions(self):
        """
        Método que obtiene del configurador de los comités los que están implementados.
        :param filename nombre del fichero de configuración
        :return diccionario con los comités implementados
        """
        return self.get_valid_evaluators('model/process/Process2/Configurations/comision.json')
