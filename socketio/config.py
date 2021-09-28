import os 

class ConfigClass(object):
    version = "0.1.0"
    env = os.environ.get('env', 'test')
    if env == 'test':   
        #greenroom queue
        gm_queue_endpoint = '10.3.7.232'
        gm_username = 'greenroom'
        gm_password = 'indoc101'
    elif env == 'charite': 
        #greenroom queue
        gm_queue_endpoint = 'message-bus-greenroom.greenroom'
        gm_username = 'greenroom'
        gm_password = 'rabbitmq-jrjmfa9svvC'
    else: 
        #greenroom queue
        gm_queue_endpoint = 'message-bus-greenroom.greenroom'
        gm_username = 'greenroom'
        gm_password = 'indoc101'
