import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
NUM_SERVERS = 5           # Número de servidores diferentes
DAYS_OF_DATA = 60         # Días de historia (60 días * 24 horas = 1440 filas por servidor)
FREQ = '1h'               # Frecuencia de los datos (cada hora)
START_DATE = '2024-01-01' # Fecha de inicio

# --- FUNCIÓN GENERADORA ---
def generate_server_data():
    data = []
    
    # Creamos el rango de fechas
    date_range = pd.date_range(start=START_DATE, periods=DAYS_OF_DATA * 24, freq=FREQ)
    
    for i in range(1, NUM_SERVERS + 1):
        server_id = f"server_{i:02d}" # Ej: server_01, server_02
        
        # Simular características estáticas (útil para Vertex AI)
        server_region = np.random.choice(['us-central1', 'europe-west1', 'asia-east1'])
        os_type = np.random.choice(['linux_ubuntu', 'windows_server', 'linux_centos'])
        
        # Generar datos para cada hora
        for timestamp in date_range:
            hour = timestamp.hour
            day_of_week = timestamp.dayofweek
            
            # --- LÓGICA DE SIMULACIÓN DE CPU ---
            # Patrón: Más carga durante horas laborales (8am - 6pm) y entre semana
            base_load = 20
            if 8 <= hour <= 18:
                hourly_pattern = np.random.uniform(30, 50) # Carga alta
            else:
                hourly_pattern = np.random.uniform(0, 15)  # Carga baja (noche)
            
            # Menos carga los fines de semana (5 y 6 son sab/dom)
            if day_of_week > 4:
                hourly_pattern *= 0.5
                
            noise = np.random.normal(0, 5) # Ruido aleatorio
            cpu_usage = base_load + hourly_pattern + noise
            # Asegurar que esté entre 0 y 100
            cpu_usage = np.clip(cpu_usage, 5, 100)
            
            # --- LÓGICA DE SIMULACIÓN DE RAM ---
            # La RAM suele ser más estable pero correlacionada con la CPU
            ram_base = 40
            ram_usage = ram_base + (cpu_usage * 0.4) + np.random.normal(0, 2)
            ram_usage = np.clip(ram_usage, 10, 100)

            # Agregar fila
            data.append({
                'timestamp': timestamp,
                'server_id': server_id,       # ID de la serie temporal
                'region': server_region,      # Variable estática (opcional pero recomendada)
                'os_type': os_type,           # Variable estática
                'cpu_usage': round(cpu_usage, 2), # TARGET 1
                'ram_usage': round(ram_usage, 2)  # TARGET 2 (o variable predictora)
            })

    return pd.DataFrame(data)

# --- EJECUCIÓN ---
print("Generando datos sintéticos...")
df = generate_server_data()

# Guardar a CSV
file_name = 'server_metrics_training.csv'
df.to_csv(file_name, index=False)

print(f"¡Listo! Archivo '{file_name}' generado.")
print(f"Total de filas: {len(df)}")
print(f"Columnas: {list(df.columns)}")
print("\nPrimeras 5 filas:")
print(df.head())