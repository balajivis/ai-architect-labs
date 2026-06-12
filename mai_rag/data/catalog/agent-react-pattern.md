---
title: ReAct Pattern
doc_id: agent-react-pattern
topic_area: AI Agents
source: synthetic
type: topic
---
# ReAct Pattern

ReAct ("Reasoning + Acting") is a foundational agent pattern where the model alternates between thinking about the problem and taking an action, such as calling a tool, then using what it observes to think again.

## Key ideas
- The agent interleaves reasoning steps with concrete actions.
- After each action it observes a result and feeds that back into its next thought.
- This loop lets the agent gather information it didn't have at the start.
- It makes the agent's behavior more transparent and easier to debug.
- ReAct is a building block for many more advanced agent designs.

## At Modern AI Pro
Modern AI Pro introduces ReAct as a core pattern in its Agentic AI track, explained at an overview level alongside other reasoning patterns.
