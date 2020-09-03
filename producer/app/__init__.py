from flask import Flask, request
from flask_cors import CORS
from config import ConfigClass
import importlib
import logging
import logging.handlers
import os

def create_app(extra_config_settings={}):
    # initialize app and config app
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')
    CORS(
        app, 
        origins="*",
        allow_headers=["Content-Type", "Authorization","Access-Control-Allow-Credentials"],
        supports_credentials=True, 
        intercept_exceptions=False)

    # dynamic add the dataset module by the config we set
    for apis in ConfigClass.api_modules:
        api = importlib.import_module(apis)
        api.module_api.init_app(app)
    if not os.path.exists('./logs'):
        print(os.path.exists('./logs'))
        os.makedirs('./logs') 
    formatter = logging.Formatter('%(asctime)s - %(name)s - \
                              %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('./logs/queue.log')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('start')   
    return app