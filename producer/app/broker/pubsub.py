import json
import pika
from .rabbit_operator import RabbitConnection
from .consumer_dynamic import ConsumerDynamic, eventhook
from .sub_list import SubscriberList

def do_publish(queue, routing_key, body,
        exchange_name, exchange_type):
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
        body=json.dumps(body),
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