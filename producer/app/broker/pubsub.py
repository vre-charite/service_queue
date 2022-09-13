# Copyright 2022 Indoc Research
# 
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# 
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# 
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# 

import json
import pika
import pickle
from .rabbit_operator import RabbitConnection
from .consumer_dynamic import ConsumerDynamic, eventhook
from .sub_list import SubscriberList

def do_publish(queue, routing_key, body,
        exchange_name, exchange_type, binary=False):
    # publish a event to all subscribers
    my_rabbit = RabbitConnection()
    connection_instance = my_rabbit.init_connection()
    channel = connection_instance.channel()
    channel.queue_declare(queue=queue)
    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type=exchange_type)
    channel.queue_bind(
            exchange=exchange_name,
            queue=queue,
            routing_key=routing_key)
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        # for socketio, we will send the binary hex
        body=pickle.dumps(body) if binary else json.dumps(body),
        properties=pika.BasicProperties(
            delivery_mode = 2, # make message persistent
        )
    )
    channel.confirm_delivery()
    my_rabbit.close_connection()

def do_subscribe(sub_name, queue, routing_key, exchange, subscriber_location):
    # register a subscriber
    subscribe_list = SubscriberList()
    sub_content = {
        "sub_name": sub_name,
        "queue": queue,
        "routing_key": routing_key,
        "exchange": exchange,
        "location": subscriber_location
    }
    subscribe_list.register(sub_name, subscriber_location, sub_content)
    consumer = ConsumerDynamic(
            sub_name, queue,
            routing_key=routing_key,
            exchange_name=exchange['name'],
            exchange_type=exchange['type'])
    consumer.set_callback(eventhook, sub_content)
    consumer.start()

def do_unsubscribe(sub_name):
    # disable a subscriber
    subscribe_list = SubscriberList()
    subscribe_list.delist(sub_name=sub_name)