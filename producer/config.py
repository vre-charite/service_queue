import os 
class ConfigClass(object):
    version = "0.2.0"
    env = os.environ.get('env', 'test')
    if env == 'test':   
        #greenroom queue
        gm_queue_endpoint = '10.3.7.232'
        gm_username = 'greenroom'
        gm_password = 'indoc101'
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
        WORK_PATH = '/tmp/workdir'
        LOG_PATH = '/tmp/logs'
    elif env == 'charite': 
        #greenroom queue
        gm_queue_endpoint = 'message-bus-greenroom.greenroom'
        gm_username = 'greenroom'
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
        WORK_PATH = '/tmp/workdir'
        LOG_PATH = '/tmp/logs'
    else: 
        #greenroom queue
        gm_queue_endpoint = 'message-bus-greenroom.greenroom'
        gm_username = 'greenroom'
        gm_password = 'indoc101'
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

        WORK_PATH = '/tmp/workdir'
        LOG_PATH = '/tmp/logs'

