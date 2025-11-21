# 🚀 Guía Completa: Predicción de Series Temporales en Google Vertex AI

Esta guía documenta el proceso completo para predecir el consumo de **CPU y RAM** de servidores utilizando Google Cloud Vertex AI con AutoML Forecasting.

---

## 📊 Entendiendo los Datos

### ¿Por qué necesitamos 2 archivos CSV?

En **Forecasting**, debemos separar claramente el "pasado para aprender" del "contexto para predecir".

| Archivo | Propósito | Contenido | Estructura de Datos |
|---------|-----------|-----------|---------------------|
| **A: server_metrics_training.csv** | 📚 **El Libro de Texto** | Historial completo (ej. 60 días) | Todas las columnas con valores reales |
| **B: prediction_input.csv** | 📝 **El Examen** | Ventana de contexto reciente (48h) + filas futuras vacías | Target columnas con `null`/`NaN` en el futuro |

#### Archivo A: El Dataset de Entrenamiento

- **Objetivo**: Entrenar el modelo
- **Lógica**: El modelo aprende patrones históricos (ej: "Los lunes por la mañana la CPU aumenta")
- **Uso**: Solo durante la fase de training

#### Archivo B: El Input de Predicción

- **Objetivo**: Generar predicciones mediante Batch Prediction
- **Lógica**: Proporciona contexto reciente para que el modelo "tome impulso" y prediga el futuro
- **Requisito crítico**: Las filas futuras deben tener el timestamp pero el target vacío (`NaN`) para indicar a Vertex AI qué valores debe predecir

> ⚠️ **Importante**: Vertex AI necesita el Context Window completo para generar predicciones precisas.

---

## 🎯 Creación del Dataset y Entrenamiento

### Configuración del Dataset

1. **Tipo**: Tabular → Forecasting
2. **Fuente**: `server_metrics_training.csv`
3. **Esquema (Schema)**:

| Rol | Columna | Descripción |
|-----|---------|-------------|
| 🎯 **Target** | `cpu_usage` | Variable a predecir |
| 🔢 **Series Identifier** | `server_id` | Identifica cada servidor individualmente |
| ⏰ **Timestamp** | `timestamp` | Variable temporal |
| 📈 **Covariate** | `ram_usage` | Variable auxiliar predictora |
| 🏷️ **Attributes** | `region`, `os_type` | Características categóricas |

### Parámetros del Entrenamiento

- **Método**: AutoML
- **Forecast Horizon**: 24 horas (cuánto tiempo al futuro predecir)
- **Context Window**: 48 horas (cuánto histórico analizar)
- **Presupuesto**: 1 node hour
- **Arquitectura**: TiDE (TimeSeries Dense Encoder)

---

## ⚠️ El Dilema del Despliegue: Endpoint vs Batch

### ❌ Por qué falló "Deploy to Endpoint"

**Error encontrado**: `Invalid model for deployment`

| Método | Características | Idóneo para Forecasting |
|--------|----------------|------------------------|
| **Online Prediction (Endpoint)** | Respuesta en milisegundos, una fila a la vez | ❌ No compatible |
| **Batch Prediction** | Procesamiento por lotes, analiza secuencias largas | ✅ Recomendado |

#### Explicación técnica

Un **Endpoint** funciona como un chat en tiempo real, pero los modelos de Forecasting necesitan:

- Analizar el **Context Window** completo (ej. 48 horas de historia)
- Procesar secuencias temporales complejas
- Realizar cálculos computacionalmente intensivos

> 💡 **Solución**: Usar **Batch Prediction** para procesar archivos completos con todas las series temporales de forma eficiente.

### ✅ Ventajas de Batch Prediction

- **Costo-eficiente**: Solo pagas por el tiempo de procesamiento
- **Escalable**: Maneja grandes volúmenes de datos históricos
- **Robusto**: Procesa múltiples series temporales simultáneamente
- **Flexible**: Resultados exportables a BigQuery para análisis

---

## 🔮 Ejecución de la Predicción

### Paso 1: Preparar el archivo de input

```python
# Generar prediction_input.csv con:
# - Últimas 48h de datos reales (Context Window)
# - Próximas 24h con timestamps pero target = NaN
```

### Paso 2: Subir a Cloud Storage

Ubicación: `gs://your-bucket/prediction_input.csv`

### Paso 3: Configurar Batch Prediction

En **Vertex AI** → **Batch Predictions** → **Create**:

| Configuración | Valor |
|---------------|-------|
| **Modelo** | `cpu_predict` (modelo entrenado) |
| **Origen** | CSV en Cloud Storage |
| **Destino** | BigQuery → Dataset `test` |
| **Monitoring** | Off (para evitar errores de Skew en pruebas) |

### Paso 4: Ajuste crítico de Compute

> ⚠️ **Problema común**: Si la región (ej. Madrid `europe-southwest1`) no tiene stock de máquinas `n1-highmem-8`

**Soluciones**:
- Cambiar en **Advanced Options** a `n1-standard-4`
- Usar región con más disponibilidad como `us-central1`

### Paso 5: Ejecutar y monitorear

Estado esperado: ✅ **Finished**

Los resultados aparecen automáticamente en la tabla de BigQuery especificada.

---

## 📈 Visualización de Resultados en Looker Studio

### Configuración del gráfico

#### 1. Fuente de datos
- Tabla BigQuery: `predictions_*` generada por el batch job

#### 2. Tipo de gráfico
- **Line Chart** (Gráfico de líneas) o **Time Series Chart**

#### 3. Configuración detallada

| Elemento | Configuración | Detalle |
|----------|---------------|---------|
| **Dimensión (Eje X)** | `timestamp` | ⚠️ Cambiar tipo de "Fecha" a **"Fecha y Hora"** (Date Hour) |
| **Breakdown** | `server_id` | Para visualizar las 5 series en colores diferentes |
| **Métrica (Eje Y)** | `predicted_cpu_usage.value` | Valor de la predicción |
| **Ordenar** | `timestamp` → Ascendente | Para cronología de izquierda a derecha |

#### 4. Estilo visual

- **Interpolación**: Curva suave
- **Número de series**: 5 (asegurar visualización de todos los servidores)
- **Leyenda**: Activada con identificadores de servidor

---

## 🎓 Conclusiones Clave

- **Separación de datos**: Training vs Prediction input son fundamentales en forecasting
- **Batch es el camino**: Los modelos de forecasting en Vertex AI no soportan endpoints online
- **Context Window**: Proporcionar suficiente historia (48h recomendadas) mejora la precisión
- **Infraestructura**: Considerar disponibilidad regional de compute resources
- **Visualización**: Date Hour granularity es esencial para series temporales horarias

---

## 📚 Recursos Adicionales

- [Vertex AI Forecasting Overview](https://cloud.google.com/vertex-ai/docs/tabular-data/forecasting/overview)
- [Batch Predictions Documentation](https://cloud.google.com/vertex-ai/docs/tabular-data/forecasting/get-predictions)
- [TiDE Architecture Details](https://cloud.google.com/blog/products/ai-machine-learning/vertex-ai-forecasting)

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0