from config import ConfigClass
from job import KubernetesApiClient
from kubernetes.client.rest import ApiException
import datetime

def run_pipeline(logger, input_path, output_path, log_file, project_code = None):
    #create kubernetes job to run Generate 'dcm_edit' pipeline
    volume_path = ConfigClass.data_lake
    command = ["/usr/bin/python3", "scripts/file_copy.py"]
    args = ["-i", input_path, "-o", output_path, "-l", log_file]
    try:
        api_client = KubernetesApiClient()
        job_api_client = api_client.create_batch_api_client()
        job_name = ConfigClass.tvbc_copy_pipeline
        job = api_client.tvb_c_copy_job_obj(
            "data-transfer-tvb-c-" + str(round(datetime.datetime.now().timestamp())),
            ConfigClass.tvbc_copy_image,
            volume_path,
            command,
            args,
            project_code)
        api_response = job_api_client.create_namespaced_job(
            namespace=ConfigClass.namespace,
            body=job)
        logger.info(api_response.status)
        logger.info(api_response)
        return api_response
    except ApiException as e:
        logger.exception(e)
        return
