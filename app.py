import requests
import time
from prometheus_client import Gauge, start_http_server
import os

if os.getenv('SYSDIG_API_TOKEN') is not None:
    SYSDIG_API_TOKEN = os.getenv('SYSDIG_API_TOKEN')
else:
    print("Error: SYSDIG_API_TOKEN not set")
    exit(1)

if os.getenv('SYSDIG_URL') is not None:
    SYSDIG_URL = os.getenv('SYSDIG_URL')
else:
    print("Error: SYSDIG_URL not set")
    exit(1)

if os.getenv('SLEEP_TIME') is not None:
    SLEEP_TIME = int(os.getenv('SLEEP_TIME'))
else:
    print("Error: SLEEP_TIME not set")
    exit(1)

# Initialize Prometheus metrics
passed_metric = Gauge('sysdig_vm_runtime_policy_passed', 'Workloads passing policy', ['cluster_name'])
failed_metric = Gauge('sysdig_vm_runtime_policy_failed', 'Workloads failing policy', ['cluster_name'])
total_metric = Gauge('sysdig_vm_runtime_total', 'Total Workloads', ['cluster_name'])
passed_percent_metric = Gauge('sysdig_vm_runtime_policy_passed_percent', 'Percentage of Workloads passing policy', ['cluster_name'])

def fetch_clusters():
    url = SYSDIG_URL + "/api/data/entity/mds"
    headers = {
        'Authorization': f'Bearer {SYSDIG_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        "filter": "kubernetes.cluster.name != null",
        "metrics": ["kubernetes.cluster.name"],
        "time": {"last": 3600000000},
        "paging": {"from": 0, "to": 99},
        "sort": [{"kubernetes.cluster.name": "ASC"}],
        "zoneIds": []
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    
    cluster_names = [item["kubernetes.cluster.name"] for item in data["data"]]
    return cluster_names

def fetch_sysdig_data(cluster_name, filter_string, metric):
    url = SYSDIG_URL + "/api/scanning/runtime/v2/workflows/results"
    params = {
        'cursor': '',
        'filter': filter_string,
        'limit': 0,
        'order': 'desc',
        'sort': 'runningVulnsBySev',
        'zones': ''
    }
    headers = {
        'Authorization': f'Bearer {SYSDIG_API_TOKEN}'
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    
    # Extract the 'matched' value
    matched_value = data.get('page', {}).get('matched', 0)
    
    # Set the Prometheus metric with the cluster name as a label
    metric.labels(cluster_name=cluster_name).set(matched_value)
    return matched_value

if __name__ == "__main__":
    # Start Prometheus server to expose metrics on port 8000
    start_http_server(8000)
    
    while True:
        # Fetch the list of clusters
        cluster_names = fetch_clusters()
        
        for cluster_name in cluster_names:
            # Construct filter strings for each metric type
            filter_passed = f'policyStatus in ("passed", "accepted") and kubernetes.cluster.name = "{cluster_name}"'
            filter_failed = f'policyStatus = "failed" and kubernetes.cluster.name = "{cluster_name}"'
            filter_total = f'kubernetes.cluster.name = "{cluster_name}"'
            
            # Update metrics for each cluster
            passed_count = fetch_sysdig_data(cluster_name, filter_passed, passed_metric)
            failed_count = fetch_sysdig_data(cluster_name, filter_failed, failed_metric)
            total_count = fetch_sysdig_data(cluster_name, filter_total, total_metric)
            
            # Calculate percentage of passed policies
            if total_count > 0:
                passed_percent = (passed_count / total_count) * 100
            else:
                passed_percent = 0
            
            # Update percentage metric
            passed_percent_metric.labels(cluster_name=cluster_name).set(passed_percent)
        
        # Wait for 10mins before the next fetch
        time.sleep(SLEEP_TIME)
