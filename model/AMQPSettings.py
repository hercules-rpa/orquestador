


"""
Clase para modelar los Ajustes AMQP de la aplicación
"""
class AMQPSettings():
    def __init__(self, username,password,host,port,subscriptions,exchange_name,queue_name):
        self.user = username
        self.password = password
        self.host = host
        self.port = port
        self.subscriptions = subscriptions
        self.exchange_name = exchange_name
        self.queue_name = queue_name
