# Orchestration layer notes

Redesigned our multi-agent orchestration layer around an explicit state
machine instead of implicit control flow buried in prompt chaining. Each
agent transition is now a logged, inspectable state change, which made
debugging failed multi-step runs dramatically easier -- previously we'd
have to reconstruct what happened from scattered logs.
