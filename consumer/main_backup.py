from config import ConfigClass
from consumer import QueueConsumer
from job import KubernetesApiClient
from kubernetes.client.rest import ApiException
import logging
import requests
import pika
import time
import json
import os 

logger = logging.getLogger(__name__)

def millis():
    current_milli_time = str(round(time.time() * 1000))

    return current_milli_time

def generate_pipeline( input_path, output_path, work_path, log_file, job_name, project, generate_id, uploader):
    #create kubernetes job to run Generate 'dcm_edit' pipeline
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/dcm_edit.py"]
    args = [ "-i", input_path, "-o", output_path, "-t", work_path, "-l", log_file, "-p", project, "-s", generate_id]
    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.create_job_object(job_name, ConfigClass.dcmedit_image, volume_path, command, args, uploader)
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
                output_path, message['work_path'], 
                log_file, 
                job_name.lower(),
                message['project'],
                generate_id,message['uploader'])
            logger.info(result)
            logger.info("pipeline is processing")
            ch.basic_ack(delivery_tag = method.delivery_tag)
        except Exception as e:
            logger.exception(f'Error occurred while copying file. {e}')
            ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)
    elif method.routing_key == 'tvbcloud.data_uploaded':
        try:
            logger.info('tvbcloud data uploaded')
            url = ConfigClass.dag_generator_endpoint+'/'
            logger.info(message)
            res = requests.post(url, json=message)
            logger.info('response for data copy')
            if res.status_code == 202:
                dag_info = json.loads(res.text)
                ch.basic_ack(delivery_tag = method.delivery_tag)
                logger.info('status_code for invoking dag generator: {}'.format(res.status_code))
                # stream file_process_on_create event to pipelinewatch
                on_create_url = ConfigClass.file_process_on_create_endpoint
                res_on_create = requests.post(on_create_url, json=dag_info)
                logger.info('status_code for invoking pipelinewatch: {}'.format(res_on_create.status_code))
                if res_on_create.status_code == 200:
                    logger.info('Succeed: stream pipeline events')
                else:
                    logger.exception(json.loads(res_on_create.text))
            else:
                logger.exception(json.loads(res.text))
                ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)
        except Exception as e:
            logger.exception(f'Error occurred while copying file. {e}')
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
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    consumer = QueueConsumer(routing_key='#', exchange_name=ConfigClass.gr_exchange, exchange_type='topic', queue=ConfigClass.gr_queue)
    consumer.channel.basic_qos(prefetch_count=1)
    consumer.channel.basic_consume(
        queue=consumer.queue, 
        on_message_callback=callback)     
    logger.info('Start consuming')
    consumer.channel.start_consuming()

if __name__ == "__main__":
    main()
