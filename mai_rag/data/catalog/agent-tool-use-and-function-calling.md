---
title: Tool Use and Function Calling
doc_id: agent-tool-use-and-function-calling
topic_area: AI Agents
source: synthetic
type: topic
---
# Tool Use and Function Calling

Tool use is how an agent reaches beyond text to do real work — searching the web, querying a database, sending an email, or running a calculation. Function calling is the common mechanism that lets a model request one of these actions in a structured way the surrounding system can execute.

> Note: this doc merges the near-duplicate topics "Tool Use" and "Function Calling," since function calling is the standard way agents invoke tools.

## Key ideas
- Tools give an agent abilities the model alone doesn't have.
- The model proposes a tool and its inputs; the application runs it and returns the result.
- Clear tool descriptions help the model pick the right one.
- Well-scoped tools improve reliability and reduce mistakes.
- Tool results feed back into the agent's reasoning loop.

## At Modern AI Pro
Modern AI Pro teaches tool use and function calling in its Agentic AI track at an overview level, with an explainer showing how agents extend their reach.
