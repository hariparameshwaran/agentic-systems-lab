# Agentic Systems — Architecture Notes

## 1. Core Stack

```text id="ah16v6"
Application
    ↓
OpenAI SDK
    ↓
OpenAI API
    ↓
Model
```

**SDK ≠ API ≠ Model**

The SDK hides a distributed-system boundary: serialization, HTTP, authentication, failures, retries, rate limits, and response deserialization.

---

# 2. LLM ≠ Agent

An LLM provides reasoning and generation.

An agent adds capabilities and an execution environment.

```text id="f12l22"
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

---

# 3. Cognitive Loop

```text id="ugtyz8"
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
   └──────→ REASON
```

Simplified:

**Reason → Act → Observe → Reason**

A tool result is an **observation** that becomes new input to reasoning.

---

# 4. Cognitive Plane vs Execution Plane

```text id="cjgyvq"
        COGNITIVE PLANE

             LLM
              │
        proposes action
              │
══════════════╪══════════════
              │
        EXECUTION PLANE
              │
              ▼
        Agent Runtime
              │
        validate
        authorize
        guard
        execute
              │
              ▼
             Tool
              │
              ▼
      Enterprise System
```

Core principle:

**Model proposes. Runtime executes.**

Never confuse model intent with authorized execution.

---

# 5. Tool Architecture

The model receives a **tool contract**:

```text id="syuw8d"
Tool
├── name
├── description
└── parameter schema
```

The model does **not** receive the Python implementation.

Runtime execution:

```text id="4i85kg"
Model
  │
  │ tool name + arguments
  ▼
Tool Registry
  │
  ▼
Python Function
  │
  ▼
Service Layer
  │
  ▼
Enterprise System
```

Recommended enterprise layering:

```text id="bsuc8q"
AGENT
Reasoning / instructions
        ↓
TOOL
Agent-accessible capability
        ↓
SERVICE
Deterministic business logic
        ↓
ENTERPRISE SYSTEM
OMS / CRM / API / DB / Kafka
```

---

# 6. Tools vs Tool Registry

```text id="m4x8vc"
tools
  ↓
Describes available capabilities
to the MODEL


tool_registry
  ↓
Maps tool names to implementations
inside the RUNTIME
```

Example:

```text id="zfx3pg"
"get_order_status" → get_order_status()
"cancel_order"     → cancel_order()
```

---

# 7. Structured AI Boundary

Free-form text is useful for humans.

Software often needs typed contracts.

```text id="wwrhyu"
Natural Language
      ↓
     LLM
      ↓
Structured Output
      ↓
Typed Application Object
      ↓
Deterministic Software
```

With Pydantic:

```text id="f8l6t8"
Pydantic Model
      ↓
JSON Schema
      ↓
Model
      ↓
Structured Output
      ↓
Pydantic Object
```

Use structured outputs when downstream software must reliably interpret model output.

---

# 8. Context, State and Memory

Do not use these interchangeably.

### Context

Information available to the model **during the current inference**.

### State

Information maintained while an interaction or process progresses.

### Memory

Information deliberately persisted and recalled later.

```text id="k4dv9u"
Context ≠ State ≠ Memory
```

Context may be assembled from:

```text id="lv5dhc"
Context
├── current request
├── recent conversation
├── summaries
├── business state
├── retrieved knowledge
└── relevant memories
```

---

# 9. Agent Runtime Loop

```text id="1f60uv"
              ┌─────────────┐
              │     LLM     │◄────────────┐
              └──────┬──────┘             │
                     ↓                    │
               Next action?               │
                /       \                 │
             Tool       Answer            │
              │           │               │
              ▼           ▼               │
           Runtime       STOP             │
              │                           │
              ▼                           │
            Tool                           │
              │                           │
              ▼                           │
         Observation ─────────────────────┘
```

The loop exists because the number of reasoning/action steps may not be known beforehand.

---

# 10. Termination

Agents need explicit termination behavior.

### Semantic termination

```text id="d1r4c3"
Enough information
      ↓
No more tool calls
      ↓
Final answer
      ↓
STOP
```

### Runtime termination

```text id="1jdjhp"
Maximum iterations
Timeout
Budget exhausted
Policy violation
Human intervention
      ↓
STOP
```

Core principle:

**Autonomy must operate inside deterministic boundaries.**

---

# 11. Prompt Guidance vs Deterministic Control

Prompt:

```text id="x45zfj"
"Do not refund more than ₹5,000."
```

Useful guidance, but not sufficient enforcement.

Runtime:

```text id="e75d47"
refund > ₹5,000
      ↓
require approval
```

Use deterministic enforcement for:

- authorization
- financial limits
- compliance
- security
- destructive operations
- approvals
- idempotency

Core principle:

**Prompts guide behavior. Code enforces critical constraints.**

---

# 12. Agent Runtime Responsibilities

A production runtime may need to control:

```text id="h1uywd"
Tool allow-list
Argument validation
Authorization
Policy enforcement
Human approval
Idempotency
Timeouts
Retries
Maximum iterations
Cost / token budgets
Observability
Audit trail
Guardrails
Error handling
```

The model should not own these responsibilities.

---

# 13. Three Loops Mental Model

As systems become more sophisticated, distinguish three nested concerns.

```text id="njtw7d"
BUSINESS / PROCESS LOOP
"What business step executes next?"
          │
          ▼
   AGENT COGNITIVE LOOP
   "What should I do next?"
          │
          ▼
      LLM / TOOL LOOP
   "Call model / execute tool"
```

Do not automatically use an LLM to control every transition.

Sometimes:

```text id="s2m5oa"
LLM decides
```

Sometimes:

```text id="fkmh1w"
Code decides
```

Sometimes:

```text id="dyk3lg"
Workflow / graph decides
```

This distinction becomes important when studying LangGraph and enterprise process orchestration.

---

# 14. Enterprise Agent Mental Model

```text id="v0x79f"
                  USER / EVENT
                       │
                       ▼
               ┌───────────────┐
               │ AGENT RUNTIME │
               └───────┬───────┘
                       │
               Context Assembly
                       │
                       ▼
                   ┌───────┐
                   │  LLM  │
                   └───┬───┘
                       │
                  Tool Request
                       │
                       ▼
               Runtime Controls
                       │
        ┌──────────────┼───────────────┐
        │              │               │
    Guardrails    Authorization    Approval
        │              │               │
        └──────────────┼───────────────┘
                       │
                       ▼
                     Tool
                       │
                       ▼
                  Service Layer
                       │
                       ▼
               Enterprise Systems
                       │
                       ▼
                    Result
                       │
                       ▼
                  Observation
                       │
                       └──────→ LLM
```

---

# 15. Ten Principles to Remember

1. **SDK ≠ API ≠ Model**

2. **AI responses are structured results, not merely text.**

3. **Context ≠ State ≠ Memory.**

4. **Natural language can be converted into typed application contracts.**

5. **The model proposes; the runtime executes.**

6. **Tool results become observations for further reasoning.**

7. **Reason → Act → Observe → Reason is the core cognitive loop.**

8. **The number of agent steps may not be known beforehand.**

9. **Prompts guide behavior; deterministic code enforces critical constraints.**

10. **Agent autonomy must live inside deterministic runtime boundaries.**

---

# 16. Architecture Question to Keep Asking

Whenever introducing an agentic capability, ask:

> **What should the model decide, and what should deterministic software control?**

That single question prevents many poor agentic architectures.