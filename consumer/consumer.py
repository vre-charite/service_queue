from kubernetes.client.rest import ApiException
from job import KubernetesApiClient, Constant
from connection_handler import ConnectionHandler
from config import ConfigClass
import logging

logger = logging.getLogger()

class QueueConsumer:
    def __init__(self, routing_key, exchange_name=None, exchange_type=None, queue=None):
        self.conn = ConnectionHandler()
        self.current_conn = self.conn.get_current_connection()
        self.channel = self.current_conn.channel()
         # exchange
        self.channel.exchange_declare(
            exchange=exchange_name, 
            exchange_type=exchange_type)
        # queue
        self.channel.queue_declare(
            queue=queue, 
            durable=True)
        # queue exchange binding
        self.channel.queue_bind(
            exchange=exchange_name, 
            queue=queue, 
            routing_key=routing_key)
        self.exchange = exchange_name
        self.routing_key = routing_key
        self.queue = queue        