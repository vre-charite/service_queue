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
import os

class SubscriberList():

    def __init__(self):
        dir, filename = os.path.split(os.path.realpath(__file__))
        self.sub_list_location = os.path.join(dir, "sub_list.json")
        self.read()

    def register(self, sub_name, subscriber_location, sub_content):
        subscribe = {
            "location": subscriber_location,
            "content": sub_content
        }
        self.data[sub_name] = subscribe
        self.save()

    def delist(self, sub_name):
        del self.data[sub_name]
        self.save()

    def read(self):
        with open(self.sub_list_location) as f:
            self.data = json.load(f)
            return self.data

    def save(self):
        with open(self.sub_list_location, 'w') as json_file:
            json.dump(self.data, json_file, indent=4, sort_keys=True)

