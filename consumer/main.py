import json
import os
import time

from kubernetes.client.rest import ApiException

from config import ConfigClass
from consumer import QueueConsumer
from job import KubernetesApiClient
from logger_services.logger_factory_service import SrvLoggerFactory
from pipelines.bids_validate import run_pipeline as run_bids_validate
from pipelines.data_copy import folder_copy_pipeline as run_folder_copy
from pipelines.data_copy import run_pipeline as run_data_copy
from pipelines.data_move import folder_delete_pipeline as run_folder_delete
from pipelines.data_move import run_pipeline as run_data_move

logger = SrvLoggerFactory('pipeline_message_consumer').get_logger()


def millis():
    current_milli_time = str(round(time.time() * 1000))

    return current_milli_time


def generate_pipeline(
    input_path,
    output_path,
    work_path,
    log_file,
    job_name,
    project,
    generate_id,
    uploader,
    auth_token,
    event_payload,
):
    # create kubernetes job to run Generate 'dcm_edit' pipeline
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/dcm_edit.py"]
    env = os.environ.get('env')
    args = ["-i", input_path, "-o", output_path, "-t", work_path,
            "-l", log_file, "-p", project, "-s", generate_id, "-env", env,
            '-at', auth_token["at"], '-rt', auth_token["rt"]]
    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.create_job_object(
            job_name, ConfigClass.dcmedit_image, volume_path, command, args,
            uploader, auth_token, event_payload)
        api_response = job_api_client.create_namespaced_job(
            namespace=ConfigClass.namespace,
            body=job)

        logger.info(api_response.status)
        logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return


def generate_pipeline_common(
    input_path,
    output_path,
    work_path,
    log_file,
    job_name,
    project,
    generate_id,
    uploader,
    event_payload,
):
    # create kubernetes job to run Generate 'dcm_edit' pipeline
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/dcm_edit.py"]
    args = ["-i", input_path, "-o", output_path, "-t", work_path, "-l", log_file, "-p", project, "-s", generate_id,
            "--use-default-anonymization"]
    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.create_job_object(
            job_name, ConfigClass.dcmedit_image, volume_path, command, args, uploader, event_payload)
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
    # received message and start to consume message
    logger.info(" [x] Received %r" % body)
    message = json.loads(body)
    if method.routing_key == 'generate.data_uploaded':
        output_path = message['output_path']
        auth_token = message['auth_token']
        log_file = message['log_path']+'/'+ConfigClass.generate_pipeline+'.log'
        generate_id = message['generate_id']
        logger.info(f'GenerateID is {generate_id}')
        job_name = message['project']+'-' + millis()

        try:
            result = generate_pipeline(
                message['input_path'],
                output_path,
                message['work_path'],
                log_file,
                job_name.lower(),
                message['project'],
                generate_id,
                message['uploader'],
                auth_token,
                message)
            # logger.info(result)
            logger.info("generate.data_uploaded pipeline is processing")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.exception(f'Error occurred while copying file. {e}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    elif method.routing_key.split('.')[-1] == 'bids_validate':
        try:
            logger.info('manual bids validate triggered')
            logger.info(message)
            dataset_geid = message['dataset_geid']
            refresh_token = message['refresh_token']
            access_token = message['access_token']
            try:
                result = run_bids_validate(
                    logger, dataset_geid, access_token, refresh_token)
                # logger.info(result)
                logger.info("bids_validate pipeline is processing")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.exception(
                    f'Error occurred while validate bids dataset. {e}')
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            logger.exception(
                f'Error occurred while validate bids dataset. {e}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    elif method.routing_key.split('.')[-1] == 'file_copy':
        try:
            logger.info(f'file_copy message has been received: {message}')
            input_path = message['input_path']
            output_path = message['output_path']
            request_id = message.get('request_id')
            generate_id = message['generate_id']
            uploader = message['uploader']
            auth_token = message['auth_token']

            try:
                result = run_data_copy(
                    logger,
                    input_path,
                    output_path,
                    method.routing_key.split('.')[0],
                    uploader,
                    request_id,
                    generate_id,
                    message,
                    auth_token,
                )
                # logger.info(result)
                logger.info('file_copy pipeline is processing')
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.exception(f'Error occurred while copying file. {e}')
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            logger.exception(f'Error occurred while copying file. {e}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    elif method.routing_key.split('.')[-1] == 'file_delete':
        try:
            logger.info('manual data deletion triggered')
            logger.info(message)
            input_path = message['input_path']
            output_path = message['output_path']
            trash_path = message['trash_path']
            auth_token = message['auth_token']
            try:
                result = run_data_move(logger, input_path, output_path, trash_path,
                                       method.routing_key.split('.')[0], message, auth_token)
                # logger.info(result)
                logger.info("file_delete pipeline is processing")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.exception(f'Error occurred while moving file. {e}')
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.exception(f'Error occurred while moving file. {e}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    elif method.routing_key.split('.')[-1] == 'folder_copy':
        try:
            logger.info(f'folder_copy message has been received: {message}')
            input_ = message['input_geid']
            output = message['destination_geid']
            uploader = message['uploader']
            request_id = message.get('request_id')
            auth_token = message['auth_token']
            try:
                result = run_folder_copy(
                    logger,
                    input_,
                    output,
                    method.routing_key.split('.')[0],
                    uploader,
                    request_id,
                    message,
                    auth_token,
                )
                # logger.info(result)
                logger.info('folder_copy pipeline is processing')
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.exception(f'Error occurred while moving file. {e}')
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.exception(f'Error occurred while moving file. {e}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    elif method.routing_key.split('.')[-1] == 'folder_delete':
        try:
            logger.info(message)
            input_geid = message['input_geid']
            trash_path = message['trash_path']
            auth_token = message['auth_token']
            try:
                result = run_folder_delete(logger,
                    input_geid,
                    trash_path,
                    method.routing_key.split('.')[0],
                    message,
                    auth_token)
                # logger.info(result)
                logger.info("folder_delete pipeline is processing")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.exception(f'Error occurred while moving file. {e}')
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.exception(f'Error occurred while moving file. {e}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    else:
        logger.exception('Undefined Routing key')
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    # define log formatter and location
    # initialize queue connection and consume messages
    # routing key set up to '#' means consume all routes in connected queue
    if not os.path.exists('./logs'):
        print(os.path.exists('./logs'))
        os.makedirs('./logs')
    consumer = QueueConsumer(routing_key='#', exchange_name=ConfigClass.gr_exchange,
                             exchange_type='topic', queue=ConfigClass.gr_queue)
    consumer.channel.basic_qos(prefetch_count=1)
    consumer.channel.basic_consume(
        queue=consumer.queue,
        on_message_callback=callback)
    logger.info('=========================Start consuming================================')
    logger.info(ConfigClass.gr_exchange)
    logger.info(ConfigClass.gr_queue)
    consumer.channel.start_consuming()


if __name__ == "__main__":
    main()
