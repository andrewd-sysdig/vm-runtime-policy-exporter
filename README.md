# Disclaimer

Notwithstanding anything that may be contained to the contrary in your agreement(s) with Sysdig, Sysdig provides no support, no updates, and no warranty or guarantee of any kind with respect to these script(s), including as to their functionality or their ability to work in your environment(s).  Sysdig disclaims all liability and responsibility with respect to any use of these scripts. 

# Sysdig Vulnerability Runtime Policy Exporter

Export your Sysdig Runtime Workload Vulnerabilitiy policy pass and fail rate as prometheus metrics. 

Note: This uses an undocumented/unsupported API

## Install

`docker run -p 8000:8000 -e SLEEP_TIME=600 -e SYSDIG_API_TOKEN=xxx -e SYSDIG_URL=https://us2.app.sysdig.com ghcr.io/andrewd-sysdig/sysdig-vm-runtime-policy-exporter:latest`

or see `docker-compose.yaml`

