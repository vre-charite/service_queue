
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

