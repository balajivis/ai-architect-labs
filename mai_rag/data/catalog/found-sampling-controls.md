---
title: Sampling Controls (Temperature, Top-p, Top-k, Max Tokens)
doc_id: found-sampling-controls
topic_area: LLM Foundations
source: synthetic
type: topic
---
# Sampling Controls (Temperature, Top-p, Top-k, Max Tokens)

> Note: this doc merges four near-duplicate topics — Temperature, Top-p and Top-k Sampling, and Max Tokens — since all are decoding/sampling knobs that shape a model's output.

Sampling controls are settings that influence how a model chooses its next words and how long its answer can be. They let you dial outputs between focused and creative, and cap response length.

## Key ideas
- Temperature broadly controls how random or focused outputs are.
- Top-p and top-k limit which candidate words the model may pick from.
- Max tokens caps the length of the generated response.
- Lower randomness suits factual tasks; higher suits brainstorming.
- These are tuning knobs, not magic; defaults work for many cases.

## At Modern AI Pro
Modern AI Pro covers these sampling controls together in its Practitioner course through an interactive explainer that shows how each knob shifts the output.
