---
title: Human-in-the-Loop Patterns and Design
doc_id: agent-human-in-the-loop
topic_area: AI Agents
source: synthetic
type: topic
---
# Human-in-the-Loop Patterns and Design

Human-in-the-loop (HITL) means keeping a person in the agent's workflow at key moments — to approve, correct, or take over. Good HITL design decides where human judgment adds the most value and builds those checkpoints into the system.

> Note: this doc merges the near-duplicate topics "Human-in-the-Loop Patterns" and "Human-in-the-Loop Design."

## Key ideas
- HITL inserts approval or review before high-stakes actions.
- Common patterns include approve-before-send, edit-and-continue, and escalation.
- Design choices: which steps need a human, and how control is handed back.
- HITL builds trust and catches mistakes autonomous agents would miss.
- The goal is oversight without slowing everything to a crawl.

## At Modern AI Pro
Modern AI Pro covers human-in-the-loop patterns and design in its Agentic AI track at an overview level, emphasizing safe, trustworthy agents.
