from models.api_response import APIResponse, EAPIResponseCode
from queue_op.connection_handler import ConnectionHandler
from flask import request, current_app
from flask_restx import Api, Resource, fields
import pika 
import json

class MessagePublish:
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


    def publish(self, body):     
        res = APIResponse()     
        try:
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=json.dumps(body),
                properties=pika.BasicProperties(
                    delivery_mode = 2, # make message persistent
                )
            )
            current_app.logger.info(" [x] Sent %r"%body)
            self.channel.confirm_delivery() # confirm the delivery to exchange
            self.conn.close_connection()
            res.set_result('Sent Message successfully to the queue')
            res.set_code(EAPIResponseCode.success)
            return res.response, res.code
        except pika.exceptions.UnroutableError:
            current_app.logger.error("Failed to send message %r" % body)
            res.set_result('Failed to send message')
            res.set_code(EAPIResponseCode.internal_error)
            return res.response, res.code   