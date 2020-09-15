from flask_restx import Api, Resource, fields
# from flask_restful import Api
module_api = Api(
    version='1.0', 
    title='Queue service API',
    description='Queue API', 
    doc='/v1/api-doc'
)

# api = Api()
api = module_api.namespace('Queue Service', description='Operation on RabbitMQ', path ='/')

# user operations
from queue_op.sender import Queue_sender
api.add_resource(Queue_sender, '/v1/send_message')
