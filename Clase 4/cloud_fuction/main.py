import base64
import json
import functions_framework
from google.cloud import aiplatform

# Setup
PROJECT_ID = "formacionaiops-476808"
ENDPOINT_ID = "109592721986945024" 
REGION = "europe-west4"

@functions_framework.cloud_event
def predict_pubsub(cloud_event):
    try:
        # --- MOVED INIT INSIDE THE FUNCTION ---
        # This prevents the container from crashing on startup if credentials fail
        aiplatform.init(project=PROJECT_ID, location=REGION)
        
        # 1. DECODE DATA
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
        event_data = json.loads(pubsub_message)
        print(f"Processing: {event_data}")

        # 2. PREPARE INSTANCE
        instance_for_model = {
            "avg_cpu_last_hour": event_data["last_hour"],
            "avg_cpu_yesterday": event_data["yesterday"]
        }

        # 3. PREDICT
        endpoint = aiplatform.Endpoint(ENDPOINT_ID)
        response = endpoint.predict(instances=[instance_for_model])
        
        # 4. LOGIC
        prediction = response.predictions[0]
        is_high = prediction['predicted_is_high_cpu'][0]
        status = "CRITICAL" if is_high == '1' else "OK"
        
        print(f"SUCCESS: {event_data.get('id')} is {status}")

    except Exception as e:
        # This print will show up in Cloud Logging so you know WHY it failed
        print(f"ERROR: {e}")
        raise e