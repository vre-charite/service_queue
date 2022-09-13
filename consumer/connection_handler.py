# Copyright 2022 Indoc Research
# 
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# 
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# 
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# 

from config import ConfigClass
import logging
import pika

logger = logging.getLogger()

class ConnectionHandler:
    # this class used to handle the connection with rabbitmq server
    # AMQP connection heartbeat timeout value for negotiation during connection tuning or callable which is invoked during connection tuning. 
    # None to accept broker's value. 0 turns heartbeat off.
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
                    heartbeat=180,
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

    