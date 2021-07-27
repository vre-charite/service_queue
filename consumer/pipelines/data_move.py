from config import ConfigClass
from job import KubernetesApiClient
from kubernetes.client.rest import ApiException
import time

def run_pipeline(logger, input_path, output_path,
    trash_path, project_code, event_payload):
    #create kubernetes job to run Generate 'dcm_edit' pipeline
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/file_move.py"]
    args = ["-i", input_path, "-o", output_path, "-t", trash_path,
        "-env", ConfigClass.env, "-p", event_payload["project"], "-op", event_payload["operator"]]
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
