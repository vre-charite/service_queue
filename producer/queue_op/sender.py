from flask import request, current_app
from flask_restx import Api, Resource, fields
from models.api_response import APIResponse, EAPIResponseCode
import pika
from config import ConfigClass
import json 
import filetype

class Queue_sender(Resource):
    def post(self):
        try: 
            res = APIResponse()
            post_data = request.get_json()
            event_type = post_data.get('event_type', None)
            payload = post_data.get('payload', None)
            create_time = post_data.get('create_timestamp', None)
            current_app.logger.info(f'postData is : {post_data}')
            if event_type != 'data_uploaded':
                current_app.logger.exception('Wrong event type')
                res.set_result('EWrong event type')
                res.set_code(EAPIResponseCode.bad_request)
                return res.response, res.code
            if not post_data or not payload:
                current_app.logger.exception('Empty Message')
                res.set_result('Empty Message in the queue')
                res.set_code(EAPIResponseCode.not_found)
            else:
                send_to_queue(payload, create_time)
            return res.response, res.code
        except Exception as e:
            current_app.logger.exception(f'Error when sending message to queue: {e}')
            res.set_result('Error when sending message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res.response, res.code


def get_queue_connection(username, password, endpoint):
        try:
            # channel
            credentials = pika.PlainCredentials(
                username,
                password)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=endpoint,
                    heartbeat=0,
                    credentials=credentials)
            )
            current_app.logger.info('Successed Initiated queue connection')
            return connection
        except Exception as e:
            current_app.logger.error(f'Error when connecting to queue service: {e}')
            raise


def send_to_queue(payload, create_time):        
        try: 
            res = APIResponse()
            project = payload.get('project', None)
            input_path = payload.get('input_path', None)
            generate_id = payload.get('generate_id', None)
            uploader = payload.get('uploader', None)
            if not input_path or not project or not generate_id or not uploader:
                res.set_result('Missing required information')
                res.set_code(EAPIResponseCode.bad_request)
                return res.response, res.code
            path_list = str(input_path).split('/')
            if len(path_list) != 6:
                    res.set_result('Not a valid path')
                    res.set_code(EAPIResponseCode.bad_request)
                    return res.response, res.code
            base_path = path_list[:4]
            work_path = path_list[:4]
            log_path = path_list[:4]
            work_path.append('workdir')
            log_path.append('logs')
            base_path.append('processed')
            base_path.append(ConfigClass.generate_pipeline)
            current_app.logger.info(base_path)
            file_type = filetype.guess(input_path)
            current_app.logger.info(f'input path: {input_path}, file type : {file_type}')
            if ''.join(project.split()).upper() == 'GENERATE':
                if file_type is None:
                    current_app.logger.error('Can not recognize file type')
                    res.set_result('Invalid File Type')
                    res.set_code(EAPIResponseCode.bad_request) 
                else: 
                    if file_type.extension == 'zip':
                        message_json = {
                            'project': project.upper(),
                            'input_path': input_path,
                            'pipeline': ConfigClass.generate_pipeline,
                            'output_path': '/'.join(base_path),
                            'work_path': '/'.join(work_path),
                            'log_path': '/'.join(log_path),
                            'generate_id': generate_id,
                            'uploader': uploader,
                            'create_time': create_time
                        }
                        current_app.logger.info(message_json)
                        generate_queue(message_json)
                    else:
                        current_app.logger.error(f'Wrong file type: {file_type}')
                        res.set_result('Invalid File Type')
                        res.set_code(EAPIResponseCode.bad_request)        
            else:
                current_app.logger.error(f'Not belong to Generate project.  Project Name:  {project}')
                res.set_result('Not belong to Generate Project')
                res.set_code(EAPIResponseCode.bad_request)
            return res.response, res.code
        except FileNotFoundError as not_found:
            current_app.logger.error(f'File not found in given path: {not_found}')
            res.set_result(f'File not found: {not_found.filename}')
            res.set_code(EAPIResponseCode.bad_request)
        except Exception as e:
            current_app.logger.error(f'Error when trying to parse the message to queue: {e}')
            res.set_result('Error when trying to parse the message to queue')
            res.set_code(EAPIResponseCode.internal_error)
            return res.response, res.code    
            
def generate_queue(generate_message):
        conn = get_queue_connection(ConfigClass.gm_username,ConfigClass.gm_password,ConfigClass.gm_queue_endpoint)
        channel = conn.channel()
        res = APIResponse()
        # exchange
        channel.exchange_declare(
            exchange='ge1', 
            exchange_type='direct')
        # queue
        channel.queue_declare(
            queue='gq1', 
            durable=True)
        # queue exchange binding
        channel.queue_bind(
            exchange='ge1', 
            queue="gq1", 
            routing_key="gk1")
        # public message to exchange
        try:
            channel.basic_publish(
                exchange='ge1',
                routing_key='gk1',
                body=json.dumps(generate_message),
                properties=pika.BasicProperties(
                    delivery_mode = 2, # make message persistent
                )
            )
            current_app.logger.info(" [x] Sent %r"%generate_message)
            channel.confirm_delivery() # confirm the delivery to exchange
            conn.close()
            res.set_result('Sent Message successfully to the queue')
            res.set_code(EAPIResponseCode.success)
            return res.response, res.code
        except pika.exceptions.UnroutableError:
            current_app.logger.error("Failed to send message %r" % generate_message)
            res.set_result('Failed to send message')
            res.set_code(EAPIResponseCode.internal_error)
            return res.response, res.code   