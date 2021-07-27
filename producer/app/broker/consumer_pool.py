from models.singleton import singleton
from consumer_dynamic import ConsumerDynamic

@singleton
class ConsumerPool:

    def __init__(self):
        self.pool = {}
    
    def add_consumer(self, sub_name, consumer: ConsumerDynamic):
        self.pool[sub_name] = consumer

    def disable_consumer(self, sub_name):
        consumer: ConsumerDynamic = self.pool[sub_name]
        # consumer.