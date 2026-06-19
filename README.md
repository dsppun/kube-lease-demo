# kube-lease-demo

A small, readable demo of **Kubernetes Leases** (`coordination.k8s.io/v1`) for leader election and active–passive coordination.

Two replicas run, but only **one is active at a time**. If the active pod dies, another takes over automatically — no human needed.

## How it works

Each pod runs a simple loop:

1. **Acquire** — try to claim the Lease with its own identity (the pod name).
2. **Lead** — the pod holding the Lease does the work; the others wait on the bench.
3. **Renew** — the leader keeps updating `renewTime` to say "still alive".
4. **Step down (safety)** — if the leader *can't* renew in time, it stops working **before** the Lease expires. This is what prevents two leaders running at once.
5. **Take over** — when a passive pod sees the Lease has expired, it claims it and becomes the new leader.

> The Lease object itself does nothing. Kubernetes watches Leases for *node* health, but for app leader election like this, **your code** does the renewing and the checking. The Lease is just a shared note everyone reads and writes.

## Project structure

```
.
├── lease_worker.py      # the whole app: acquire / renew / step down / take over
├── requirements.txt     # kubernetes Python client
├── Dockerfile           # container image (runs as non-root)
├── LICENSE              # Apache-2.0
├── README.md            # this file
└── k8s/
    ├── rbac.yaml        # ServiceAccount + Role + RoleBinding (required!)
    └── deployment.yaml  # 2 replicas, POD_NAME via downward API
```

There is no separate Lease manifest — the app **creates the Lease automatically** on first run if it doesn't exist.

## Prerequisites

- Python 3.9+ (only needed for local edits; the container ships its own)
- Docker
- A Kubernetes cluster + `kubectl`

## Quick start

### 1. Build and push the image

```bash
docker build -t YOUR_REGISTRY/kube-lease-demo:1.0 .
docker push YOUR_REGISTRY/kube-lease-demo:1.0
```

Then update the `image:` line in `k8s/deployment.yaml`.

### 2. Apply RBAC first, then the Deployment

```bash
kubectl apply -f k8s/rbac.yaml        # do this first!
kubectl apply -f k8s/deployment.yaml
```

> **Apply `rbac.yaml` before the Deployment.** Without it, the pod gets `403 Forbidden` the moment it touches a Lease. The Role grants access to `leases` in `coordination.k8s.io` and nothing else.

### 3. Watch it work

```bash
kubectl get pods -l app=kube-lease-demo
kubectl logs -l app=kube-lease-demo --prefix -f

# See holderIdentity flip when leadership changes:
kubectl get lease kube-lease-demo -n default -o yaml --watch
```

### 4. Test failover

Delete the active pod and watch the other take over within a few seconds:

```bash
kubectl delete pod <name-of-the-leader-pod>
```

## Configuration

All settings are environment variables, set in `k8s/deployment.yaml`.

| Variable          | Default           | Meaning                                                        |
| ----------------- | ----------------- | -------------------------------------------------------------- |
| `LEASE_NAME`      | `my-worker-lease` | Name of the Lease object                                       |
| `LEASE_NAMESPACE` | `default`         | Namespace for the Lease                                        |
| `LEASE_DURATION`  | `15`              | How long a Lease stays valid (seconds)                         |
| `RENEW_DEADLINE`  | `10`              | If the leader can't renew within this, it steps down (seconds) |
| `RETRY_PERIOD`    | `2`               | How often each pod tries / checks (seconds)                    |
| `POD_NAME`        | pod hostname      | Unique identity per pod (injected via the downward API)        |

**Keep this rule true:** `RETRY_PERIOD < RENEW_DEADLINE < LEASE_DURATION`.
It's what lets an old leader give up *before* its Lease expires, so a new leader never overlaps with it.

## A note on correctness

Leases give you single-active **almost** all the time, not a perfect lock. There's always a tiny window (a frozen process, a network split) where two pods could briefly both think they lead. For low-stakes jobs that's fine. For anything that must run exactly once (billing, payments), also make the work **idempotent** so running it twice is harmless.


## License

Apache-2.0. See [LICENSE](LICENSE).
