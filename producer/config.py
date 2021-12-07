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
    host: str = "0.0.0.0"
    env: str = "test"

    gm_queue_endpoint: str
    gm_username: str
    gm_password: str
    # folders been watched
    data_lake: str = '/data/vre-storage'
    vre_data_storage: str = '/vre-data'
    #pipeline name
    generate_pipeline: str ='dicom_edit'
    copy_pipeline: str = 'data_transfer'
    move_pipeline: str = 'data_delete'
    #greenroom queue
    gr_queue: str = 'gr_queue'
    gr_exchange: str = 'gr_exchange'
    WORK_PATH: str = '/tmp/workdir'
    LOG_PATH: str = '/tmp/logs'
    
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

    version = "0.2.0"
    env = settings.env

    gm_queue_endpoint = settings.gm_queue_endpoint
    gm_username = settings.gm_username
    gm_password = settings.gm_password
    # folders been watched
    data_lake = settings.data_lake
    vre_data_storage = settings.vre_data_storage
    #pipeline name
    generate_pipeline = settings.generate_pipeline
    copy_pipeline = settings.copy_pipeline
    move_pipeline = settings.move_pipeline
    #greenroom queue
    gr_queue = settings.gr_queue
    gr_exchange = settings.gr_exchange

    WORK_PATH = settings.WORK_PATH
    LOG_PATH = settings.LOG_PATH