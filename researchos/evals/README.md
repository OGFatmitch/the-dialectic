# Integrity evals

Evals are separate from unit tests. Each fixture describes adversarial input and the invariant expected from a model-backed workflow.

- `hallucinated_source.json`: reject plausible but nonexistent citations.
- `contradiction_detection.json`: surface disagreement rather than average it away.
- `confidentiality.json`: block restricted content from public artifacts.

The deterministic V1 records these contracts now; the executable model grader arrives with the live agent provider.
