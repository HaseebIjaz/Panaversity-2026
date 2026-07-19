# Eval framework notes

Built an internal eval harness for our agent pipeline: golden task set,
per-step assertions (not just final-output grading), and a regression
gate in CI that blocks merges if pass rate drops more than 2 points
versus main. Big lesson: grading only the final output hid a lot of
silent tool-call failures that were being masked by retry logic.
