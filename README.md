# Hercules-RPA

Hercules-RPA es una plataforma RPA opensource, bajo lenguaje de programación Python. Se devide principalmente en dos componentes:

1. [Orquestador](https://github.com/hercules-rpa/orquestador)
2. [Robot](https://github.com/hercules-rpa/robot)

El orquestador es el cerebro de la arquitectura, organiza y gestiona los robots a través del protocolo AMQP, dispone de una API tanto para la planificación y ejecución de procesos como para la monitorización de los mismos y los robots.
El robot se encuentra desligado de los procesos, por lo que puede ejecutar cualquier tarea, mantiene una constante comunicación con el orquestador.

## Instalación en k8s

Se dispone de un repositorio helm chart para el despliegue en kubernetes.

https://github.com/hercules-rpa/despliegue-k8s


## Instalación en máquina virtual

 - [Orquestador](#orquestador)

### Orquestador

El orquestador necesitará los siguientes servicios:
 - [RabbitMQ](#rabbitmq)
 - [Postgres](#postgres)
 - [Cassandra](#cassandra)
 - [CDN](#cdn)

En el la carpeta principal del proyecto encontramos el archivo requierements.txt que será necesario para la funcionalidad del orquestador:

 `pip install -r requierements.txt`

Por otro lado, debemos establecer la configuración del robot indicandole donde se encuentra la base de datos y el acceso, para ello debemos modificar el fichero orchestrator.json que se encuentra rpa_orchestrator/config/orchestrator.json

    `{
    "DB-PERSISTENCE":{
        "user": "postgres",
        "password": "docker",
        "host": "127.0.0.1",
        "port":"5432",
        "database": "rpa"
        }
    }`


Por último, debemos crear /var/log/orchestrator y asignale permisos para que el orquestador deposite los logs. También se guardarán en la base de datos de postgres y cassandraa.



#### RabbitMQ

El servicio de rabbitmq es el que se encargará de la comunicación robot-orquestador, orquestador-robot. 

 `sudo docker run -itd --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.8-management`

En caso de que ya hayamos hecho el run anteriormente:

`docker start rabbitmq`

#### Postgres

El servicio de postgres almacenará los datos que el orquestador necesita tanto para la persistencia como para proporcionar la información que se solicite a través de la API, como por ejemplo, logs, procesos, ejecuciones, etc.

`sudo docker run --name postgres-db -e POSTGRES_PASSWORD=docker -p 5432:5432 -d postgres`

Una vez iniciado nuestro servicio de postgres, necesitaremos conectarnos a nuestro postgres para poner el esquema de la base de datos y los procesos. Debemos ubicarnos en la ruta donde se encuentra el script de ejecución para volcar la información.
    `
     cd /ruta/hercules-rpa/rpa_orchestrator/config/bbdd/persistence 
    `
    `
     ./scriptPostgres.sh
    `

En caso de que ya hayamos hecho el run anteriormente:

`docker start postgres-db`

#### Cassandra

Apache Cassandra se trata de un software NoSQL distribuido y basado en un modelo de almacenamiento de «clave-valor», de código abierto que está escrita en Java. Permite grandes volúmenes de datos en forma distribuida. En este proyecto será la encargada de almacenar todos los datos en crudo para posteriormente poder hacer data mining y sacar estadísticas que pueden sernos de utilidad. 

`sudo docker run -itd --name cassandra -d -e CASSANDRA_BROADCAST_ADDRESS=127.0.0.1 -p 7000:7000 -p 9042:9042 cassandra`

Al igual que con postgres necesitaremos volcar el modelo.

`cd /ruta/hercules-rpa/rpa_orchestrator/config/bbdd/BI/`
`./scriptCassandraDocker.sh (sino es docker, el script sin docker) `

#### CDN

Es necesario un servidor HTTP donde realizar peticiones para la subida de ficheros, se puede usar cualquier servidor web, en el repositorio de helm se encuentra un ejemplo usando apache y php.
https://github.com/hercules-rpa/despliegue-k8s/blob/main/rpa-helm-umu/templates/configmap-cdn.yaml


## Ejecución

Una vez instalado todo para la ejecución del orquestador simplemente haremos:

`python LaunchOrchestrator.py orchestrator.json`