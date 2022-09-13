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
from typing import List

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
    port: int = 6060
    host: str = '127.0.0.1'
    env: str = 'test'
    namespace: str = 'greenroom'

    CONFIG_CENTER_ENABLED: str
    VAULT_URL: str
    VAULT_CRT: str
    VAULT_TOKEN: str

    # greenroom queue
    gm_queue_endpoint: str
    gm_username: str
    gm_password: str
    core_nfs_path: str
    core_nfs_server: str

    # folders been watched
    data_lake: str
    claim_name: str = 'greenroom-storage'

    # core mount
    core_mount: str
    core_volume_name: str

    # pipeline name
    dcm_pipeline: str = 'dicom_edit'

    # dicom pipeline image
    dcmedit_image: str = ""

    # data_transfer pipeline
    data_transfer_image: str = ""
    bids_validate_image: str = ""

    # data_transfer pipeline
    copy_pipeline: str = 'data_transfer'
    copy_pipeline_folder: str = 'data_transfer_folder'
    move_pipeline: str = 'data_delete'
    move_pipeline_folder: str = 'data_delete_folder'
    bids_validate_pipeline: str = 'bids_validate'

    # greenroom queue
    gr_queue: str = 'gr_queue'
    gr_exchange: str = 'gr_exchange'

    OPEN_TELEMETRY_ENABLED: str = "FALSE"
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831

    KEYCLOAK_ENDPOINT: str
    SQL_DB_NAME: str
    GR_ZONE_LABEL: str
    CORE_ZONE_LABEL: str
    MINIO_ENDPOINT: str
    DCM_PROJECT: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return env_settings, load_vault_settings, init_settings, file_secret_settings


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings

ConfigClass = Settings()
