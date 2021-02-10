import os
class ConfigClass(object):
    # the packaged modules
    api_modules = ["queue_op"]    

    #greenroom queue
    gm_queue_endpoint = 'message-bus-greenroom.greenroom'
    gm_username = 'greenroom'
    env = os.environ.get('env')
    if env == 'charite':
        gm_password = 'rabbitmq-jrjmfa9svvC'
        vre_core_pvc_name = 'greenroom-vre-storage'
    else:
        gm_password = 'indoc101'
        vre_core_pvc_name = "greenroom-storage-vre-data"

    # folders been watched
    data_lake = "/data/vre-storage"
    claim_name = "greenroom-storage"

    # vre core mount
    vre_core = "/vre-data"
    vre_core_volume_name = "nfsvol-vre-data"

    #pipeline name
    generate_pipeline='dicom_edit'

    #data ops gateway url
    data_ops_endpoint = "http://dataops-gr.greenroom:5063"

    #dag generator url
    # dag_generator_endpoint= "http://dag-generator.utility:5000"
    dag_generator_endpoint= "http://10.3.7.236:5000"
    file_process_on_create_endpoint = data_ops_endpoint + "/v1/containers/1/files/process/on-create"

    #namespace in kubernetes cluster
    namespace = 'greenroom'

    #dicom pipeline image
    docker_ip = os.environ.get('docker-registry-ip') 
    dcmedit_image = docker_ip + ':5000/dcmedit:v0.1' if docker_ip else '10.3.7.221:5000/dcmedit:v0.1'

    #data_transfer pipeline
    data_transfer_image = docker_ip + ':5000/filecopy:v0.1' if docker_ip else '10.3.7.221:5000/filecopy:v0.1'
    copy_pipeline = 'data_transfer'
    move_pipeline = 'data_delete'
    
    #greenroom queue
    gr_queue = 'gr_queue'
    gr_exchange = 'gr_exchange'

# trigger pipeline

