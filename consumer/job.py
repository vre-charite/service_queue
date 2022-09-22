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

import logging
import sys
import os
import time
from kubernetes import client, config, utils
from config import ConfigClass


class KubernetesApiClient(object):
    # This class is used to init kubernetes job client and include create job function
    def __init__(self):
        # load kubernetes configuration
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        self.configuration = client.Configuration()

    def create_batch_api_client(self):
        return client.BatchV1Api(client.ApiClient(self.configuration))
    
    def create_job(self, job_name, container_image, volume_path, command, args, pipeline,anno):
        # define the persistent volume claim and mount pvc to k8s job container
        pvc = client.V1PersistentVolumeClaimVolumeSource(
            claim_name=ConfigClass.claim_name,
            read_only=False
        )
        volume = client.V1Volume(
            persistent_volume_claim=pvc,
            name='nfsvol'
        )
        volume_mount = client.V1VolumeMount(
            mount_path=volume_path,
            name='nfsvol'
        )

        #Create environment variables for container.
        env = [
            client.V1EnvVar(
               name='CONFIG_CENTER_ENABLED',
               value=ConfigClass.CONFIG_CENTER_ENABLED), 
            client.V1EnvVar(
               name='KEYCLOAK_ENDPOINT',
               value=ConfigClass.KEYCLOAK_ENDPOINT),
            client.V1EnvVar(
               name='SQL_DB_NAME',
               value=ConfigClass.SQL_DB_NAME),
            client.V1EnvVar(
               name='GR_ZONE_LABEL',
               value=ConfigClass.GR_ZONE_LABEL),
            client.V1EnvVar(
               name='CORE_ZONE_LABEL',
               value=ConfigClass.CORE_ZONE_LABEL),
            client.V1EnvVar(
               name='VAULT_URL',
               value=ConfigClass.VAULT_URL),
            client.V1EnvVar(
               name='VAULT_CRT',
               value=ConfigClass.VAULT_CRT),
            client.V1EnvVar(
               name='VAULT_TOKEN',
               value=ConfigClass.VAULT_TOKEN),
            client.V1EnvVar(
               name='MINIO_ENDPOINT',
               value=ConfigClass.MINIO_ENDPOINT),
            client.V1EnvVar(
               name='DCM_PROJECT',
               value=ConfigClass.DCM_PROJECT)
               ]

        # core mount
        core_nfs = client.V1NFSVolumeSource(
            path=ConfigClass.core_nfs_path,
            server=ConfigClass.core_nfs_server,
            read_only=False
        )
        core_volume = client.V1Volume(
            nfs=core_nfs,
            name=ConfigClass.core_volume_name
        )
        core_volume_mount = client.V1VolumeMount(
            mount_path=ConfigClass.core_mount,
            name=ConfigClass.core_volume_name
        )
        container = client.V1Container(
            name=job_name,
            image=container_image,
            command=command,
            args=args,
            env=env,
            volume_mounts=[volume_mount, core_volume_mount],
            image_pull_policy="Always")
        
        # metadata defined in annotations part
        # node selector defined how to assgin work nodes when creating job container
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"pipeline": pipeline},
                                         annotations=anno),
            spec=client.V1PodSpec(restart_policy="Never",
                                  containers=[container],
                                  volumes=[volume, core_volume],
                                  node_selector={"namespace": ConfigClass.namespace}))

        spec = client.V1JobSpec(
            template=template,
            backoff_limit=0,
            completions=1,
            ttl_seconds_after_finished=60)
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=job_name),
            spec=spec)
        
        return job

    # Create dcmedit job, rename to be more understandable
    def dcm_job_object(self, job_name, container_image, volume_path, command, args, 
        uploader, auth_token, event_payload):
        # define the persistent volume claim and mount pvc to k8s job container
        anno = {
            "input_file": args[1],
            "output_path": args[3],
            "uploader": uploader,
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        
        job = self.create_job(job_name, container_image, volume_path, 
                              command, args, ConfigClass.dcm_pipeline, anno)

        return job
        

    def bids_validate_job_obj(self, job_name, container_image,
                              volume_path, command, args, dataset_geid, access_token, refresh_token):
        # define the persistent volume claim and mount pvc to k8s job container
        anno = {
            "dataset": dataset_geid,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

        job = self.create_job(job_name, container_image, volume_path, 
                              command, args, ConfigClass.bids_validate_pipeline, anno)

        return job


    def copy_job_obj(self, job_name, container_image,
                     volume_path, command, args, project_code, uploader, dcm_id,
                     auth_token, event_payload):
        # define the persistent volume claim and mount pvc to k8s job container
        
        anno = {
            "input_path": args[1],
            "output_path": args[3],
            "project": project_code,
            "dcm_id": dcm_id,
            "uploader": uploader,
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        
        job = self.create_job(job_name, container_image, volume_path, 
                              command, args, ConfigClass.copy_pipeline, anno)

        return job

    def copy_folder_job_obj(self, job_name, container_image,
                     volume_path, command, args, project_code, uploader,
                     auth_token, event_payload):
        # define the persistent volume claim and mount pvc to k8s job container
        anno = {
            "input": args[1],
            "output": args[3],
            "project": project_code,
            "uploader": uploader,
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        
        job = self.create_job(job_name, container_image, volume_path, 
                              command, args, ConfigClass.copy_pipeline_folder, anno)

        return job

    def move_job_obj(self, job_name, container_image,
                     volume_path, command, args, project_code,
                     auth_token, event_payload):
        # define the persistent volume claim and mount pvc to k8s job container
        anno = {
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        
        job = self.create_job(job_name, container_image, volume_path, 
                              command, args, ConfigClass.move_pipeline, anno)

        return job

    def copy_folder_job_obj(self, job_name, container_image,
                     volume_path, command, args, project_code, uploader,
                     auth_token, event_payload):
        # define the persistent volume claim and mount pvc to k8s job container
        anno = {
            "input": args[1],
            "output": args[3],
            "project": project_code,
            "uploader": uploader,
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        
        job = self.create_job(job_name, container_image, volume_path, 
                              command, args, ConfigClass.copy_pipeline_folder, anno)

        return job

    def move_folder_job_obj(self, job_name, container_image,
                     volume_path, command, args,
                     project_code, auth_token, event_payload):
        # define the persistent volume claim and mount pvc to k8s job container
        anno = {
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        
        job = self.create_job(job_name, container_image, volume_path, 
                              command, args, ConfigClass.move_pipeline_folder, anno)

        return job
