import requests

class RPA():

    def __init__(self, token):
        self.token = token

    def get(self, service: str):
        """
        Método GET para realizar contra nuestra API interna.

        :param service endpoint al que consulta
        :return Response respuesta obtenida
        """
        header = {'Token_Robot': self.token}
        response = requests.request("GET", service, headers=header)
        return response

    def post(self, service, data_body, files:list=None):
        """
        Método POST para realizar contra nuestra API interna.
        
        :param str service: endpoint al que consulta
        :param {} data: JSON con el cambio para el método post
        :param list files: lista de ficheros
        :return Response respuesta obtenida
        """
        headers = {'Token_Robot': self.token, 'Content-Type': 'application/json'}
        response = requests.post(service, headers=headers, data=data_body, files=files)
        return response
    
    def patch(self, service, data_body):
        """
        Método PATCH para realizar contra nuestra API interna.
        
        :param str service: endpoint al que consulta
        :param {} data: JSON con el cambio para el método patch
        :return Response respuesta obtenida
        """
        headers = {'Token_Robot': self.token, 'Content-Type': 'application/json'}
        response = requests.patch(service, headers=headers, data=data_body)
        return response
