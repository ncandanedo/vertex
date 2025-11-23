import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
# Fecha donde terminaron tus datos de entrenamiento
# (IMPORTANTE: Asegúrate que esta fecha conecta con el final de tu training)
last_training_date = datetime.strptime('2024-03-01 23:00:00', '%Y-%m-%d %H:%M:%S')

SERVERS = ['server_01', 'server_02', 'server_03', 'server_04', 'server_05']
CONTEXT_HOURS = 48  # El pasado que le damos para coger contexto
HORIZON_HOURS = 24  # El futuro que queremos predecir

def generate_correct_input():
    data = []
    
    for server in SERVERS:
        region = 'us-central1' 
        os_type = 'linux_ubuntu' 
        
        # 1. PARTE DEL PASADO (CONTEXTO) - Con datos reales/simulados
        # Esto sirve para que el modelo coja carrerilla
        for i in range(CONTEXT_HOURS, 0, -1):
            timestamp = last_training_date - timedelta(hours=i)
            data.append({
                'timestamp': timestamp,
                'server_id': server,
                'cpu_usage': np.random.uniform(20, 60), # Valor conocido
                'ram_usage': np.random.uniform(40, 70), # Valor conocido
                'region': region,
                'os_type': os_type
            })

        # 2. PARTE DEL FUTURO (PREDICCIÓN) - ¡ESTO ES LO QUE FALTABA!
        # Generamos filas para las próximas 24h con la CPU VACÍA (NaN)
        for i in range(1, HORIZON_HOURS + 1):
            timestamp = last_training_date + timedelta(hours=i)
            data.append({
                'timestamp': timestamp,
                'server_id': server,
                'cpu_usage': np.nan,  # <--- AQUÍ ESTÁ LA CLAVE (Vacío)
                'ram_usage': np.nan,  # Vacío también (no lo sabemos)
                'region': region,
                'os_type': os_type
            })
            
    return pd.DataFrame(data)

print("Generando archivo CORREGIDO para predicción...")
df_predict = generate_correct_input()

# Guardamos asegurándonos de que los vacíos se guarden como vacíos
df_predict.to_csv('prediction_input_corrected.csv', index=False)

print("¡Hecho! Archivo 'prediction_input_corrected.csv' creado.")
print("Este archivo tiene el pasado (con datos) Y el futuro (vacío para rellenar).")
print(df_predict.tail(10)) # Mostramos las ultimas filas para ver los NaNs