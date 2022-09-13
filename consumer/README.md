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

# Queue Consumer Service

Consumers consumer message from queue. When a new consumer is added, assuming there are already messages ready in the queue, deliveries will start immediately.

The target queue can be empty at the time of consumer registration. In that case first deliveries will happen when new messages are enqueued.


## Installation

follow the step below to run the queue consumer

### Clone

- Clone this repo to local using 'https://git.indocresearch.org/platform/service_queue'

### Setup

``
docker build . -t queue-consumer/latest
docker run queue-consumer/latest -d

``

## Thrid party library Documents

pika: 'https://github.com/pika/pika'
kubernetes: 'https://github.com/kubernetes-client/python'

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

### Routing all route for connecting queue

```python

consumer = QueueConsumer(routing_key='#', exchange_name=ConfigClass.gr_exchange, exchange_type='topic', queue=ConfigClass.gr_queue)

```

### Consuming Queue

```python

consumer.channel.basic_qos(prefetch_count=1)
    consumer.channel.basic_consume(
        queue=consumer.queue,
        on_message_callback=callback)

```


### Load kubernetes configuration

```python

try:
            config.load_incluster_config()
        except:
            config.load_kube_config()

```
