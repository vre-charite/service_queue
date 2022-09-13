<!--
 Copyright 2022 Indoc Research
 
 Licensed under the EUPL, Version 1.2 or – as soon they
 will be approved by the European Commission - subsequent
 versions of the EUPL (the "Licence");
 You may not use this work except in compliance with the
 Licence.
 You may obtain a copy of the Licence at:
 
 https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 
 Unless required by applicable law or agreed to in
 writing, software distributed under the Licence is
 distributed on an "AS IS" basis,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 express or implied.
 See the Licence for the specific language governing
 permissions and limitations under the Licence.
 
-->

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
