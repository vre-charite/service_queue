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
    dcm_id,
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

    logger.info(f"The vault url is: {ConfigClass.VAULT_URL}")
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
            dcm_id,
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
