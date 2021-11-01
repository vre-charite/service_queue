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

    def create_job_object(self, job_name, container_image, volume_path, command, args, 
        uploader, auth_token, event_payload):
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

        # vre core mount
        vre_core_nfs = client.V1NFSVolumeSource(
            path=ConfigClass.vre_core_nfs_path,
            server=ConfigClass.vre_core_nfs_server,
            read_only=False
        )
        vre_core_volume = client.V1Volume(
            nfs=vre_core_nfs,
            name=ConfigClass.vre_core_volume_name
        )
        vre_core_volume_mount = client.V1VolumeMount(
            mount_path=ConfigClass.vre_core,
            name=ConfigClass.vre_core_volume_name
        )
        container = client.V1Container(
            name=job_name,
            image=container_image,
            command=command,
            args=args,
            volume_mounts=[volume_mount, vre_core_volume_mount],
            image_pull_policy="Always")
        # parse annotation
        anno = {
            "input_file": args[1],
            "output_path": args[3],
            "uploader": uploader,
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        # metadata defined in annotations part
        # node selector defined how to assgin work nodes when creating job container
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"pipeline": ConfigClass.generate_pipeline},
                                         annotations=anno),
            spec=client.V1PodSpec(restart_policy="Never",
                                  containers=[container],
                                  volumes=[volume, vre_core_volume],
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

    def bids_validate_job_obj(self, job_name, container_image,
                              volume_path, command, args, dataset_geid, access_token, refresh_token):
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
               name='CONFIG_CENTER_BASE_URL',
               value=ConfigClass.CONFIG_CENTER_BASE_URL), 
           client.V1EnvVar(
               name='CONFIG_CENTER_ENABLED',
               value=ConfigClass.CONFIG_CENTER_ENABLED)
               ]
        
        # vre core mount
        vre_core_nfs = client.V1NFSVolumeSource(
            path=ConfigClass.vre_core_nfs_path,
            server=ConfigClass.vre_core_nfs_server,
            read_only=False
        )
        vre_core_volume = client.V1Volume(
            nfs=vre_core_nfs,
            name=ConfigClass.vre_core_volume_name
        )
        vre_core_volume_mount = client.V1VolumeMount(
            mount_path=ConfigClass.vre_core,
            name=ConfigClass.vre_core_volume_name
        )
        container = client.V1Container(
            name=job_name,
            image=container_image,
            command=command,
            args=args,
            env=env,
            volume_mounts=[volume_mount, vre_core_volume_mount],
            image_pull_policy="Always")
        # metadata defined in annotations part
        # node selector defined how to assgin work nodes when creating job container
        anno = {
            "dataset": dataset_geid,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"pipeline": ConfigClass.bids_validate_pipeline},
                annotations=anno),
            spec=client.V1PodSpec(restart_policy="Never",
                                  containers=[container],
                                  volumes=[volume, vre_core_volume],
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


    def copy_job_obj(self, job_name, container_image,
                     volume_path, command, args, project_code, uploader, generate_id,
                     auth_token, event_payload):
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
        # vre core mount
        vre_core_nfs = client.V1NFSVolumeSource(
            path=ConfigClass.vre_core_nfs_path,
            server=ConfigClass.vre_core_nfs_server,
            read_only=False
        )
        vre_core_volume = client.V1Volume(
            nfs=vre_core_nfs,
            name=ConfigClass.vre_core_volume_name
        )
        vre_core_volume_mount = client.V1VolumeMount(
            mount_path=ConfigClass.vre_core,
            name=ConfigClass.vre_core_volume_name
        )
        container = client.V1Container(
            name=job_name,
            image=container_image,
            command=command,
            args=args,
            volume_mounts=[volume_mount, vre_core_volume_mount],
            image_pull_policy="Always")

        # metadata defined in annotations part
        # node selector defined how to assgin work nodes when creating job container
        anno = {
            "input_path": args[1],
            "output_path": args[3],
            "project": project_code,
            "generate_id": generate_id,
            "uploader": uploader,
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"pipeline": ConfigClass.copy_pipeline},
                annotations=anno),
            spec=client.V1PodSpec(restart_policy="Never",
                                  containers=[container],
                                  volumes=[volume, vre_core_volume],
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

    def copy_folder_job_obj(self, job_name, container_image,
                     volume_path, command, args, project_code, uploader,
                     auth_token, event_payload):
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
        # vre core mount
        vre_core_nfs = client.V1NFSVolumeSource(
            path=ConfigClass.vre_core_nfs_path,
            server=ConfigClass.vre_core_nfs_server,
            read_only=False
        )
        vre_core_volume = client.V1Volume(
            nfs=vre_core_nfs,
            name=ConfigClass.vre_core_volume_name
        )
        vre_core_volume_mount = client.V1VolumeMount(
            mount_path=ConfigClass.vre_core,
            name=ConfigClass.vre_core_volume_name
        )
        container = client.V1Container(
            name=job_name,
            image=container_image,
            command=command,
            args=args,
            volume_mounts=[volume_mount, vre_core_volume_mount],
            image_pull_policy="Always")

        # metadata defined in annotations part
        # node selector defined how to assgin work nodes when creating job container
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
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"pipeline": ConfigClass.copy_pipeline_folder},
                annotations=anno),
            spec=client.V1PodSpec(restart_policy="Never",
                                  containers=[container],
                                  volumes=[volume, vre_core_volume],
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

    def move_job_obj(self, job_name, container_image,
                     volume_path, command, args, project_code,
                     auth_token, event_payload):
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
        # vre core mount
        vre_core_nfs = client.V1NFSVolumeSource(
            path=ConfigClass.vre_core_nfs_path,
            server=ConfigClass.vre_core_nfs_server,
            read_only=False
        )
        vre_core_volume = client.V1Volume(
            nfs=vre_core_nfs,
            name=ConfigClass.vre_core_volume_name
        )
        vre_core_volume_mount = client.V1VolumeMount(
            mount_path=ConfigClass.vre_core,
            name=ConfigClass.vre_core_volume_name
        )
        container = client.V1Container(
            name=job_name,
            image=container_image,
            command=command,
            args=args,
            volume_mounts=[volume_mount, vre_core_volume_mount],
            image_pull_policy="Always")
        # metadata defined in annotations part
        # node selector defined how to assgin work nodes when creating job container
        anno = {
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"pipeline": ConfigClass.move_pipeline},
                annotations=anno),
            spec=client.V1PodSpec(restart_policy="Never",
                                  containers=[container],
                                  volumes=[volume, vre_core_volume],
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

    def copy_folder_job_obj(self, job_name, container_image,
                     volume_path, command, args, project_code, uploader,
                     auth_token, event_payload):
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
        # vre core mount
        vre_core_nfs = client.V1NFSVolumeSource(
            path=ConfigClass.vre_core_nfs_path,
            server=ConfigClass.vre_core_nfs_server,
            read_only=False
        )
        vre_core_volume = client.V1Volume(
            nfs=vre_core_nfs,
            name=ConfigClass.vre_core_volume_name
        )
        vre_core_volume_mount = client.V1VolumeMount(
            mount_path=ConfigClass.vre_core,
            name=ConfigClass.vre_core_volume_name
        )
        container = client.V1Container(
            name=job_name,
            image=container_image,
            command=command,
            args=args,
            volume_mounts=[volume_mount, vre_core_volume_mount],
            image_pull_policy="Always")

        # metadata defined in annotations part
        # node selector defined how to assgin work nodes when creating job container
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
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"pipeline": ConfigClass.copy_pipeline_folder},
                annotations=anno),
            spec=client.V1PodSpec(restart_policy="Never",
                                  containers=[container],
                                  volumes=[volume, vre_core_volume],
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

    def move_folder_job_obj(self, job_name, container_image,
                     volume_path, command, args,
                     project_code, auth_token, event_payload):
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
        # vre core mount
        vre_core_nfs = client.V1NFSVolumeSource(
            path=ConfigClass.vre_core_nfs_path,
            server=ConfigClass.vre_core_nfs_server,
            read_only=False
        )
        vre_core_volume = client.V1Volume(
            nfs=vre_core_nfs,
            name=ConfigClass.vre_core_volume_name
        )
        vre_core_volume_mount = client.V1VolumeMount(
            mount_path=ConfigClass.vre_core,
            name=ConfigClass.vre_core_volume_name
        )
        container = client.V1Container(
            name=job_name,
            image=container_image,
            command=command,
            args=args,
            volume_mounts=[volume_mount, vre_core_volume_mount],
            image_pull_policy="Always")
        # metadata defined in annotations part
        # node selector defined how to assgin work nodes when creating job container
        anno = {
            "at": auth_token["at"],
            "rt": auth_token["rt"],
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key])
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"pipeline": ConfigClass.move_pipeline_folder},
                annotations=anno),
            spec=client.V1PodSpec(restart_policy="Never",
                                  containers=[container],
                                  volumes=[volume, vre_core_volume],
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
