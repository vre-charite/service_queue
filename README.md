This repo will document how to use rabbitmq.
### Sender
* sender will not directly talk to the queue, instead, it will talk to an exchange, like the following
```python
# channel
connection = pika.BlockingConnection(pika.ConnectionParameters('10.3.9.240'))
channel = connection.channel()

# exchange
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

channel.basic_publish(
    exchange='direct_logs',                                    # talk to the exchange
    routing_key=severity,                                      # send to the routing
    body=message,                                              # message to be send
    properties=pika.BasicProperties(
        delivery_mode = 2,                                     # make message persistent
    )
)
```


### Receiver
```
# same as sender
# channel
connection = pika.BlockingConnection(pika.ConnectionParameters('10.3.9.240'))
channel = connection.channel()

# exchange 
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

# queue
# we need to make sure that the queue will survive a RabbitMQ node restart(durable)
# Secondly, once the consumer connection is closed, the queue should be deleted. There's an exclusive flag for that:
result = channel.queue_declare(queue='', exclusive=True, durable=True)  
queue_name = result.method.queue
# connect the queue with the exchange, receive only the message that match the routing_key
channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key=severity)

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

# we can use the Channel#basic_qos channel method with the prefetch_count=1 setting. 
# This uses the basic.qos protocol method to tell RabbitMQ not to give more than one message to a worker at a time. 
# Or, in other words, don't dispatch a new message to a worker until it has processed and acknowledged the previous one.
#  Instead, it will dispatch it to the next worker that is not still busy
channel.basic_qos(prefetch_count=1)

# Manual message acknowledgments are turned on by default. 
# In previous examples we explicitly turned them off via the auto_ack=True flag. 
# It's time to remove this flag and send a proper acknowledgment from the worker, 
# once we're done with a task.
channel.basic_consume(queue=queue_name, on_message_callback=callback)
channel.start_consuming()

```