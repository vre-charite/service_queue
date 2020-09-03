import logging
import pika
import os
from config import ConfigClass
import json
import requests
from kubernetes.client.rest import ApiException
from job import KubernetesApiClient, Constant
import time


logger = logging.getLogger(__name__)

def millis():
    current_milli_time = str(round(time.time() * 1000))

    return current_milli_time

def get_queue_connection(username, password, endpoint):
    try:
        # channel
        credentials = pika.PlainCredentials(
            username,
            password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=endpoint,
                heartbeat=60,
                credentials=credentials)
        )
        logger.info('Successed Initiated queue connection')
        return connection
    except Exception as e:
        logger.error(f'Error when connecting to queue service: {e}')
        raise

def queue_declare(channel):
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

def generate_pipeline(input_path, output_path, work_path, log_file, job_name, project, generate_id, uploader, create_time):
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/dcm_edit.py"]
    args = [ "-i", input_path, "-o", output_path, "-t", work_path, "-l", log_file, "-p", project, "-s", generate_id]
    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.create_job_object(job_name, ConfigClass.image, volume_path, command, args, uploader, create_time)
        api_response = job_api_client.create_namespaced_job(
            namespace=Constant.NAMESPACE,
            body=job)
        logger.info(api_response.status)
        logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return

def callback(ch, method, properties, body):
    logger.info(" [x] Received %r" % body)
    message = json.loads(body)
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
        result = generate_pipeline(message['input_path'], output_path, message['work_path'], log_file, job_name.lower(),message['project'],generate_id,message['uploader'],message['create_time'])
        logger.info(result)
        logger.info("pipeline is processing")
        ch.basic_ack(delivery_tag = method.delivery_tag)
    except Exception as e:
        logger.exception(f'Error occurred while copying file. {e}')
        ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)
        return
    

def main():
    # connect to the queue
    if not os.path.exists('./logs'):
        print(os.path.exists('./logs'))
        os.makedirs('./logs')
    formatter = logging.Formatter('%(asctime)s - %(name)s - \
                              %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('./logs/consumer.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    conn = get_queue_connection(ConfigClass.gm_username,ConfigClass.gm_password,ConfigClass.gm_queue_endpoint)
    channel = conn.channel()
    queue_declare(channel)
    # This uses the basic.qos protocol method to tell RabbitMQ not to give more than one message to a worker at a time.
    channel.basic_qos(prefetch_count=1)
    # Manual message acknowledgments are turned on by default.
    logger.info('Basic consume')
    channel.basic_consume(queue='gq1', on_message_callback=callback)
    logger.info('Start consuming')
    channel.start_consuming()

if __name__ == "__main__":
    main()
