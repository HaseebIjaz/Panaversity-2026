# Scaling notes

We moved from a single monolithic worker queue to a sharded queue-per-tenant
model once a handful of high-volume tenants started starving smaller ones.
Root cause: no fairness guarantee in the original FIFO queue.

Fix: partition queues by tenant, round-robin the dispatcher across active
partitions. Added a max-inflight-per-tenant cap to prevent one tenant
saturating the shared worker pool.

Result: p95 latency for small tenants dropped noticeably; large tenants
saw a small latency increase but stayed within SLA.
