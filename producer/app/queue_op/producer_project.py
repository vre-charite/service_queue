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

import os

from flask import current_app

from config import ConfigClass
from models.api_response import APIResponse
from models.api_response import EAPIResponseCode
from app.queue_op.message import MessagePublish


class NormalProducer:
    # Init Filecopy producer and define the normal function used for all projects
    # invalid_event function as the default function used for undefined event
    def __init__(self, event_type, project, create_time):
        self.event_type = event_type
        self.project = project
        self.create_time = create_time
        self.routing_key = project + '.' + event_type
        self.producer = MessagePublish(self.routing_key,
                                       exchange_name=ConfigClass.gr_exchange,
                                       exchange_type='topic',
                                       queue=ConfigClass.gr_queue)

    def bids_validate(self, payload):
        current_app.logger.info(self.routing_key + "  ---------bids_validate event sending.")
        res = APIResponse()
        try:
            dataset_geid = payload.get('dataset_geid', None)
            access_token = payload.get('access_token', None)
            refresh_token = payload.get('refresh_token', None)
            if not dataset_geid:
                res.set_result('Missing required dataset_geid')
                res.set_code(EAPIResponseCode.bad_request)
                return res
            current_app.logger.info(f'dataset_geid: {dataset_geid}')
            current_app.logger.info(f'access_token: {access_token}')
            current_app.logger.info(f'refresh_token: {refresh_token}')
            message_json = {
                "dataset_geid": dataset_geid,
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            self.producer.publish(message_json)
            return res

        except Exception as e:
            current_app.logger.error(f'Error when trying to parse the message to queue: {e}')
            res.set_result('Error when trying to parse the message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res

    def file_copy(self, payload):
        current_app.logger.info(self.routing_key + "  ---------event sending.")
        res = APIResponse()
        try:
            destination_geid = payload.get('destination_geid', None)
            input_path = payload.get('input_path', None)
            uploader = payload.get('uploader', None)
            request_id = payload.get('request_id', None)
            dcm_id = payload.get('dcm_id', None)
            output_path = payload.get('output_path', None)
            session_id = payload.get('session_id', 'default_session')
            job_id = payload.get('job_id', 'default_job')
            operator = payload.get('operator', 'admin')
            operation_type = payload.get('operation_type', None)
            input_geid = payload.get('input_geid', None)
            auth_token = payload.get('auth_token', {"at":"", "rt":""})

            path_list = str(input_path).split('/')
            log_path = path_list[:4]
            log_path.append('logs')
            if not input_path or not uploader or not output_path:
                res.set_result('Missing required information')
                res.set_code(EAPIResponseCode.bad_request)
                return res
            filename = os.path.basename(input_path)
            current_app.logger.info(
                f'input path: {input_path}, file name : {filename}')
            message_json = {
                'project': self.project,
                'destination_geid': destination_geid,
                'input_geid': input_geid,
                'input_path': input_path,
                'output_path': output_path,
                'logfile': '/'.join(log_path),
                'uploader': uploader,
                'process_pipeline': ConfigClass.copy_pipeline,
                'create_time': self.create_time,
                'request_id': request_id,
                'dcm_id': dcm_id,
                'session_id': session_id,
                'job_id': job_id,
                'operator': operator,
                'operation_type': operation_type,
                'auth_token': auth_token
            }
            self.producer.publish(message_json)
            return res
        except Exception as e:
            current_app.logger.error(f'Error when trying to parse the message to queue: {e}')
            res.set_result('Error when trying to parse the message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res

    def file_move(self, payload):
        current_app.logger.info(self.routing_key + "  ---------event sending.")
        res = APIResponse()
        try:
            input_geid = payload.get('input_geid', None)
            input_path = payload.get('input_path', None)
            uploader = payload.get('uploader', None)
            dcm_id = payload.get('dcm_id', None)
            output_path = payload.get('output_path', None)
            session_id = payload.get('session_id', 'default_session')
            job_id = payload.get('job_id', 'default_job')
            operator = payload.get('operator', None)
            trash_path = payload.get('trash_path', None)
            namespace = payload.get('namespace', None)
            path_list = str(input_path).split('/')
            auth_token = payload.get('auth_token', {"at":"", "rt":""})

            if not input_path or not uploader or not output_path:
                res.set_result('Missing required information')
                res.set_code(EAPIResponseCode.bad_request)
                return res
            filename = os.path.basename(input_path)
            current_app.logger.info(
                f'input path: {input_path}, file name : {filename}')
            message_json = {
                'project': self.project,
                'input_geid': input_geid,
                'input_path': input_path,
                'output_path': output_path,
                'trash_path': trash_path,
                'uploader': uploader,
                'process_pipeline': ConfigClass.move_pipeline,
                'create_time': self.create_time,
                'dcm_id': dcm_id,
                'session_id': session_id,
                'job_id': job_id,
                'operator': operator,
                'namespace': namespace,
                'auth_token': auth_token
            }
            self.producer.publish(message_json)
            return res
        except Exception as e:
            current_app.logger.error(f'Error when trying to parse the message to queue: {e}')
            res.set_result('Error when trying to parse the message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res

    def transparently_produce(self, payload):
        current_app.logger.info(self.routing_key + "  ---------event sending.")
        res = APIResponse()
        try:
            self.producer.publish(payload)
            res.set_code(EAPIResponseCode.success)
            res.set_result(payload)
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
        res.set_result('Undefined event type for Filecopy operation')
        res.set_code(EAPIResponseCode.bad_request)
        return res


class ProducerDcm(NormalProducer):
    # Init dcmedit project producer, including all dcmedit related function,
    # and different event type will be mapped to different function
    # for different event type, the published message may differ from each other
    # invalid_event function as the default function used for undefined event
    def dcm_uploaded(self, payload):
        res = APIResponse()
        try:
            input_geid = payload.get('input_geid', None)
            input_path = payload.get('input_path', None)
            dcm_id = payload.get('dcm_id', None)
            uploader = payload.get('uploader', None)
            auth_token = payload.get('auth_token', {"at":"", "rt":""})
            if not input_path or not dcm_id or not uploader:
                res.set_result('Missing required information')
                res.set_code(EAPIResponseCode.bad_request)
                return res
            output_path = '/'.join(input_path.split('/')[:-1])
            # check if file typs is zip
            file_type = input_path[-4:]
            current_app.logger.info(
                f'input path: {input_path}, file type : {file_type}')
            if file_type == '.zip':
                message_json = {
                    'project': self.project,
                    'input_geid': input_geid,
                    'input_path': input_path,
                    'pipeline': ConfigClass.dcm_pipeline,
                    'output_path': output_path,
                    'work_path': ConfigClass.WORK_PATH,
                    'log_path': ConfigClass.LOG_PATH,
                    'dcm_id': dcm_id,
                    'uploader': uploader,
                    'create_time': self.create_time,
                    'auth_token': auth_token
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

    def dcm_processed(self, payload):
        res = APIResponse()
        try:
            input_geid = payload.get('input_geid', None)
            input_path = payload.get('input_path', None)
            dcm_id = payload.get('dcm_id', None)
            uploader = payload.get('uploader', None)
            pipeline = payload.get('pipeline', None)
            if not input_path or not dcm_id or not uploader:
                res.set_result('Missing required information')
                res.set_code(EAPIResponseCode.bad_request)
                return res
            filename = os.path.basename(input_path)
            output_path = ConfigClass.data_storage + '/' + \
                self.project + '/' + pipeline + '/' + filename
            current_app.logger.info(
                f'input path: {input_path}, file name : {filename}')
            message_json = {
                'project': self.project,
                'input_geid': input_geid,
                'input_path': input_path,
                'pipeline': pipeline,
                'output_path': output_path,
                'dcm_id': dcm_id,
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
        res.set_result(f'Undefined event type for {ConfigClass.DCM_PROJECT} project')
        res.set_code(EAPIResponseCode.bad_request)
        return res
