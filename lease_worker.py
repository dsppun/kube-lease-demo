import os
import socket
import time
import datetime

from kubernetes import client, config

# --- The three magic numbers ---
LEASE_NAME = os.environ.get("LEASE_NAME", "my-worker-lease")
NAMESPACE = os.environ.get("LEASE_NAMESPACE", "default")
LEASE_DURATION = int(os.environ.get("LEASE_DURATION", "15"))   # lease valid for (s)
RENEW_DEADLINE = int(os.environ.get("RENEW_DEADLINE", "10"))   # step down if no renew (s)
RETRY_PERIOD = int(os.environ.get("RETRY_PERIOD", "2"))        # how often we try (s)

# Each pod needs a unique name. POD_NAME is injected by the Deployment (downward API).
MY_ID = os.environ.get("POD_NAME", socket.gethostname())

# Running inside the cluster, use the pod's ServiceAccount token.
config.load_incluster_config()
coordination = client.CoordinationV1Api()


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def get_lease():
    try:
        return coordination.read_namespaced_lease(LEASE_NAME, NAMESPACE)
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return None
        raise


def try_acquire_or_renew():
    lease = get_lease()

    # No lease yet? Create one and claim it.
    if lease is None:
        body = client.V1Lease(
            metadata=client.V1ObjectMeta(name=LEASE_NAME, namespace=NAMESPACE),
            spec=client.V1LeaseSpec(
                holder_identity=MY_ID,
                lease_duration_seconds=LEASE_DURATION,
                acquire_time=now(),
                renew_time=now(),
                lease_transitions=0,
            ),
        )
        try:
            coordination.create_namespaced_lease(NAMESPACE, body)
            return True
        except client.exceptions.ApiException:
            return False  # someone beat us to it

    spec = lease.spec
    held_by_me = spec.holder_identity == MY_ID
    last_renew = spec.renew_time or now()
    expired = (now() - last_renew).total_seconds() > spec.lease_duration_seconds

    # We already hold it -> just renew.
    if held_by_me:
        spec.renew_time = now()
        coordination.replace_namespaced_lease(LEASE_NAME, NAMESPACE, lease)
        return True

    # Someone else holds it, but it has expired -> take over.
    if expired:
        spec.holder_identity = MY_ID
        spec.acquire_time = now()
        spec.renew_time = now()
        spec.lease_transitions = (spec.lease_transitions or 0) + 1
        try:
            coordination.replace_namespaced_lease(LEASE_NAME, NAMESPACE, lease)
            return True
        except client.exceptions.ApiException:
            return False  # lost the race

    # Still held by someone alive -> we stay on the bench.
    return False


def main():
    print(f"{MY_ID}: starting up, watching lease '{LEASE_NAME}' in '{NAMESPACE}'")
    am_leader = False
    last_renew_ok = now()

    while True:
        got_it = try_acquire_or_renew()

        if got_it:
            if not am_leader:
                print(f"{MY_ID}: I am the leader now. Doing the work.")
            am_leader = True
            last_renew_ok = now()
            # do_the_actual_work()
        else:
            if am_leader:
                print(f"{MY_ID}: Lost the lease. Stepping down.")
            am_leader = False

        # SAFETY: if we are leader but haven't renewed in time,
        # stop working BEFORE the lease expires. This avoids two leaders.
        if am_leader and (now() - last_renew_ok).total_seconds() > RENEW_DEADLINE:
            print(f"{MY_ID}: Couldn't renew in time. Stepping down to stay safe.")
            am_leader = False

        time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    main()
