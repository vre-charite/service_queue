from config import ConfigClass
import logging
import pika

logger = logging.getLogger()

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
            logger.info('Successed Initiated queue connection')
            return self._connection
        except Exception as e:
            logger.error(f'Error when connecting to queue service: {e}')
            raise

    def close_connection(self):
        self._connection.close()
    
    def get_current_connection(self):
        return self._connection

    