# Sysdig Vulnerability Runtime Policy Exporter

Export your Sysdig Runtime Workload Vulnerabilitiy policy pass and fail rate as prometheus metrics

## Install

`docker run -p 8000:8000 -e SLEEP_TIME=600 -e SYSDIG_API_TOKEN=xxx -e SYSDIG_URL=https://us2.app.sysdig.com ghcr.io/andrewd-sysdig/sysdig-vm-runtime-policy-exporter:latest`

or see `docker-compose.yaml`

