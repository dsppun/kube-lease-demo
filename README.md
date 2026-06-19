# kube-lease-demo

A comprehensive demonstration of Kubernetes Lease mechanisms for distributed coordination and leader election in cloud-native applications.

## Overview

This project showcases how to use Kubernetes Leases (`coordination.k8s.io/v1.Lease`) for implementing distributed locks, leader election, and coordination patterns in Kubernetes clusters. Leases are a lightweight, efficient way to coordinate between multiple pods or applications running on Kubernetes.

## Project Structure

```
.
├── k8s/                          # Kubernetes manifests
│   ├── README.md                # K8s deployment guide
│   ├── deployment.yaml          # Application deployment configuration
│   └── rbac.yaml               # Role-based access control setup
├── README.md                     # This file
├── Dockerfile                    # Container image definition
└── src/                         # Python source code
    ├── __init__.py
    ├── main.py                  # Entry point
    ├── lease_manager.py         # Lease management logic
    └── coordinator.py           # Coordination implementation
```

## Prerequisites

- Python 3.8+
- Docker (for building container images)
- Kubernetes cluster
- `kubectl` configured with access to your cluster

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/dsppun/kube-lease-demo.git
   cd kube-lease-demo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Kubernetes Deployment

1. **Build and push the Docker image**
   ```bash
   docker build -t your-registry/kube-lease-demo:latest .
   docker push your-registry/kube-lease-demo:latest
   ```

2. **Apply Kubernetes manifests**
   ```bash
   kubectl apply -f k8s/rbac.yaml
   kubectl apply -f k8s/deployment.yaml
   ```

3. **Verify deployment**
   ```bash
   kubectl get pods -l app=kube-lease-demo
   kubectl logs -f deployment/kube-lease-demo
   ```

## Configuration

Key environment variables:

- `LEASE_NAME`: Name of the Kubernetes Lease object (default: `demo-lease`)
- `LEASE_NAMESPACE`: Kubernetes namespace (default: `default`)
- `LEASE_DURATION`: Lease duration in seconds (default: `30`)
- `RENEW_INTERVAL`: Lease renewal interval in seconds (default: `10`)

## Architecture

### Lease-Based Leader Election

The application uses Kubernetes Leases to implement a leader election pattern:

1. **Acquire**: Pods attempt to acquire a lease with their identity
2. **Lead**: The pod holding the lease becomes the leader
3. **Renew**: The leader continuously renews the lease
4. **Transfer**: If the leader fails, another pod acquires the lease


