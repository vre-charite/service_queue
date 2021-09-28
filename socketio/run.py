import eventlet
import socketio
import asyncio
from aiohttp import web
import nest_asyncio
from config import ConfigClass

import pickle

nest_asyncio.apply()

mgr = socketio.AsyncAioPikaManager('amqp://%s:%s@%s/'%(ConfigClass.gm_username, \
    ConfigClass.gm_password, ConfigClass.gm_queue_endpoint), "socketio")
sio = socketio.AsyncServer(cors_allowed_origins="*", engineio_logger=True, logger=True)
app = web.Application()
sio.attach(app)


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)



# @asyncio.coroutine
async def rab_init():
    print("Start the socket io")
    while 1:
        queue_message = await mgr._listen()
        print()
        print("print all message: ", queue_message)
        print()
        # skip the echod message
        if queue_message.get("method") == "emit":
            continue

        print("recieving from queue: ", queue_message)
        dataset_geid = queue_message.get("payload", {}).get("dataset")
        event_type = queue_message.get("event_type", None)

        await sio.emit(event_type, queue_message, namespace='/'+dataset_geid)

def start_rabbitmq(loop):
    asyncio.ensure_future(rab_init())
    loop.run_forever()

async def start_socket():
    web.run_app(app, port=6062)

##############################################################

loop = asyncio.get_event_loop()
asyncio.ensure_future(start_socket())
asyncio.ensure_future(rab_init())
loop.run_forever()

