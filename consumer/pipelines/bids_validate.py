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

from config import ConfigClass
from job import KubernetesApiClient
from kubernetes.client.rest import ApiException
import time


def run_pipeline(logger, dataset_geid, access_token, refresh_token):
    # create kubernetes job to run bids validator pipeline
    logger.info(f"The vault url is: {ConfigClass.VAULT_URL}")
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/validate_dataset.py"]
    args = ["-d", dataset_geid, "-access", access_token,
            "-refresh", refresh_token, "-env", ConfigClass.env]
    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job = api_client.bids_validate_job_obj(
            'bids-validate-' + str(round(time.time() * 10000)),
            ConfigClass.bids_validate_image,
            volume_path,
            command,
            args,
            dataset_geid,
            access_token,
            refresh_token)

        api_response = job_api_client.create_namespaced_job(
            namespace=ConfigClass.namespace,
            body=job)
        logger.info(api_response.status)
        # logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return
