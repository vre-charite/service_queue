from flask_restx import Resource
from models.api_response import APIResponse, EAPIResponseCode
from config import ConfigClass

class BrokerRoot(Resource):
    def get(self):
        res = APIResponse()
        res.set_code(EAPIResponseCode.success)
        res.set_result("Message Broker Service on, verision: " + ConfigClass.version)
        return res.response, res.code