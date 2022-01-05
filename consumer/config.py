import os
import requests
from requests.models import HTTPError
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache

SRV_NAMESPACE = os.environ.get("APP_NAME", "service_queue")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")
CONFIG_CENTER_BASE_URL = os.environ.get("CONFIG_CENTER_BASE_URL", "NOT_SET")

def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        return vault_factory(CONFIG_CENTER_BASE_URL)

def vault_factory(config_center) -> dict:
    url = f"{config_center}/v1/utility/config/{SRV_NAMESPACE}"
    config_center_respon = requests.get(url)
    if config_center_respon.status_code != 200:
        raise HTTPError(config_center_respon.text)
    return config_center_respon.json()['result']


class Settings(BaseSettings):
    port: int = 6060
    host: str = "127.0.0.1"
    env: str = "test"
    namespace: str = "greenroom"
    
    CONFIG_CENTER_ENABLED: str
    CONFIG_CENTER_BASE_URL: str

    # disk mounts
    NFS_ROOT_PATH: str = "./"
    VRE_ROOT_PATH: str = "/vre-data"
    ROOT_PATH: str = {
        "vre": "/vre-data"
    }.get('namespace', "/data/vre-storage")

    # the packaged modules
    api_modules: List[str] = ["queue_op"]
    # greenroom queue
    gm_queue_endpoint: str
    gm_username: str

    gm_password: str
    vre_core_nfs_path: str
    vre_core_nfs_server: str

    # folders been watched
    data_lake: str = "/data/vre-storage"
    claim_name: str = "greenroom-storage"

    # vre core mount
    vre_core: str = "/vre-data"
    vre_core_volume_name: str = "nfsvol-vre-data"

    # pipeline name
    generate_pipeline: str = 'dicom_edit'

    # data ops gateway url
    DATA_OPS_GR: str

    # dag generator url
    dag_generator_endpoint: str

    # dicom pipeline image
    docker_registry_ip: str = "10.3.7.221"
    copy_pipeline: str = 'data_transfer'
    copy_pipeline_folder: str = 'data_transfer_folder'
    move_pipeline: str = 'data_delete'
    move_pipeline_folder: str = 'data_delete_folder'
    bids_validate_pipeline: str = 'bids_validate'

    # greenroom queue
    gr_queue: str = 'gr_queue'
    gr_exchange: str = 'gr_exchange'

    # trigger pipeline
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                load_vault_settings,
                env_settings,
                init_settings,
                file_secret_settings,
            )
    

@lru_cache(1)
def get_settings():
    settings =  Settings()
    return settings

class ConfigClass(object):
    settings = get_settings()

    version = "0.1.0"
    env = settings.env
    disk_namespace = settings.namespace
    
    CONFIG_CENTER_ENABLED = settings.CONFIG_CENTER_ENABLED
    CONFIG_CENTER_BASE_URL = settings.CONFIG_CENTER_BASE_URL

    # disk mounts
    NFS_ROOT_PATH = settings.NFS_ROOT_PATH
    VRE_ROOT_PATH = settings.VRE_ROOT_PATH
    ROOT_PATH = settings.ROOT_PATH

    # the packaged modules
    api_modules = settings.api_modules
    # greenroom queue
    gm_queue_endpoint = settings.gm_queue_endpoint
    gm_username = settings.gm_username

    gm_password = settings.gm_password
    vre_core_nfs_path = settings.vre_core_nfs_path
    vre_core_nfs_server = settings.vre_core_nfs_server

    # folders been watched
    data_lake = settings.data_lake
    claim_name = settings.claim_name

    # vre core mount
    vre_core = settings.vre_core
    vre_core_volume_name = settings.vre_core_volume_name

    # pipeline name
    generate_pipeline = settings.generate_pipeline

    # data ops gateway url
    data_ops_endpoint = settings.DATA_OPS_GR

    # dag generator url
    # dag_generator_endpoint= "http://dag-generator.utility:5000"
    dag_generator_endpoint = settings.dag_generator_endpoint
    file_process_on_create_endpoint = data_ops_endpoint + \
        "/v1/containers/1/files/process/on-create"
    # namespace in kubernetes cluster
    namespace = settings.namespace

    # dicom pipeline image
    docker_ip = settings.docker_registry_ip
    dcmedit_image = docker_ip + '/dcmedit:v0.1'

    # data_transfer pipeline
    data_transfer_image = docker_ip + '/filecopy:v0.1'
    bids_validate_image = docker_ip + '/bids-validator:v0.1'
    copy_pipeline = settings.copy_pipeline
    copy_pipeline_folder = settings.copy_pipeline_folder
    move_pipeline = settings.move_pipeline
    move_pipeline_folder = settings.move_pipeline_folder
    bids_validate_pipeline = settings.bids_validate_pipeline

    # greenroom queue
    gr_queue = settings.gr_queue
    gr_exchange = settings.gr_exchange

    # trigger pipeline
