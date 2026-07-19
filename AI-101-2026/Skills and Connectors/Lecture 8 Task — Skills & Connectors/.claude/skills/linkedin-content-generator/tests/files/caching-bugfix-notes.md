# Release notes

Fixed a bug where cache invalidation on write wasn't propagating to
read replicas fast enough, causing stale reads for ~200ms after writes
under load. Fix: switched from TTL-only invalidation to an explicit
invalidation event published to replicas on write.
