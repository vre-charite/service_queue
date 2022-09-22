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

from config import ConfigClass
from job import KubernetesApiClient
from kubernetes.client.rest import ApiException


def run_pipeline(
    logger,
    input_path,
    output_path,
    trash_path,
    project_code,
    event_payload,
    auth_token,
):
    logger.info(f"The vault url is: {ConfigClass.VAULT_URL}")
    logger.info(f'Received token: {auth_token}')
    volume_path = ConfigClass.data_lake
    command = ['/usr/bin/python3', 'scripts/file_move.py']
    args = [
        '-i',
        input_path,
        '-o',
        output_path,
        '-t',
        trash_path,
        '-j',
        event_payload['job_id'],
        '-env',
        ConfigClass.env,
        '-p',
        event_payload['project'],
        '-op',
        event_payload['operator'],
        '-at',
        auth_token['at'],
        '-rt',
        auth_token['rt'],
    ]

    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.move_job_obj(
            'data-delete-' + project_code + str(round(time.time() * 10000)),
            ConfigClass.data_transfer_image,
            volume_path,
            command,
            args,
            project_code,
            auth_token,
            event_payload,
        )

        api_response = job_api_client.create_namespaced_job(namespace=ConfigClass.namespace, body=job)
        logger.info(api_response.status)
        # logger.info(api_response)
        return api_response
    except ApiException:
        logger.exception('An ApiException exception occurred while running file_move pipeline')
        return


def folder_delete_pipeline(
    logger,
    input_geid,
    trash_path,
    project_code,
    event_payload,
    auth_token,
):
    volume_path = ConfigClass.data_lake
    command = ['/usr/bin/python3', 'scripts/folder_move.py']
    args = [
        '-i',
        input_geid,
        '-t',
        trash_path,
        '-j',
        event_payload['job_id'],
        '-env',
        ConfigClass.env,
        '-p',
        event_payload['project'],
        '-op',
        event_payload['operator'],
        '-at',
        auth_token['at'],
        '-rt',
        auth_token['rt'],
    ]

    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.move_folder_job_obj(
            'data-delete-folder-' + project_code + str(round(time.time() * 10000)),
            ConfigClass.data_transfer_image,
            volume_path,
            command,
            args,
            project_code,
            auth_token,
            event_payload,
        )

        api_response = job_api_client.create_namespaced_job(namespace=ConfigClass.namespace, body=job)
        logger.info(api_response.status)
        # logger.info(api_response)
        return api_response
    except ApiException:
        logger.exception('An ApiException exception occurred while running folder_move pipeline')
        return
