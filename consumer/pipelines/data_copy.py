from config import ConfigClass
from job import KubernetesApiClient
from kubernetes.client.rest import ApiException
import time

def run_pipeline(logger, input_path, output_path,
    project_code, uploader, generate_id, event_payload,
    auth_token):

    logger.info("recieve token: "+str(auth_token))

    #create kubernetes job to run Generate 'dcm_edit' pipeline
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/file_copy.py"]
    args = ["-i", input_path, "-o", output_path,
        "-env", ConfigClass.env, "-p", event_payload["project"], "-op", event_payload["operator"],
        "-j", event_payload["job_id"], '-at', auth_token["at"], '-rt', auth_token["rt"]]
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
            event_payload)

        # start the job
        api_response = job_api_client.create_namespaced_job(
            namespace=ConfigClass.namespace,
            body=job)
        logger.info(api_response.status)
        logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return

def folder_copy_pipeline(logger, input_geid, dest_geid,
    project_code, uploader, event_payload,
    auth_token):
    logger.info("recieve token: "+str(auth_token))
    #create kubernetes job to run Generate 'folder_copy_pipeline'
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/folder_copy.py"]
    args = ["-i", input_geid, "-o", dest_geid,
        "-env", ConfigClass.env, "-p", event_payload["project"], "-op", event_payload["operator"],
        "-j", event_payload["job_id"], '-at', auth_token["at"], '-rt', auth_token["rt"],
        "-r", event_payload["rename"]]
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
            event_payload)
        # start the job
        api_response = job_api_client.create_namespaced_job(
            namespace=ConfigClass.namespace,
            body=job)
        logger.info(api_response.status)
        logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return