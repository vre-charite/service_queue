from flask import Flask, request
from flask_cors import CORS
from config import ConfigClass
from app import api
import importlib
import logging
import logging.handlers
import os
import sys

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
    api.module_api.init_app(app)
    if not os.path.exists('./logs'):
        print(os.path.exists('./logs'))
        os.makedirs('./logs') 
    formatter = logging.Formatter('%(asctime)s - %(name)s - \
                              %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('./logs/queue.log')
    file_handler.setFormatter(formatter)
    app.logger.setLevel(logging.DEBUG)
    # Standard Out Handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.DEBUG)
    # Standard Err Handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    stderr_handler.setLevel(logging.ERROR)
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stdout_handler)
    app.logger.addHandler(stderr_handler)
    
    app.logger.info('start')   
    return app