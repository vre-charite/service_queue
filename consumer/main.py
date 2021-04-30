from config import ConfigClass
from consumer import QueueConsumer
from job import KubernetesApiClient
from kubernetes.client.rest import ApiException
from pipelines.data_copy import run_pipeline as run_data_copy
from pipelines.data_move import run_pipeline as run_data_move
import logging
import requests
import pika
import time
import json
import os 
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def millis():
    current_milli_time = str(round(time.time() * 1000))

    return current_milli_time

def generate_pipeline( input_path, output_path, work_path, log_file, job_name, project, generate_id, uploader, event_payload):
    #create kubernetes job to run Generate 'dcm_edit' pipeline
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/dcm_edit.py"]
    args = [ "-i", input_path, "-o", output_path, "-t", work_path, "-l", log_file, "-p", project, "-s", generate_id]
    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.create_job_object(job_name, ConfigClass.dcmedit_image, volume_path, command, args, uploader, event_payload)
        api_response = job_api_client.create_namespaced_job(
            namespace=ConfigClass.namespace,
            body=job)
        logger.info(api_response.status)
        logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return

def generate_pipeline_common( input_path, output_path, work_path, log_file, job_name, project, generate_id, uploader, event_payload):
    #create kubernetes job to run Generate 'dcm_edit' pipeline
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/dcm_edit.py"]
    args = [ "-i", input_path, "-o", output_path, "-t", work_path, "-l", log_file, "-p", project, "-s", generate_id,
    "--use-default-anonymization"]
    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.create_job_object(job_name, ConfigClass.dcmedit_image, volume_path, command, args, uploader, event_payload)
        api_response = job_api_client.create_namespaced_job(
            namespace=ConfigClass.namespace,
            body=job)
        logger.info(api_response.status)
        logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return

def callback(ch, method, properties, body):
    #received message and start to consume message
    logger.info(" [x] Received %r" % body)
    message = json.loads(body) 
    if method.routing_key =='generate.data_uploaded':
        output_path = message['output_path']
        log_file = message['log_path']+'/'+ConfigClass.generate_pipeline+'.log'
        isExists = os.path.exists(output_path)
        generate_id = message['generate_id']
        logger.info(f'GenerateID is {generate_id}')
        job_name = message['project']+'-'+ millis()
        try:
            if not isExists:
                os.makedirs(output_path)
            if not os.path.exists(log_file):
                os.mknod(log_file)
            result = generate_pipeline(
                message['input_path'], 
                output_path,
                message['work_path'], 
                log_file, 
                job_name.lower(),
                message['project'],
                generate_id,
                message['uploader'],
                message)
            logger.info(result)
            logger.info("pipeline is processing")
            ch.basic_ack(delivery_tag = method.delivery_tag)
        except Exception as e:
            logger.exception(f'Error occurred while copying file. {e}')
            ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)
    elif method.routing_key.split('.')[-1] == 'file_copy':
        try:
            logger.info('manual data copy triggered')
            logger.info(message)
            input_path = message['input_path']
            output_path = message['output_path']
            logfile = message['logfile']
            generate_id = message['generate_id']
            uploader = message['uploader']
            try:
                result = run_data_copy(logger, input_path, output_path, logfile,
                    method.routing_key.split('.')[0], uploader, generate_id, message)
                logger.info(result)
                logger.info("pipeline is processing")
                ch.basic_ack(delivery_tag = method.delivery_tag)
            except Exception as e:
                logger.exception(f'Error occurred while copying file. {e}')
                ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)
        except Exception as e:
            logger.exception(f'Error occurred while copying file. {e}')
            ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False) 
    elif method.routing_key.split('.')[-1] == 'file_delete':
        try:
            logger.info('manual data deletion triggered')
            logger.info(message)
            input_path = message['input_path']
            output_path = message['output_path']
            trash_path = message['trash_path']
            try:
                result = run_data_move(logger, input_path, output_path, trash_path, 
                    method.routing_key.split('.')[0], message)
                logger.info(result)
                logger.info("pipeline is processing")
                ch.basic_ack(delivery_tag = method.delivery_tag)
            except Exception as e:
                logger.exception(f'Error occurred while moving file. {e}')
                ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)
        except Exception as e:
            logger.exception(f'Error occurred while moving file. {e}')
            ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)        
    else:
        logger.exception('Undefined Routing key')
        ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)
        


def main():
    # define log formatter and location
    # initialize queue connection and consume messages
    # routing key set up to '#' means consume all routes in connected queue
    if not os.path.exists('./logs'):
        print(os.path.exists('./logs'))
        os.makedirs('./logs')
    formatter = logging.Formatter('%(asctime)s - %(name)s - \
                              %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('./logs/consumer.log')
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    # Standard Out Handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.DEBUG)
    # Standard Err Handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    stderr_handler.setLevel(logging.ERROR)
    # register handlers
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    consumer = QueueConsumer(routing_key='#', exchange_name=ConfigClass.gr_exchange, exchange_type='topic', queue=ConfigClass.gr_queue)
    consumer.channel.basic_qos(prefetch_count=1)
    consumer.channel.basic_consume(
        queue=consumer.queue, 
        on_message_callback=callback)     
    logger.info('Start consuming')
    consumer.channel.start_consuming()

if __name__ == "__main__":
    main()
