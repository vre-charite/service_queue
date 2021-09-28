from flask import request, current_app
from flask_restx import Api, Resource, fields
from models.api_response import APIResponse, EAPIResponseCode
from .producer_project import ProducerGenerate, NormalProducer
from config import ConfigClass
import pika
import json
import os


class QueueProducer(Resource):

    def generate(self, event_type, project, create_time, payload):
        # define the event type for generate project
        try:
            generate_producer = ProducerGenerate(
                event_type, project, create_time)
            event_map = {
                'data_uploaded': generate_producer.generate_uploaded,
                'data_processed': generate_producer.generate_processed,
                'file_copy': generate_producer.file_copy,
                'file_delete': generate_producer.file_move,
                'bids_validate': generate_producer.bids_validate,
                'folder_copy': generate_producer.transparently_produce,
                'folder_delete': generate_producer.transparently_produce
            }.get(event_type, generate_producer.invalid_event)
            res = event_map(payload=payload)
            return res
        except Exception as e:
            current_app.logger.exception(
                f'Error when creating generate producer object: {e}')

    def generic_project(self, event_type, project, create_time, payload):
        # define the event type for all project
        try:
            normal_producer = NormalProducer(event_type, project, create_time)
            event_map = {
                'file_copy': normal_producer.file_copy,
                'file_delete': normal_producer.file_move,
                'bids_validate': normal_producer.bids_validate,
                'folder_copy': normal_producer.transparently_produce,
                'folder_delete': normal_producer.transparently_produce
            }.get(event_type, normal_producer.invalid_event)
            res = event_map(payload=payload)
            return res
        except Exception as e:
            current_app.logger.exception(
                f'Error when creating normal producer object: {e}')

    def invalid_project(self, event_type, project, create_time, payload):
        res = APIResponse()
        current_app.logger.error(f'Cannot Recognize project.{project}')
        res.set_result('Cannot recognize project')
        res.set_code(EAPIResponseCode.bad_request)
        return res

    def post(self):
        res = APIResponse()
        try:
            post_data = request.get_json()
            event_type = post_data.get('event_type', None)
            payload = post_data.get('payload', None)
            create_time = post_data.get('create_timestamp', None)
            project = payload.get('project', None)
            current_app.logger.info(f'postData is : {post_data}')
            event_list = ['data_uploaded', 'data_processed',
                          'file_copy', 'file_delete', 'bids_validate', 'folder_copy',
                          'folder_delete']
            if event_type not in event_list:
                current_app.logger.exception('Wrong event type: ' + event_type)
                res.set_result('Wrong event type: ' + event_type)
                res.set_code(EAPIResponseCode.bad_request)
                return res.response, res.code
            if not post_data or not payload:
                current_app.logger.exception('Empty Message')
                res.set_result('Empty Message in the queue')
                res.set_code(EAPIResponseCode.not_found)
                return res.response, res.code

            project_map = {
                'generate': self.generate,
            }.get(project, self.generic_project)
            res = project_map(event_type, project, create_time, payload)
            return res.response, res.code
        except Exception as e:
            current_app.logger.exception(
                f'Error when sending message to queue: {e}')
            res.set_result('Error when sending message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res.response, res.code
