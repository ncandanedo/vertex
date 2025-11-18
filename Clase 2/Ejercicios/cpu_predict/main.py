from google.cloud import aiplatform

# Setup
PROJECT_ID = "formacionaiops-476808"
ENDPOINT_ID = "6634464157116661760" 
REGION = "europe-west4"

def predict_batch():
    aiplatform.init(project=PROJECT_ID, location=REGION)
    endpoint = aiplatform.Endpoint(ENDPOINT_ID)

    # 1. PREPARE DATA
    # We keep the IDs here in our code, we don't send them to the model.
    server_data = [
        {"id": "server_01", "last_hour": 95.0, "yesterday": 88.0}, # High load
        {"id": "server_02", "last_hour": 10.5, "yesterday": 12.0}, # Low load
        {"id": "server_03", "last_hour": 82.0, "yesterday": 70.0}  # Borderline
    ]

    # 2. FORMAT INSTANCES FOR VERTEX
    # We extract ONLY the numeric features the model expects
    instances_for_model = [
        {"avg_cpu_last_hour": s["last_hour"], "avg_cpu_yesterday": s["yesterday"]}
        for s in server_data
    ]

    # 3. SEND REQUEST
    # We send 3 items, we get 3 predictions back (in the same order)
    response = endpoint.predict(instances=instances_for_model)

    # 4. MATCH RESULTS TO SERVER IDS
    print(f"{'SERVER ID':<15} | {'PREDICTION':<12} | {'CONFIDENCE'}")
    print("-" * 45)

    # We loop through the server_data and the predictions together
    for i, prediction in enumerate(response.predictions):
        
        # Get the ID from our original list using index 'i'
        current_server_id = server_data[i]['id']
        
        # Get result from Vertex
        is_high = prediction['predicted_is_high_cpu'][0]
        probs = prediction['is_high_cpu_probs']
        
        # Logic for display
        status = "CRITICAL" if is_high == '1' else "OK"
        confidence_score = probs[0] if is_high == '1' else probs[1]

        print(f"{current_server_id:<15} | {status:<12} | {confidence_score:.2%}")

# Run it
predict_batch()