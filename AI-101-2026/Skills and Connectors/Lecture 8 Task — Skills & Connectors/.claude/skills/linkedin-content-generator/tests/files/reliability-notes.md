# Reliability / observability notes

Added structured tracing across our agent tool-call boundaries so a
single failed run can be traced end-to-end across every tool invocation,
not just the top-level request. Paired this with SLO-based alerting
(burn-rate alerts) instead of static threshold alerts, which cut
alert noise substantially while catching real incidents faster.
