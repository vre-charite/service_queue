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

from flask import request
from flask_restx import Resource
from models.api_response import APIResponse, EAPIResponseCode
from app.broker.pubsub import do_subscribe
from config import ConfigClass
import time

class BrokerSubscriber(Resource):
    def post(self):
        res = APIResponse()
        event = request.get_json()

        # payload validation
        required = ['consumer_location', 'consumer_name', 'queue', 'routing_key']
        for field in required:
            if field not in event:
                res.set_code(EAPIResponseCode.bad_request)
                res.set_result("param '{}' is required.".format(field))
                return res.response, res.code

        queue = event.get('queue')
        routing_key = event.get('routing_key')
        consumer_name = event.get('consumer_name')
        consumer_location = event.get('consumer_location')
        exchange = event.get('exchange', {
            "name": "FANOUT_TOPIC",
            "type": "fanout"})

        # exchange validation
        required = ['name', 'type']
        for field in required:
            if field not in exchange:
                res.set_code(EAPIResponseCode.bad_request)
                res.set_result("param '{}' is required in exchange object.".format(field))
                return res.response, res.code

        create_timestamp = event.get('create_timestamp', time.time())
        event['create_timestamp'] = create_timestamp
        event['exchange'] = exchange
        do_subscribe(consumer_name, queue, routing_key, exchange, consumer_location)
        res.set_code(EAPIResponseCode.success)
        res.set_result("Cosumer {} Registered.".format(consumer_name))
        return res.response, res.code

class BrokerConsumerHookShowcase(Resource):
    def post(self):
        res = APIResponse()
        event = request.get_json()
        from pprint import pprint
        pprint("============Hook Invoked===============")
        pprint(event)
        res.set_code(EAPIResponseCode.success)
        res.set_result(event)
        return res.response, res.code