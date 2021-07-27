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
