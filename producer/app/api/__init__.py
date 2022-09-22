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

from flask_restx import Api
module_api = Api(
    version='1.0', 
    title='Message Broker service API',
    description='Message Broker API', 
    doc='/v1/api-doc'
)

# queue ns
from app.queue_op.producer import QueueProducer
queue_ns = module_api.namespace('Queue Service', description='Operation on RabbitMQ', path ='/')
queue_ns.add_resource(QueueProducer, '/v1/send_message')

# broker ns
from .root import BrokerRoot
from .pub import BrokerPublisher
from .sub import BrokerSubscriber, BrokerConsumerHookShowcase
broker_ns_v1 = module_api.namespace('Message Broker Service', description='Message Broker', path ='/v1/broker')
broker_ns_v1.add_resource(BrokerRoot, '/')
broker_ns_v1.add_resource(BrokerPublisher, '/pub')
broker_ns_v1.add_resource(BrokerSubscriber, '/sub')
broker_ns_v1.add_resource(BrokerConsumerHookShowcase, '/hooktest')
