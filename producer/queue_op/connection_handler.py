from flask import request, current_app
from flask_restx import Api, Resource, fields
from config import ConfigClass
import pika

class ConnectionHandler:
    def __init__(self):      
        self.init_connection()
        
    def init_connection(self):
        try:
            credentials = pika.PlainCredentials(
                ConfigClass.gm_username,
                ConfigClass.gm_password)

            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=ConfigClass.gm_queue_endpoint,
                    heartbeat=0,
                    credentials=credentials)
            )
            current_app.logger.info('Successed Initiated queue connection')
            return self._connection
        except Exception as e:
            current_app.logger.error(f'Error when connecting to queue service: {e}')
            raise

    def close_connection(self):
        self._connection.close()
    
    def get_current_connection(self):
        return self._connection

    