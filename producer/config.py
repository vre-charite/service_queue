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
    else:
        gm_password = 'indoc101'

    # folders been watched
    data_lake = '/data/vre-storage'
    vre_data_storage = '/vre-data'

    #pipeline name
    generate_pipeline ='dicom_edit'
    copy_pipeline = 'data_transfer'
    move_pipeline = 'data_delete'

    #data ops gateway url
    data_ops_endpoint = "http://dataops-gr.greenroom:5063"

    #greenroom queue
    gr_queue = 'gr_queue'
    gr_exchange = 'gr_exchange'

