# Agentic Systems Lab

A hands-on learning journey for understanding how agentic AI systems work from first principles.

Rather than starting with an agent framework, this project begins with a simple OpenAI API call and progressively builds the mechanics underneath an agent:

**SDK → Responses → Context → Structured Outputs → Tool Calling → Agent Loop**

The goal is not just to learn API syntax. The goal is to understand what is happening underneath so that frameworks such as the OpenAI Agents SDK and LangGraph do not feel like magic.

---

## Learning Philosophy

Each lab introduces one concept at a time.

The recommended approach is:

**Type → Run → Observe → Understand → Move On**

Do not simply copy the code. Type it, run it, inspect the response, and understand what changed from the previous lab.

Throughout the labs, ask four questions:

1. **Code** — What did we implement?
2. **Mechanics** — What happened underneath?
3. **Cognition** — What part of an agent's reasoning/action loop does this represent?
4. **Architecture** — How would this appear in a real enterprise agentic system?

---

# Setup

## 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure the API key

Create a `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
```

`.env` is excluded from Git.

---

# Learning Path

## Part 1 — SDK Fundamentals

### Lab 01 — First Response

```bash
python labs/01_first_response.py
```

Introduces:

- `OpenAI()` client
- Responses API
- model invocation
- response object
- output text
- response ID
- model version
- status
- token usage

Key idea:

**An AI execution returns a structured response object, not merely text.**

---

### Lab 02 — Instructions

```bash
python labs/02_instructions.py
```

Separates:

- behavioral instructions
- current user input

Key idea:

**Instructions guide model behavior while input represents the current request.**

---

### Lab 03 — Instruction Variations

```bash
python labs/03_instructions_variations.py
```

Uses the same instructions with a different customer request.

This demonstrates how relatively stable behavioral instructions can govern changing user inputs.

Key principle:

**Prompts guide behavior. Code should enforce critical business constraints.**

---

# Part 2 — Context and State

### Lab 04 — Independent Requests

```bash
python labs/04_conversation_state.py
```

Makes two independent model calls.

The second request does not automatically know information supplied to the first.

Key idea:

**LLM intelligence and conversation state are separate concerns.**

---

### Lab 05 — Conversation Continuity

```bash
python labs/05_conversation_continuity.py
```

Introduces:

```python
previous_response_id
```

This allows a new response to continue from a previous response.

Key idea:

**The platform can provide state mechanisms, while the application still owns how those mechanisms map to users, sessions, and business processes.**

---

### Lab 06 — Application-Managed Context

```bash
python labs/06_application_managed_context.py
```

Instead of relying on response chaining, the application explicitly supplies conversation history.

This introduces an important distinction:

- **Context** — information visible to the model for the current inference
- **State** — information maintained as the interaction progresses
- **Memory** — information intentionally persisted and recalled later

These concepts are related but are not the same.

---

# Part 3 — Structured Outputs

### Lab 07 — Structured Output

```bash
python labs/07_structured_output.py
```

Introduces Pydantic models and structured model responses.

Instead of asking the model to produce arbitrary prose, the application defines a typed contract.

Conceptually:

```text
Natural Language
      ↓
     LLM
      ↓
Typed Contract
      ↓
Application
```

A Pydantic model such as:

```python
class OrderIntent(BaseModel):
    order_id: str
    intent: str
    urgency: str
    requires_action: bool
```

is converted by the SDK into a schema that can be communicated through the API.

The structured response is then parsed back into a Python object.

Mental model:

**Pydantic model → JSON Schema → model output → Pydantic object**

---

### Lab 08 — Constrained Structured Output

```bash
python labs/08_structured_output_constraints.py
```

Introduces enums to constrain model output to known domain values.

Instead of:

```text
intent = any string
```

we can constrain the output to values such as:

```text
track_order
cancel_order
return_order
other
```

This begins to demonstrate how LLM interpretation can feed deterministic application logic.

---

# Part 4 — Tool Calling

### Lab 09 — Basic Tool Calling

```bash
python labs/09_tool_calling_basic.py
```

Introduces function tools.

The model receives:

- tool name
- description
- parameter schema

The model does **not** receive or execute the Python implementation.

Instead, it can return a structured request such as:

```text
function_call

name      = get_order_status
arguments = {"order_id": "ORD-1234"}
```

Key principle:

**The model proposes an action. The runtime controls execution.**

---

### Lab 10 — Execute the Tool

```bash
python labs/10_execute_tool.py
```

The application:

1. reads the requested tool
2. deserializes its arguments
3. invokes the corresponding Python function

This establishes the boundary between:

```text
Cognitive Plane
     ↓
Model proposes action

Execution Plane
     ↓
Runtime executes action
```

---

### Lab 11 — Complete Tool Loop

```bash
python labs/11_complete_tool_loop.py
```

Completes the full tool interaction:

```text
User
 ↓
LLM
 ↓
Tool Call
 ↓
Runtime
 ↓
Tool Execution
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

The `call_id` correlates a tool result with the tool request that produced it.

The tool result becomes a new **observation** available to the model.

---

# Part 5 — Building an Agent Loop

### Lab 12 — Agent Loop

```bash
python labs/12_agent_loop.py
```

The number of reasoning and action steps required to solve a task may not be known beforehand.

Therefore the fixed sequence:

```text
Model → Tool → Model → Stop
```

becomes a loop:

```text
          ┌─────────────┐
          │     LLM     │◄─────────┐
          └──────┬──────┘          │
                 ↓                 │
           Next action?            │
             /      \              │
          Tool      Answer         │
           ↓          ↓            │
        Execute      STOP          │
           ↓                       │
        Observe ───────────────────┘
```

This maps directly to a basic cognitive loop:

**Reason → Act → Observe → Reason**

Key insight:

**The loop is required because we may not know the exact number of steps needed to complete the task.**

---

### Lab 13 — Tool Registry and Runtime Control

```bash
python labs/13_tool_registry.py
```

Introduces a tool registry:

```python
tool_registry = {
    "get_order_status": get_order_status,
    "cancel_order": cancel_order
}
```

Python functions are first-class objects, so they can be stored in a dictionary and selected dynamically.

This removes hard-coded dispatch logic.

Conceptually:

```text
Model requests tool
       ↓
Tool Registry
       ↓
Python Function
       ↓
Enterprise Capability
```

The lab also introduces bounded execution using a maximum iteration count.

The preferred termination condition is:

```text
No more tool calls
      ↓
Final answer
      ↓
STOP
```

The maximum iteration count acts as a safety mechanism if the agent does not terminate normally.

Key principle:

**Agent autonomy should operate inside deterministic runtime boundaries.**

---

# The Agent Mental Model

At this stage we can distinguish an LLM from an agent.

An LLM provides reasoning and generation capability.

A basic agent requires more:

```text
              AGENT

               LLM
                +
              Tools
                +
          Context / State
                +
          Execution Loop
                +
        Runtime Controls
```

Or viewed cognitively:

```text
PERCEIVE
   ↓
REASON
   ↓
DECIDE
   ↓
ACT
   ↓
OBSERVE
   │
   └────→ REASON AGAIN
```

The runtime surrounds this loop with deterministic controls such as:

- allowed tools
- argument validation
- authorization
- approvals
- iteration limits
- timeouts
- guardrails
- observability

---

# Core Principles Learned So Far

### SDK ≠ API ≠ Model

```text
Application
    ↓
OpenAI SDK
    ↓
OpenAI API
    ↓
Model
```

A convenient Python method call may hide a distributed-system boundary involving serialization, HTTP, authentication, retries, failures, and remote execution.

### Context ≠ State ≠ Memory

These are separate architectural concerns and should not be treated as synonyms.

### Structured Outputs Create Typed AI Boundaries

```text
Natural Language
      ↓
LLM
      ↓
Structured Contract
      ↓
Normal Software
```

### Model Proposes — Runtime Executes

The model can request an action.

The runtime determines whether and how that action actually occurs.

### Prompts Are Not Business Controls

Prompts are useful behavioral guidance.

Critical authorization, financial, security, and compliance constraints should be enforced deterministically.

### Tool Results Are Observations

The result of an action becomes new information that the model can reason over.

### Agent Execution Is a Loop

```text
Reason → Act → Observe → Reason
```

The number of cycles may not be known in advance.

### Autonomy Requires Boundaries

The model may participate in deciding what happens next, but the runtime controls what it is actually permitted to do.

---

# Where the Journey Goes Next

The next stage explores what happens when frameworks begin implementing these mechanics for us.

Planned topics include:

1. OpenAI Agents SDK
2. Agent, Runner, tools and context
3. Sessions and state
4. Guardrails
5. Handoffs
6. Multi-agent systems
7. Agent orchestration patterns
8. LangGraph
9. Production agent architecture
10. Enterprise Order Exception Resolution reference architecture

The important difference is that we are entering those frameworks after manually understanding the mechanics they abstract.

The objective remains:

**Do not merely learn how to use an agent framework. Understand how agentic systems work.**