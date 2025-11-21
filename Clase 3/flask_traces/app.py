# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import time
from random import randint, uniform
import random
import requests
from flask import Flask, url_for,jsonify

from gcp_logging import setup_structured_logging
from setup_opentelemetry import setup_opentelemetry
from setup_profile import init_gcp_profiler
# [START opentelemetry_instrumentation_main]
logger = logging.getLogger(__name__)

# Initialize OpenTelemetry Python SDK and structured logging
setup_opentelemetry()
setup_structured_logging()
init_gcp_profiler(logger)
app = Flask(__name__)


@app.route("/heavy")
def heavy_task():
    """Simula una tarea pesada para ver en Trace y Profiler."""

    logger.info("Iniciando tarea pesada...")
    
    # Simulamos carga de CPU para el Profiler
    result = 0
    for _ in range(1_000_000):
        result += random.random()
        
    # Simulamos latencia de red/IO para el Trace
    time.sleep(0.5) 
    
    return jsonify({"message": "Tarea pesada completada", "result": result})
    
# [START opentelemetry_instrumentation_handle_multi]
@app.route("/multi")
def multi():
    """Handle an http request by making 3-7 http requests to the /single endpoint."""
    sub_requests = randint(3, 7)
    logger.info("handle /multi request", extra={"subRequests": sub_requests})
    for _ in range(sub_requests):
        requests.get(url_for("single", _external=True))
    return "ok"


# [END opentelemetry_instrumentation_handle_multi]


# [START opentelemetry_instrumentation_handle_single]
@app.route("/single")
def single():
    """Handle an http request by sleeping for 100-200 ms, and write the number of seconds slept as the response."""
    duration = uniform(0.1, 0.2)
    logger.info("handle /single request", extra={"duration": duration})
    time.sleep(duration)
    return f"slept {duration} seconds"


# [END opentelemetry_instrumentation_handle_single]