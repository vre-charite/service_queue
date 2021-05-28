import os 
class ConfigClass(object):
    env = os.environ.get('env')
    # the packaged modules
    api_modules = ["queue_op"]    

    #greenroom queue
    gm_queue_endpoint = 'message-bus-greenroom.greenroom'
    gm_username = 'greenroom'
    gm_password = 'indoc101'
    if env == 'charite':
        gm_password = 'rabbitmq-jrjmfa9svvC'

    # folders been watched
    data_lake = '/data/vre-storage'
    vre_data_storage = '/vre-data'

    #pipeline name
    generate_pipeline ='dicom_edit'
    copy_pipeline = 'data_transfer'
    move_pipeline = 'data_delete'

    #greenroom queue
    gr_queue = 'gr_queue'
    gr_exchange = 'gr_exchange'

