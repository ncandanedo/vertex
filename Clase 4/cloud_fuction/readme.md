Server Load Predictor: Pub/Sub to Vertex AI

This project deploys a Google Cloud Function that listens to a Pub/Sub Topic. When a message containing server metrics is published to the topic, the function triggers a Vertex AI Endpoint to predict whether the server is in a critical state.

🏗 Architecture

Pub/Sub Topic (Trigger) ➔ Cloud Function (Processor) ➔ Vertex AI (Model) ➔ Cloud Logging (Result)

📋 Prerequisites

Google Cloud Project with billing enabled.

APIs Enabled:

Cloud Functions API

Cloud Pub/Sub API

Vertex AI API

Cloud Build API

Vertex AI Endpoint: You need a deployed model endpoint ID (configured in main.py).

📂 Project Files

1. requirements.txt

Dependencies required for the environment.

functions-framework==3.*
google-cloud-aiplatform
protobuf


2. main.py

The main logic script.

import base64
import json
import functions_framework
from google.cloud import aiplatform

# --- Configuration ---
PROJECT_ID = "formacionaiops-476808"
ENDPOINT_ID = "6634464157116661760" 
REGION = "europe-west4"

@functions_framework.cloud_event
def predict_pubsub(cloud_event):
    """
    Triggered from a message on a Cloud Pub/Sub topic.
    """
    try:
        # Initialize Vertex AI SDK inside the function to prevent startup crashes
        aiplatform.init(project=PROJECT_ID, location=REGION)

        # 1. DECODE PUBSUB MESSAGE
        # Pub/Sub data comes in base64 format inside the cloud_event
        if "data" in cloud_event.data["message"]:
            pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
            event_data = json.loads(pubsub_message)
        else:
            print("No data found in message")
            return

        print(f"Processing event for Server ID: {event_data.get('id', 'Unknown')}")

        # 2. FORMAT DATA FOR VERTEX
        # Extract ONLY the numeric features the model expects
        instance_for_model = {
            "avg_cpu_last_hour": event_data["last_hour"],
            "avg_cpu_yesterday": event_data["yesterday"]
        }

        # 3. SEND REQUEST TO ENDPOINT
        endpoint = aiplatform.Endpoint(ENDPOINT_ID)
        response = endpoint.predict(instances=[instance_for_model])

        # 4. PROCESS PREDICTION
        prediction = response.predictions[0]
        
        # Extract logic
        server_id = event_data.get('id', 'Unknown')
        is_high = prediction['predicted_is_high_cpu'][0] 
        probs = prediction['is_high_cpu_probs']

        # Logic for display
        status = "CRITICAL" if is_high == '1' else "OK"
        confidence_score = probs[0] if is_high == '1' else probs[1]

        # 5. LOG RESULT
        log_message = f"RESULT: {server_id:<15} | {status:<12} | {confidence_score:.2%}"
        print(log_message)

    except Exception as e:
        print(f"Error processing prediction: {e}")
        raise e


🚀 Deployment

You can deploy this function using the Google Cloud Console or the command line.

Option 1: Using gcloud CLI

Run this command in the folder containing your files:

gcloud functions deploy predict_pubsub \
--gen2 \
--runtime=python310 \
--region=europe-west4 \
--source=. \
--entry-point=predict_pubsub \
--trigger-topic=test


Note: Ensure the topic test exists in Pub/Sub before running this.

Option 2: Using Cloud Console UI

Go to Cloud Functions > Create Function.

Environment: 2nd Gen.

Trigger: Cloud Pub/Sub -> Select your topic (e.g., projects/formacionaiops-476808/topics/test).

Runtime: Python 3.10 (or newer).

Entry point: predict_pubsub.

Code: Paste the contents of main.py and requirements.txt.

📡 How to Call (Test) via Pub/Sub

You can trigger the function by publishing a message to the topic.

Method 1: Google Cloud Console (Easiest)

Go to Pub/Sub > Topics.

Click on your topic (e.g., test).

Click the Messages tab > Publish Message.

In the Message body box, paste this JSON:

{
  "id": "server_03",
  "last_hour": 82.0,
  "yesterday": 70.0
}


Click Publish.

Method 2: Using gcloud CLI

You can send a message directly from your terminal:

gcloud pubsub topics publish test --message='{"id": "server_03", "last_hour": 82.0, "yesterday": 70.0}'


🔍 Verifying Results

Since this is a background function, it does not return a result to the user immediately. To see the output:

Go to Cloud Functions in the console.

Click your function name (predict_pubsub).

Click the Logs tab.

Look for the entry:
RESULT: server_03       | CRITICAL     | 95.00%