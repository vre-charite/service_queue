import os
import requests
from requests.models import HTTPError

# os.environ['env'] = 'test'
srv_namespace = "service_queue"
CONFIG_CENTER = "http://10.3.7.222:5062" \
    if os.environ.get('env') == "test" \
    else "http://common.utility:5062"


def vault_factory() -> dict:
    url = CONFIG_CENTER + \
        "/v1/utility/config/{}".format(srv_namespace)
    config_center_respon = requests.get(url)
    if config_center_respon.status_code != 200:
        raise HTTPError(config_center_respon.text)
    return config_center_respon.json()['result']


class ConfigClass(object):
    vault = vault_factory()
    env = os.environ.get('env')
    disk_namespace = os.environ.get('namespace')
    CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED")
    CONFIG_CENTER_BASE_URL = os.environ.get("CONFIG_CENTER_BASE_URL")
    version = "0.1.0"
    # disk mounts
    NFS_ROOT_PATH = "./"
    VRE_ROOT_PATH = "/vre-data"
    ROOT_PATH = {
        "vre": "/vre-data"
    }.get(os.environ.get('namespace'), "/data/vre-storage")

    # the packaged modules
    api_modules = ["queue_op"]
    # greenroom queue
    gm_queue_endpoint = vault['gm_queue_endpoint']
    gm_username = vault['gm_username']

    gm_password = vault['gm_password']
    vre_core_nfs_path = vault['vre_core_nfs_path']
    vre_core_nfs_server = vault['vre_core_nfs_server']

    # folders been watched
    data_lake = "/data/vre-storage"
    claim_name = "greenroom-storage"

    # vre core mount
    vre_core = "/vre-data"
    vre_core_volume_name = "nfsvol-vre-data"

    # pipeline name
    generate_pipeline = 'dicom_edit'

    # data ops gateway url
    data_ops_endpoint = "http://dataops-gr.greenroom:5063"

    # dag generator url
    # dag_generator_endpoint= "http://dag-generator.utility:5000"
    dag_generator_endpoint = vault['dag_generator_endpoint']
    file_process_on_create_endpoint = data_ops_endpoint + \
        "/v1/containers/1/files/process/on-create"
    # namespace in kubernetes cluster
    namespace = 'greenroom'

    # dicom pipeline image
    docker_ip = os.environ.get('docker-registry-ip')
    dcmedit_image = docker_ip + \
        ':5000/dcmedit:v0.1' if docker_ip else '10.3.7.221:5000/dcmedit:v0.1'

    # data_transfer pipeline
    data_transfer_image = docker_ip + \
        ':5000/filecopy:v0.1' if docker_ip else '10.3.7.221:5000/filecopy:v0.1'
    bids_validate_image = docker_ip + \
        ':5000/bids-validator:v0.1' if docker_ip else '10.3.7.221:5000/bids-validator:v0.1'
    copy_pipeline = 'data_transfer'
    copy_pipeline_folder = 'data_transfer_folder'
    move_pipeline = 'data_delete'
    move_pipeline_folder = 'data_delete_folder'
    bids_validate_pipeline = 'bids_validate'

    # greenroom queue
    gr_queue = 'gr_queue'
    gr_exchange = 'gr_exchange'

    # trigger pipeline
