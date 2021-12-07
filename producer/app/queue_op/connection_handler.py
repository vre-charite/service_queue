import pika
from flask import current_app

from config import ConfigClass


class ConnectionHandler:
    # This class used to initiate Queue connection
    def __init__(self):
        self._connection = None
        self.init_connection()

    def init_connection(self):
        try:
            credentials = pika.PlainCredentials(
                ConfigClass.gm_username,
                ConfigClass.gm_password)

            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=ConfigClass.gm_queue_endpoint,
                    heartbeat=180,
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
