class ConfigClass(object):
    # the packaged modules
    api_modules = ["queue_op"]    

    #greenroom queue
    gm_queue_endpoint = 'message-bus-greenroom.greenroom'
    gm_username = 'greenroom'
    gm_password = 'indoc101'

    # folders been watched
    data_lake = "/data/vre-storage"

    #pipeline name
    generate_pipeline='dicom_edit'

    #data ops gateway url
    data_ops_endpoint = "http://dataops-gr.greenroom:5063"