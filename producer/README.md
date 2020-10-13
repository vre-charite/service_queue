# Queue Producer Application

this service provides an API to send queue message to rabittmq server, and the producer application will also do some pre-processing jobs before dispatching message to the queue.

This service will run at **** <host>:6060

## Installation

follow the step below to run the queue producer

### Clone

- Clone this repo to local using 'https://git.indocresearch.org/platform/service_queue'

### Setup

``
docker build . -t queue-producer/latest
docker run queue-producer/latest -d

``

## Features

- Api to send message to queue : ``/v1/send_message``

### Queue Connection

```python
import pika

credentials = pika.PlainCredentials(
                ConfigClass.gm_username,
                ConfigClass.gm_password)

            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=ConfigClass.gm_queue_endpoint,
                    heartbeat=180,
                    credentials=credentials)
            )
```

### Message Publish

```python

self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=json.dumps(body),
                properties=pika.BasicProperties(
                    delivery_mode = 2, # make message persistent
                )
            )

```