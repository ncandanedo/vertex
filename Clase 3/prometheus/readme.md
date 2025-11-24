docker run --rm -it \
  --name prometheus-sidecar \
  --net=host \
  -v $(pwd)/key.json:/tmp/key.json \
  -v $(pwd)/prometheus_dummy.yml:/etc/prometheus/prometheus.yml \
  -v prometheus_data:/prometheus \
  -e GOOGLE_APPLICATION_CREDENTIALS="/tmp/key.json" \
  gke.gcr.io/prometheus-engine/prometheus:v2.45.3-gmp.10-gke.0 \
  --export.label.project-id="formacionaiops-476808" \
  --export.label.location="europe-west1" \
  --export.label.cluster="mi-vm-prometheus" \
  --web.listen-address=":19095" \
  --config.file="/etc/prometheus/prometheus.yml" \
  --storage.tsdb.path="/prometheus" \
  --web.enable-remote-write-receiver


  docker run --rm -it  --net=host  -v $PWD/examples/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus


  remote_write:
  - url: "http://127.0.0.1:19095/api/v1/write"

  https://github.com/prometheus-community/json_exporter