import socketio
import asyncio
from aiohttp import web
import nest_asyncio

from config import ConfigClass
from message_queue import MessageQueue


nest_asyncio.apply()
sio = socketio.AsyncServer(cors_allowed_origins="*", engineio_logger=True, logger=True)
app = web.Application()
sio.attach(app)

loop = asyncio.get_event_loop()
mq_manager = MessageQueue(ConfigClass.gm_queue_endpoint, ConfigClass.gm_username, \
    ConfigClass.gm_password, loop, "socketio")


@sio.event
def connect(sid, environ):
    '''
    Summary:
        SocketIO connection echo
    '''
    print("connect ", sid)


@sio.event
def disconnect(sid):
    '''
    Summary:
        SocketIO disconnection echo 
    '''
    print('disconnect ', sid)


async def rab_init() -> None:
    '''
    Summary:
        Async function to run in the event loop. It will recieve the 
        notification from rabbitqm and use socketio to send to frontend
    '''

    print("Start the socket io")
    await mq_manager.connect()
    while 1:
        queue_message = await mq_manager.get_message()
        # skip the echo message
        if queue_message.get("method") == "emit":
            continue
        
        # based on the dataset info in message
        # send the notification to target dataset
        print("recieving from queue: ", queue_message)
        dataset_geid = queue_message.get("payload", {}).get("dataset")
        event_type = queue_message.get("event_type", None)

        await sio.emit(event_type, queue_message, namespace='/'+dataset_geid)


async def start_socket():
    '''
    Summary:
        the socketio initialization function
    '''
    web.run_app(app, port=6062)

##############################################################


asyncio.ensure_future(start_socket())
asyncio.ensure_future(rab_init())
loop.run_forever()

