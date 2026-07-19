# Notes

Had a rough week, felt pretty burnt out and stressed about the project
deadline. Anyway -- technical bit: we refactored our retry logic for
the agent tool-call layer to use exponential backoff with jitter instead
of fixed-interval retries, which cut down on thundering-herd retries
during upstream API outages.

Also need to call the dentist, and mom's birthday is next week.
