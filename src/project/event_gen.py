# System Guarantees
#
# dempotency
# Duplicate events do not create duplicate state
# Robustness
# Malformed events do not crash the system
# Eventual Consistency
# System may be temporarily incomplete but converges
# Accurate Queries
# Queries reflect the current processed state
#
# You need to devise unit tests that reflect these guarantees
#
# Failure modes to inject: duplicates, dropped messages, delayed delivery, and subscriber downtime.
#
# Do Definsive Testing
