from flask import request, current_app
from flask_restx import Api, Resource, fields
from models.api_response import APIResponse, EAPIResponseCode
from queue_op.producer_project import ProducerGenerate, ProducerTVBCloud, NormalProducer
from config import ConfigClass
import pika
import json 
import os    

class QueueProducer(Resource):
    def generate(self, event_type, project, create_time, payload):
        # define the event type for generate project
        try:
            generate_producer = ProducerGenerate(event_type, project, create_time)
            event_map = {
                'data_uploaded':generate_producer.generate_uploaded,
                'data_processed':generate_producer.generate_processed
            }.get(event_type, generate_producer.invalid_event)
            res = event_map(payload=payload)
            return res
        except Exception as e:
            current_app.logger.exception(f'Error when creating generate producer object: {e}')
        

    def tvbcloud(self, event_type, project, create_time, payload):
        # define the event type for tvp project 
        try:
            tvbc_producer = ProducerTVBCloud(event_type, project, create_time)
            event_map = {
                'data_uploaded':tvbc_producer.tvbc_uploaded,
            }.get(event_type, tvbc_producer.invalid_event)
            res = event_map(payload=payload)
            return res
        except Exception as e:
            current_app.logger.exception(f'Error when creating generate producer object: {e}')

    def generic_project(self, event_type, project, create_time, payload):
         # define the event type for all project
        try:
            normal_producer = NormalProducer(event_type, project, create_time)
            event_map = {
                'file_copy': normal_producer.file_copy
            }.get(event_type, normal_producer.invalid_event)
            res = event_map(payload=payload)
            return res
        except Exception as e:
            current_app.logger.exception(f'Error when creating normal producer object: {e}')

    def invalid_project(self, event_type, project, create_time, payload):
        res = APIResponse()
        current_app.logger.error(f'Cannot Recognize project.{project}')
        res.set_result('Cannot recognize project')
        res.set_code(EAPIResponseCode.bad_request)
        return res

    def post(self):
        try: 
            res = APIResponse()
            post_data = request.get_json()
            event_type = post_data.get('event_type', None)
            payload = post_data.get('payload', None)
            create_time = post_data.get('create_timestamp', None)
            project = payload.get('project', None)
            generic_project = payload.get('generic',False)
            current_app.logger.info(f'postData is : {post_data}')
            event_list = ['data_uploaded', 'data_processed', 'file_copy']
            if event_type not in event_list:
                current_app.logger.exception('Wrong event type')
                res.set_result('Wrong event type')
                res.set_code(EAPIResponseCode.bad_request)
                return res.response, res.code
            if not post_data or not payload:
                current_app.logger.exception('Empty Message')
                res.set_result('Empty Message in the queue')
                res.set_code(EAPIResponseCode.not_found)
                return res.response, res.code
            if generic_project:
                res = self.generic_project(event_type, project, create_time, payload)
            else:
            # project_map will map project to different functions, and if there is no mapping found, it will map project to default function, which is invalid_project
                project_map = {
                    'generate': self.generate,
                    # 'tvbcloud': self.tvbcloud
                }.get(project, self.invalid_project)
                res = project_map(event_type, project, create_time, payload)
            return res.response, res.code
        except Exception as e:
            current_app.logger.exception(f'Error when sending message to queue: {e}')
            res.set_result('Error when sending message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res.response, res.code

