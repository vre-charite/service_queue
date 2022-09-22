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

from kubernetes.client.rest import ApiException
from connection_handler import ConnectionHandler
from config import ConfigClass
import logging

logger = logging.getLogger()

class QueueConsumer:
    # Init Queue Consumer connection
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