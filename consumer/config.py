import os
class ConfigClass(object):
    # the packaged modules
    api_modules = ["queue_op"]    

    #greenroom queue
    gm_queue_endpoint = 'message-bus-greenroom.greenroom'
    gm_username = 'greenroom'
    gm_password = 'indoc101'

    # folders been watched
    data_lake = "/data/vre-storage"
    claim_name = "greenroom-storage"

    #pipeline name
    generate_pipeline='dicom_edit'

    #data ops gateway url
    data_ops_endpoint = "http://dataops-gr.greenroom:5063"

    #namespace in kubernetes cluster
    namespace = 'greenroom'

    #dicom pipeline image
    docker_ip = os.environ.get('docker-registry-ip') 
    image = docker_ip+':5000/dcmedit:v0.1' if docker_ip else '10.3.7.221:5000/dcmedit:v0.1'
    
    