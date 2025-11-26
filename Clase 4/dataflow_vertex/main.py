import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import aiplatform
import logging

# --- CONFIGURACIÓN ---
PROJECT_ID = "formacionaiops-476808"
ENDPOINT_ID = "109592721986945024" 
REGION = "europe-west4"

# --- TUS DATOS DE ENTRADA (Simulados) ---
# En un caso real, esto vendría de BigQuery o Pub/Sub
SERVER_DATA = [
    {"id": "server_01", "last_hour": 95.0, "yesterday": 88.0},
    {"id": "server_02", "last_hour": 10.5, "yesterday": 12.0},
    {"id": "server_03", "last_hour": 82.0, "yesterday": 70.0}
]

# --- LA LÓGICA DE PROCESAMIENTO (DoFn) ---
class VertexPredictDoFn(beam.DoFn):
    """
    Esta clase se encarga de procesar cada elemento (o lote) en los workers.
    """
    def __init__(self, project_id, region, endpoint_id):
        self.project_id = project_id
        self.region = region
        self.endpoint_id = endpoint_id
        self.endpoint = None

    def setup(self):
        """
        Esto se ejecuta UNA VEZ cuando el worker arranca.
        Es el lugar eficiente para iniciar la conexión con Vertex AI.
        """
        aiplatform.init(project=self.project_id, location=self.region)
        self.endpoint = aiplatform.Endpoint(self.endpoint_id)

    def process(self, element):
        """
        Esto se ejecuta para CADA elemento que pasa por la tubería.
        element: Es un diccionario {"id": "server_01", ...}
        """
        try:
            # 1. Formatear para Vertex (igual que tu script original)
            instance = {
                "avg_cpu_last_hour": element["last_hour"], 
                "avg_cpu_yesterday": element["yesterday"]
            }

            # 2. Llamar al modelo
            # Nota: Enviamos una lista de 1 elemento [instance]
            response = self.endpoint.predict(instances=[instance])
            
            # 3. Procesar la respuesta
            prediction = response.predictions[0]
            
            is_high = prediction['predicted_is_high_cpu'][0]
            probs = prediction['is_high_cpu_probs']
            
            status = "CRITICAL" if is_high == '1' else "OK"
            confidence_score = probs[0] if is_high == '1' else probs[1]

            # 4. Devolver el resultado enriquecido (yield)
            # Unimos el ID original con la predicción
            yield {
                "server_id": element['id'],
                "status": status,
                "confidence": round(confidence_score, 4)
            }

        except Exception as e:
            logging.error(f"Error prediciendo server {element.get('id')}: {e}")

# --- EL PIPELINE PRINCIPAL ---
def run():
    # Opciones para correr en local o en la nube
    options = PipelineOptions()
    
    with beam.Pipeline(options=options) as p:
        (
            p
            | "Crear Datos" >> beam.Create(SERVER_DATA)
            | "Predecir en Vertex" >> beam.ParDo(VertexPredictDoFn(PROJECT_ID, REGION, ENDPOINT_ID))
            | "Formatear Salida" >> beam.Map(lambda x: print(f"Resultado: {x}"))
            # Nota: En producción, aquí usarías beam.io.WriteToBigQuery(...)
        )

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()