# --- Imports de Cloud Profiler --
# 
# -

import os 
try:
    import googlecloudprofiler
except ImportError:
    googlecloudprofiler = None
    
def init_gcp_profiler(logger):
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