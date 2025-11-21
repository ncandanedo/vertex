#!/bin/bash

echo "🔥 Generando carga pesada en: $URL/heavy"
echo "Presiona CTRL+C para detener (déjalo correr 5-10 minutos)"

# Lanzamos 4 procesos en paralelo para estresar la CPU
for i in {1..4}; do
  while true; do 
    curl -s "https://mi-flask-observability-521912427275.europe-west1.run.app/heavy" > /dev/null
  done &
done

# Esperamos
wait