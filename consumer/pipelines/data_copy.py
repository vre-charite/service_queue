import time
from typing import Optional

from config import ConfigClass
from job import KubernetesApiClient
from kubernetes.client.rest import ApiException


def run_pipeline(
    logger,
    input_path,
    output_path,
    project_code,
    uploader,
    request_id: Optional[str],
    generate_id,
    event_payload,
    auth_token,
):
    logger.info(f'Received token: {auth_token}')
    volume_path = ConfigClass.data_lake
    command = ['/usr/bin/python3', 'scripts/file_copy.py']
    args = [
        '-i',
        input_path,
        '-o',
        output_path,
        '-env',
        ConfigClass.env,
        '-p',
        event_payload['project'],
        '-op',
        event_payload['operator'],
        '-j',
        event_payload['job_id'],
        '-at',
        auth_token['at'],
        '-rt',
        auth_token['rt'],
    ]

    if request_id:
        args.extend(['--request-id', request_id])

    logger.info(f'Creating job using command {command} and args {args}')

    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.copy_job_obj(
            'data-transfer-' + project_code + str(round(time.time() * 10000)),
            ConfigClass.data_transfer_image,
            volume_path,
            command,
            args,
            project_code,
            uploader,
            generate_id,
            auth_token,
            event_payload,
        )
        # start the job
        logger.info(f"The namespace is: {ConfigClass.namespace}")
        api_response = job_api_client.create_namespaced_job(namespace=ConfigClass.namespace, body=job)
        logger.info(api_response.status)
        # logger.info(api_response)
        return api_response
    except ApiException:
        logger.exception('An ApiException exception occurred while running file_copy pipeline')
        return


def folder_copy_pipeline(
    logger,
    input_geid,
    dest_geid,
    project_code,
    uploader,
    request_id: Optional[str],
    event_payload,
    auth_token,
):
    logger.info(f'Received token: {auth_token}')
    volume_path = ConfigClass.data_lake
    command = ['/usr/bin/python3', 'scripts/folder_copy.py']
    args = [
        '-i',
        input_geid,
        '-o',
        dest_geid,
        '-env',
        ConfigClass.env,
        '-p',
        event_payload['project'],
        '-op',
        event_payload['operator'],
        '-j',
        event_payload['job_id'],
        '-at',
        auth_token['at'],
        '-rt',
        auth_token['rt'],
    ]

    if request_id:
        args.extend(['--request-id', request_id])

    logger.info(f'Creating job using command {command} and args {args}')

    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.copy_folder_job_obj(
            'data-transfer-folder-' + project_code + str(round(time.time() * 10000)),
            ConfigClass.data_transfer_image,
            volume_path,
            command,
            args,
            project_code,
            uploader,
            auth_token,
            event_payload,
        )
        # start the job
        api_response = job_api_client.create_namespaced_job(namespace=ConfigClass.namespace, body=job)
        logger.info(api_response.status)
        # logger.info(api_response)
        return api_response
    except ApiException:
        logger.exception('An ApiException exception occurred while running folder_copy pipeline')
        return
