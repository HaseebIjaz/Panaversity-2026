# System design & deployment notes

## CI/CD pipeline redesign
Moved from a single long-running deploy pipeline to a staged pipeline:
build -> canary (5% traffic, 15 min bake) -> full rollout, with automatic
rollback if error rate crosses a threshold during canary. This caught two
bad deploys in the first month that would previously have gone straight
to 100% of traffic.

## Infra decision framework
Standardized how we decide managed vs self-hosted for new infra
components: default to managed unless there's a specific cost, latency,
or compliance reason not to. Wrote this down after a self-hosted Kafka
cluster ate significant on-call time that a managed alternative would
have avoided.

## Scaling approach
Sharded queue-per-tenant model (see scaling-notes) plus horizontal
autoscaling keyed off queue depth rather than CPU, since our workloads
are I/O bound and CPU-based autoscaling was under-provisioning during
traffic spikes.
