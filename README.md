# kube-lease-demo

A comprehensive demonstration of Kubernetes Lease mechanisms for distributed coordination and leader election in cloud-native applications.

## Overview

This project showcases how to use Kubernetes Leases (`coordination.k8s.io/v1.Lease`) for implementing distributed locks, leader election, and coordination patterns in Kubernetes clusters. Leases are a lightweight, efficient way to coordinate between multiple pods or applications running on Kubernetes.

## Features

- **Leader Election**: Demonstrate how multiple replicas can coordinate to elect a single leader
- **Distributed Locking**: Show patterns for implementing distributed locks using Kubernetes Leases
- **Lease Renewal**: Examples of proper lease acquisition, renewal, and release patterns
- **Kubernetes Integration**: Full integration with Kubernetes API and RBAC policies

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
- Kubernetes 1.19+ cluster
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

3. **Run locally** (requires kubectl context)
   ```bash
   python src/main.py
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

### Key Components

- **LeaseManager**: Handles lease acquisition, renewal, and release
- **Coordinator**: Implements the leader election logic
- **Main**: Application entry point and orchestration

## API Reference

### Lease Operations

The application interacts with the Kubernetes API to:

- Create/update `coordination.k8s.io/v1.Lease` objects
- Monitor lease ownership and expiration
- Handle graceful lease transfers

## RBAC Requirements

The deployment requires the following Kubernetes RBAC permissions:

```yaml
- get, create, update, delete, watch leases
- get pods
- watch events
```

See `k8s/rbac.yaml` for complete RBAC configuration.

## Monitoring and Logging

- **Logs**: Check application logs via `kubectl logs`
- **Events**: View Kubernetes events: `kubectl describe lease <lease-name>`
- **Metrics**: Application exports standard metrics (configurable)

## Testing

Run the test suite:

```bash
pytest tests/
```

## Troubleshooting

### Lease Acquisition Fails
- Verify RBAC permissions are correctly applied
- Check pod service account has required roles
- Ensure lease namespace exists

### Leader Repeatedly Changes
- Check network connectivity between pods
- Verify lease duration and renewal intervals
- Review application logs for errors

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Resources

- [Kubernetes Leases Documentation](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.25/#lease-v1-coordination-k8s-io)
- [Leader Election Patterns](https://kubernetes.io/docs/concepts/architecture/leases/)
- [RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

## Support

For issues, questions, or suggestions, please open a GitHub issue on the [project repository](https://github.com/dsppun/kube-lease-demo).
