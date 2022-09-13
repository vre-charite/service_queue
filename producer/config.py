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

import os
from functools import lru_cache
from typing import Any
from typing import Dict

from pydantic import BaseSettings
from pydantic import Extra
from common import VaultClient
from dotenv import load_dotenv

# load env var from local env file
load_dotenv()
SRV_NAMESPACE = os.environ.get('APP_NAME', 'service_queue')
CONFIG_CENTER_ENABLED = os.environ.get('CONFIG_CENTER_ENABLED', 'false')


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        vc = VaultClient(os.getenv("VAULT_URL"), os.getenv("VAULT_CRT"), os.getenv("VAULT_TOKEN"))
        return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    """Store service configuration settings."""

    APP_NAME: str = 'service_queue'
    version: str = '0.2.0'
    port: int = 6060
    host: str = '0.0.0.0'
    env: str = 'test'

    gm_queue_endpoint: str
    gm_username: str
    gm_password: str
    # folders been watched
    data_storage: str
    # pipeline name
    dcm_pipeline: str = 'dicom_edit'
    copy_pipeline: str = 'data_transfer'
    move_pipeline: str = 'data_delete'
    # greenroom queue
    gr_queue: str = 'gr_queue'
    gr_exchange: str = 'gr_exchange'
    WORK_PATH: str = '/tmp/workdir'
    LOG_PATH: str = '/tmp/logs'

    OPEN_TELEMETRY_ENABLED: str = "FALSE"
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831
    DCM_PROJECT: str

    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return load_vault_settings, env_settings, init_settings, file_secret_settings


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings


ConfigClass = Settings()
