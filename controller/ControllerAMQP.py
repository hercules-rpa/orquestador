import asyncio
from aio_pika import ExchangeType, connect_robust, Message, DeliveryMode, IncomingMessage, exceptions

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ControllerAMQP(metaclass=Singleton):
    def __init__(self, user, password, host, port, subscriptions, exchange_name, queue_name, listener=None):
        self.user           = user
        self.password       = password
        self.host           = host
        self.port           = str(port)
        self.subscriptions  = subscriptions
        self.exchange_name  = exchange_name
        self.queue_name     = queue_name
        self.listener       = listener
        
        self.connection_send        = None
        self.channel_send           = None
        self.connection_consume     = None
        self.channel_consume        = None
        self.exchange_send          = None
        self.exchange_consume       = None
        self.queue                  = None
        self.threadConsumer         = None
        self.threadProducer         = None
        self.topic_logs_exchange    = None

    async def add_subscription(self, subs):
        self.subscriptions.append(subs)
        await self.__add_queuebind()

    async def remove_subscription(self, subs):
        self.subscriptions.remove(subs)
        await self.__add_queuebind()


    async def start_consumer(self, loop = None):
        await self.__start_connection_consume(loop)
        await self.__start_consumer()
        
    def set_listener(self, listener):
        self.listener = listener

    async def send_message(self, routing_key, message_body):
        await self.__send_message(routing_key, message_body)

 
    async def __start_connection_consume(self, loop):
        try:
            self.connection_consume =  await connect_robust(
                "amqp://"+self.user+":"+self.password+"@"+self.host+":"+self.port+"/", loop=loop
            )
            
            
            self.channel_consume =  await self.connection_consume.channel()    # type: aio_pika.Channel
            self.exchange_consume = await self.channel_consume.declare_exchange(
                self.exchange_name, ExchangeType.TOPIC, auto_delete=True, durable=False
            )

            # Declaring queue
            self.queue = await self.channel_consume.declare_queue(
                self.queue_name, auto_delete=True,durable=False, arguments={"x-queue-mode":"lazy"}
            )

        except asyncio.CancelledError:
            print("Conection cancelled after trying to reconnect")
        except (exceptions.AMQPError, ConnectionError) as error:
            print("Connection failed")


    async def __send_message(self, routing_key, message_body):
        try: 
            connection_send =  await connect_robust(
                "amqp://"+self.user+":"+self.password+"@"+self.host+":"+self.port+"/", loop=None
            )
            
            channel_send =  await connection_send.channel()    # type: aio_pika.Channel
            exchange_send = await channel_send.declare_exchange(
                self.exchange_name, ExchangeType.TOPIC, auto_delete=True, durable=False
            )
            
            message = Message(
                bytes(message_body, "utf-8"),
                content_type="text/plain",
                delivery_mode=DeliveryMode.NOT_PERSISTENT
            )

            # Sending the message
            await exchange_send.publish(message, routing_key=routing_key)
        
            #print(" [x] Sent %r" % message.body)

            await connection_send.close()
        except asyncio.CancelledError:
            print("Conection cancelled after trying to reconnect")
        except (exceptions.AMQPError, ConnectionError) as error:
            print("Connection failed")
        
    async def __start_consumer(self):
        #    "amqp://guest:guest@172.17.0.1:5672/", loop=loop
        #self.connection_consumer = await connect_robust(
        #    "amqp://"+self.user+":"+self.password+"@"+self.host+":"+self.port+"/", loop=None
        #)
        
        # Creating a channel
        #channel = await self.connection_consumer.channel()
#        await self.channel_consume.set_qos(prefetch_count=10)

        #if len(self.subscriptions) > 0:
        for i in self.subscriptions:
            await self.queue.bind(self.exchange_consume, routing_key=i)

            # Start listening the queue
        await self.queue.consume(self.on_message)
        
    async def __add_queuebind(self):
        if(self.queue is not None):
            if len(self.subscriptions) > 0:
                for i in self.subscriptions:
                    await self.queue.bind(self.exchange_consume, routing_key=i)

    async def on_message(self, message: IncomingMessage):
        async with message.process():
            await self.listener.notify_msg(message.body)
            # print("[x] %r" % message.body)
            # print(message.content_type)
            # print(" [x] Received %r" % json.loads(message.body))

    def get_host(self):
        return self.host
