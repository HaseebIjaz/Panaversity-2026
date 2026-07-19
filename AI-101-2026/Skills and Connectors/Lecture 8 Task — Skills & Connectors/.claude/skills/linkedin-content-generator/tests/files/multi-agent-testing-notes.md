# Multi-agent testing strategy

Testing multi-agent systems needs a different approach than testing
single-model calls: we test at three layers -- individual agent unit
tests (does this agent do its one job correctly in isolation), 
integration tests (do handoffs between agents preserve state correctly),
and end-to-end scenario tests against golden transcripts.
