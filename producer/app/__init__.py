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

import logging
import logging.handlers
import os
import sys

from flask import Flask
from flask_cors import CORS
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.pika import PikaInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app import api
from config import ConfigClass  # noqa


def create_app():
    """Initialize and configure app."""

    app = Flask(__name__)
    app.config.from_object(__name__ + '.ConfigClass')
    CORS(
        app,
        origins="*",
        allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        supports_credentials=True,
        intercept_exceptions=False,
    )
    api.module_api.init_app(app)
    if not os.path.exists('./logs'):
        os.makedirs('./logs')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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


def instrument_app(app: Flask) -> None:
    """Instrument the application with OpenTelemetry tracing."""

    if ConfigClass.OPEN_TELEMETRY_ENABLED != "TRUE":
        return

    tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: ConfigClass.APP_NAME}))
    trace.set_tracer_provider(tracer_provider)

    FlaskInstrumentor().instrument_app(app)
    PikaInstrumentor().instrument()
    RequestsInstrumentor().instrument()

    jaeger_exporter = JaegerExporter(
        agent_host_name=ConfigClass.OPEN_TELEMETRY_HOST, agent_port=ConfigClass.OPEN_TELEMETRY_PORT
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
