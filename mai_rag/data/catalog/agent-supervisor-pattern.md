---
title: Supervisor Pattern
doc_id: agent-supervisor-pattern
topic_area: AI Agents
source: synthetic
type: topic
---
# Supervisor Pattern

The supervisor pattern puts one coordinating agent in charge of a team of worker agents. The supervisor receives the goal, decides which worker should handle each part, and assembles their results.

## Key ideas
- A central supervisor delegates tasks to specialized workers.
- Workers focus on their narrow job and report back.
- The supervisor manages sequencing and combines outputs.
- This gives a clear, hierarchical structure that's easy to reason about.
- It contrasts with flatter, peer-to-peer designs like swarms.

## At Modern AI Pro
Modern AI Pro presents the supervisor pattern in its Multi-Agent Systems course at an overview level, as one common way to organize agent teams.
