import os
import time
import random
import logging
from flask import Flask, jsonify

# --- Imports de Cloud Profiler ---
try:
    import googlecloudprofiler
except ImportError:
    googlecloudprofiler = None

# --- Imports de OpenTelemetry (Cloud Trace) ---
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.resourcedetector.gcp import GoogleCloudResourceDetector
app = Flask(__name__)

# Configuración de Logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_gcp_profiler():
    """Inicializa Cloud Profiler si la variable de entorno lo permite."""
    if os.environ.get("ENABLE_PROFILER") == "true":
        if googlecloudprofiler:
            try:
                googlecloudprofiler.start(
                    service=os.environ.get("K_SERVICE", "mi-flask-api"),
                    service_version=os.environ.get("K_REVISION", "1.0.0"),
                    # verbose=3, # Descomentar para debug local
                )
                logger.info("✅ Google Cloud Profiler iniciado.")
            except (ValueError, NotImplementedError) as exc:
                logger.error(f"❌ Error al iniciar Profiler: {exc}")
        else:
            logger.warning("⚠️ Librería google-cloud-profiler no instalada.")


def init_cloud_trace():
    """Inicializa Cloud Trace (OpenTelemetry) con detección de recursos."""
    if os.environ.get("ENABLE_TRACING") == "true":
        try:
            # 1. Detectar automáticamente el entorno de GCP (Cloud Run)
            # Esto llena atributos como cloud.platform, cloud.region, host.id, etc.
            gcp_resource = GoogleCloudResourceDetector(raise_on_error=False).detect()

            # 2. Definir explícitamente el nombre del servicio
            # Fusionamos (merge) el recurso detectado con nuestro nombre manual
            service_resource = Resource.create({
                "service.name": os.environ.get("K_SERVICE", "mi-flask-observability"),
                "service.version": os.environ.get("K_REVISION", "1.0.0")
            })
            final_resource = gcp_resource.merge(service_resource)

            # Configurar el exportador
            exporter = CloudTraceSpanExporter()
            
            # Usar el recurso combinado en el Provider
            tracer_provider = TracerProvider(resource=final_resource)
            
            tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(tracer_provider)
            
            # Instrumentar Flask
            FlaskInstrumentor().instrument_app(app)
            
            logger.info(f"✅ Google Cloud Trace iniciado para el servicio: {os.environ.get('K_SERVICE')}")
        except Exception as e:
            logger.error(f"❌ Error al iniciar Cloud Trace: {e}")
            
# --- Inicialización ---
init_gcp_profiler()
init_cloud_trace()

# Obtener el tracer para spans manuales si es necesario
tracer = trace.get_tracer(__name__)

@app.route("/")
def index():
    logger.info("Endpoint raíz llamado")
    return jsonify({"message": "Hola desde Cloud Run con Observabilidad!", "status": "online"})

@app.route("/heavy")
def heavy_task():
    """Simula una tarea pesada para ver en Trace y Profiler."""
    with tracer.start_as_current_span("tarea_procesamiento_pesado"):
        logger.info("Iniciando tarea pesada...")
        
        # Simulamos carga de CPU para el Profiler
        result = 0
        for _ in range(1_000_000):
            result += random.random()
            
        # Simulamos latencia de red/IO para el Trace
        time.sleep(0.5) 
        
        return jsonify({"message": "Tarea pesada completada", "result": result})

if __name__ == "__main__":
    # Esto es solo para ejecución local
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))