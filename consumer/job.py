import logging
import sys,os, time
from kubernetes import client, config, utils
from config import ConfigClass

class KubernetesApiClient(object):
    #This class is used to init kubernetes job client and include create job function
    def __init__(self):
        # load kubernetes configuration
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        self.configuration = client.Configuration()

    def create_batch_api_client(self):
            return client.BatchV1Api(client.ApiClient(self.configuration))

    def create_job_object(self, job_name, container_image, volume_path, command, args, uploader):
            # define the persistent volume claim and mount pvc to k8s job container
            pvc = client.V1PersistentVolumeClaimVolumeSource(
                claim_name = ConfigClass.claim_name,
                read_only = False
            )
            volume = client.V1Volume(
                persistent_volume_claim = pvc,
                name = 'nfsvol'
            )
            volume_mount = client.V1VolumeMount(
                mount_path=volume_path,
                name = 'nfsvol'
            )
            # vre core mount
            vre_core_pvc = client.V1PersistentVolumeClaimVolumeSource(
                claim_name = ConfigClass.vre_core_pvc_name,
                read_only = False
            )
            vre_core_volume = client.V1Volume(
                persistent_volume_claim = vre_core_pvc,
                name = ConfigClass.vre_core_volume_name
            )
            vre_core_volume_mount = client.V1VolumeMount(
                mount_path= ConfigClass.vre_core,
                name = ConfigClass.vre_core_volume_name
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
            template = client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(labels={"pipeline": ConfigClass.generate_pipeline},
                                                    annotations={"input_file":args[1],
                                                                "output_path":args[3],
                                                                "uploader": uploader}),
                        spec=client.V1PodSpec(restart_policy="Never", 
                                            containers=[container],
                                            volumes=[volume, vre_core_volume],
                                            node_selector={"namespace":ConfigClass.namespace}))
                                            
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
        event_payload):
        # define the persistent volume claim and mount pvc to k8s job container
        pvc = client.V1PersistentVolumeClaimVolumeSource(
            claim_name = ConfigClass.claim_name,
            read_only = False
        )
        volume = client.V1Volume(
            persistent_volume_claim = pvc,
            name = 'nfsvol'
        )
        volume_mount = client.V1VolumeMount(
            mount_path=volume_path,
            name = 'nfsvol'
        )
        # vre core mount
        vre_core_pvc = client.V1PersistentVolumeClaimVolumeSource(
            claim_name = ConfigClass.vre_core_pvc_name,
            read_only = False
        )
        vre_core_volume = client.V1Volume(
            persistent_volume_claim = vre_core_pvc,
            name = ConfigClass.vre_core_volume_name
        )
        vre_core_volume_mount = client.V1VolumeMount(
            mount_path= ConfigClass.vre_core,
            name = ConfigClass.vre_core_volume_name
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
            "input_path":args[1],
            "output_path":args[3],
            "project": project_code,
            "generate_id":generate_id,
            "uploader": uploader,
        }
        for key in event_payload:
            anno['event_payload_' + key] = str(event_payload[key] )
        template = client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                    labels={"pipeline": ConfigClass.copy_pipeline},
                                                annotations=anno),
                    spec=client.V1PodSpec(restart_policy="Never", 
                                        containers=[container],
                                        volumes=[volume, vre_core_volume],
                                        node_selector={"namespace":ConfigClass.namespace}))
                                        
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
