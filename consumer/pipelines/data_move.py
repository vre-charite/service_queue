from config import ConfigClass
from job import KubernetesApiClient
from kubernetes.client.rest import ApiException
import time

def run_pipeline(logger, input_path, output_path,
    trash_path, project_code, event_payload, auth_token):
    #create kubernetes job to run Generate 'dcm_edit' pipeline
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/file_move.py"]
    args = ["-i", input_path, "-o", output_path, "-t", trash_path,
        "-env", ConfigClass.env, "-p", event_payload["project"], "-op", event_payload["operator"], '-at', 
        auth_token["at"], '-rt', auth_token["rt"]]

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
            event_payload)
            
        api_response = job_api_client.create_namespaced_job(
            namespace=ConfigClass.namespace,
            body=job)
        logger.info(api_response.status)
        logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return

def folder_delete_pipeline(logger, input_geid,
    trash_path, project_code, event_payload, auth_token):
    #create kubernetes job to run Generate 'folder_delete_pipeline'
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/folder_move.py"]
    args = ["-i", input_geid, "-t", trash_path,
        "-env", ConfigClass.env, "-p", event_payload["project"], "-op", event_payload["operator"], '-at', 
        auth_token["at"], '-rt', auth_token["rt"]]

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
            event_payload)
            
        api_response = job_api_client.create_namespaced_job(
            namespace=ConfigClass.namespace,
            body=job)
        logger.info(api_response.status)
        logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return
