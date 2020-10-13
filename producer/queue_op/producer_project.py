from flask import request, current_app
from models.api_response import APIResponse, EAPIResponseCode
from queue_op.message import MessagePublish
from config import ConfigClass
import filetype
import time
import os

class ProducerGenerate:
    # Init generate project producer, including all generate related function, and different event type will be mapped to different function
    # for different event type, the published message may differ from each other
    # invalid_event function as the default function used for undefined event 
    def __init__(self, event_type, project, create_time):
        self.event_type = event_type
        self.project = project
        self.create_time = create_time
        self.routing_key = project + '.' + event_type
        self.producer = MessagePublish(self.routing_key, exchange_name=ConfigClass.gr_exchange, exchange_type='topic', queue=ConfigClass.gr_queue)
        
    def generate_uploaded(self, payload):        
        try: 
            res = APIResponse()
            input_path = payload.get('input_path', None)
            generate_id = payload.get('generate_id', None)
            uploader = payload.get('uploader', None)
            if not input_path or not generate_id or not uploader:
                res.set_result('Missing required information')
                res.set_code(EAPIResponseCode.bad_request)
                return res
            path_list = str(input_path).split('/')
            if len(path_list) != 6:
                    res.set_result('Not a valid path')
                    res.set_code(EAPIResponseCode.bad_request)
                    return res
            base_path = path_list[:4]
            work_path = path_list[:4]
            log_path = path_list[:4]
            work_path.append('workdir')
            log_path.append('logs')
            base_path.append('processed')
            base_path.append(ConfigClass.generate_pipeline)
            # check if file typs is zip
            file_type = filetype.guess(input_path)
            current_app.logger.info(f'input path: {input_path}, file type : {file_type}')
            if file_type is None:
                current_app.logger.error('Can not recognize file type')
                res.set_result('Invalid File Type')
                res.set_code(EAPIResponseCode.bad_request) 
            else: 
                if file_type.extension == 'zip':
                    message_json = {
                        'project': self.project,
                        'input_path': input_path,
                        'pipeline': ConfigClass.generate_pipeline,
                        'output_path': '/'.join(base_path),
                        'work_path': '/'.join(work_path),
                        'log_path': '/'.join(log_path),
                        'generate_id': generate_id,
                        'uploader': uploader,
                        'create_time': self.create_time
                    }
                    self.producer.publish(message_json)
                else:
                    current_app.logger.error(f'Wrong file type: {file_type}')
                    res.set_result('Invalid File Type')
                    res.set_code(EAPIResponseCode.bad_request)        
            return res
        except FileNotFoundError as not_found:
            current_app.logger.error(f'File not found in given path: {not_found}')
            res.set_result(f'File not found: {not_found.filename}')
            res.set_code(EAPIResponseCode.bad_request)
        except Exception as e:
            current_app.logger.error(f'Error when trying to parse the message to queue: {e}')
            res.set_result('Error when trying to parse the message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res 

    def generate_processed(self, payload):        
        try: 
            res = APIResponse()
            input_path = payload.get('input_path', None)
            generate_id = payload.get('generate_id', None)
            uploader = payload.get('uploader', None)
            pipeline = payload.get('pipeline', None)
            if not input_path or not generate_id or not uploader:
                res.set_result('Missing required information')
                res.set_code(EAPIResponseCode.bad_request)
                return res
            filename = os.path.basename(input_path)
            output_path = ConfigClass.vre_data_storage + '/' + self.project + '/' + pipeline + '/' + filename
            current_app.logger.info(f'input path: {input_path}, file name : {filename}')
            message_json = {
                'project': self.project,
                'input_path': input_path,
                'pipeline': pipeline,
                'output_path': output_path,
                'generate_id': generate_id,
                'uploader': uploader,
                'create_time': self.create_time
            }
            self.producer.publish(message_json)  
            return res
        except Exception as e:
            current_app.logger.error(f'Error when trying to parse the message to queue: {e}')
            res.set_result('Error when trying to parse the message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res

    def invalid_event(self, payload):        
        res = APIResponse()
        project = payload.get('project', None)
        current_app.logger.error(f'Undefined event type for project {project}')
        res.set_result('Undefined event type for generate project')
        res.set_code(EAPIResponseCode.bad_request)
        return res


class ProducerTVB:
    # Init tvb project producer, including all tvb related function, and different event type will be mapped to different function
    # for different event type, the published message may differ from each other
    # invalid_event function as the default function used for undefined event 
    def __init__(self, event_type, project, create_time):
        self.event_type = event_type
        self.project = project
        self.create_time = create_time
        self.routing_key = project + '.' + event_type
        self.producer = MessagePublish(self.routing_key, exchange_name=ConfigClass.gr_exchange, exchange_type='topic', queue=ConfigClass.gr_queue)
        
    def tvb_uploaded(self, payload):        
        try: 
            res = APIResponse()
            input_path = payload.get('input_path', None)
            uploader = payload.get('uploader', None)
            if not input_path or not uploader:
                res.set_result('Missing required information')
                res.set_code(EAPIResponseCode.bad_request)
                return res
            filename = os.path.basename(input_path)
            output_path = ConfigClass.vre_data_storage + '/' + self.project + '/adni/' + filename
            current_app.logger.info(f'input path: {input_path}, file name : {filename}')
            message_json = {
                'project': self.project,
                'input_path': input_path,
                'output_path': output_path,
                'uploader': uploader,
                'create_time': self.create_time
            }
            self.producer.publish(message_json)  
            return res
        except Exception as e:
            current_app.logger.error(f'Error when trying to parse the message to queue: {e}')
            res.set_result('Error when trying to parse the message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res

    def invalid_event(self, payload):        
        res = APIResponse()
        project = payload.get('project', None)
        current_app.logger.error(f'Undefined event type for project {project}')
        res.set_result('Undefined event type for TVB project')
        res.set_code(EAPIResponseCode.bad_request)
        return res

