# Agentic Systems Learning Journal

## From a Model Call to an Agent Loop

This journal captures the reasoning journey behind the first phase of the Agentic Systems Lab.

The purpose is not to memorize OpenAI SDK syntax. The purpose is to build a mental model of how an agentic system actually works.

When rereading this document, focus on the progression:

**Model → Structured Response → Context → Typed Output → Tool → Observation → Loop → Agent Runtime**

---

# 1. It Started With an Innocent Python Call

Our first program contained:

```python
response = client.responses.create(
    model="gpt-5.5",
    input="Explain what an order management system is in one sentence."
)
```

At first glance, this looks like an ordinary Python method call.

But it isn't just a local method invocation.

Conceptually:

```text
Python Application
       │
       ▼
   OpenAI SDK
       │
       ▼
serialization + HTTP + authentication
       │
       ▼
     NETWORK
       │
       ▼
   OpenAI API
       │
       ▼
      Model
```

The SDK is not the LLM.

The SDK is a client-side abstraction that helps our application communicate with the OpenAI platform.

This gives us our first mental model:

```text
Application → SDK → API → Model
```

The SDK hides complexity such as HTTP communication, serialization, authentication, errors, retries, and conversion between network representations and convenient Python objects.

Whenever an SDK makes something look simple, an architect should ask:

> What complexity is this abstraction hiding?

---

# 2. A Model Response Is More Than Text

Initially we used:

```python
response.output_text
```

This makes it easy to think:

> I send text to the LLM and receive text back.

But when we inspected the complete `response`, we discovered something more interesting.

The response contains information such as:

```text
Response
│
├── id
├── model
├── status
├── usage
└── output
```

And `output` itself contains typed output items.

So:

```python
response.output_text
```

is a convenience abstraction.

The deeper structure is closer to:

```text
Response
   │
   └── output[]
          │
          ├── message
          ├── function_call
          └── other supported output items
```

This becomes important later because an AI execution does not always produce human-facing prose.

Sometimes it produces an **action request**.

That leads to an important principle:

> AI execution returns structured results, not merely text.

---

# 3. Instructions and Input Have Different Jobs

Next we separated:

```python
instructions="..."
```

from:

```python
input="..."
```

The instructions describe relatively stable behavioral expectations.

For example:

```text
You are an order support assistant.
Be concise.
Do not invent order information.
```

The input represents the current request:

```text
Where is my order?
```

Conceptually:

```text
Behavior / Role
      │
 instructions
      │
      ▼
     MODEL
      ▲
      │
    input
      │
Current Request
```

But we also learned something more important.

A prompt such as:

```text
Never refund more than ₹5,000.
```

is behavioral guidance.

It is not the same as deterministic enforcement.

A real financial rule should look more like:

```python
if refund_amount > 5000:
    require_approval()
```

Therefore:

> Prompts guide behavior. Code enforces critical constraints.

This principle becomes increasingly important as agents gain access to real enterprise actions.

---

# 4. Intelligence Is Not Conversation State

We then performed an experiment.

First request:

```text
My order number is ORD-1234. Remember it.
```

Then we made an independent second request:

```text
What is my order number?
```

The second call did not automatically know the order number.

This exposed an important architectural distinction.

The model may be intelligent, but that does not mean two independent executions automatically share state.

We separated three concepts.

## Context

What information can the model see **during this inference**?

## State

What information does the system maintain as an interaction or process progresses?

## Memory

What information should persist and be recalled later?

Therefore:

```text
Context ≠ State ≠ Memory
```

These concepts interact, but they solve different problems.

---

# 5. Conversation Continuity Is a System Capability

We then used:

```python
previous_response_id=response1.id
```

Now a second response could continue from the first response.

Conceptually:

```text
Response 1
    │
    │ previous_response_id
    ▼
Response 2
```

This taught us another useful distinction.

A platform can provide mechanisms for maintaining continuity.

But the application still needs to determine:

```text
Which customer?
Which session?
Which conversation?
Which business process?
Which previous response?
```

Therefore:

> The platform may provide state mechanisms, but the application owns how those mechanisms map to business concepts.

---

# 6. The Application Can Also Build Context

Instead of relying on response chaining, we supplied conversation history ourselves.

Conceptually:

```text
Application
    │
    │ constructs context
    ▼
user: My order is ORD-1234
assistant: Understood
user: What is my order number?
    │
    ▼
   MODEL
```

This makes an important fact visible:

> The model does not need magical memory if the application provides the information required for the current inference.

Later, context assembly can become much more sophisticated:

```text
Context
│
├── recent messages
├── conversation summary
├── user information
├── retrieved knowledge
├── business state
└── relevant memories
```

We deliberately did not go deeper into context engineering yet.

---

# 7. Moving From Prose to Typed Contracts

Until this point, the model mainly produced prose.

Humans like prose.

Software usually prefers structure.

Instead of:

```text
"The customer is asking about order ORD-1234 and the request appears urgent."
```

our application would rather receive:

```text
order_id = ORD-1234
intent = track_order
urgency = high
requires_action = true
```

This introduced structured outputs.

We defined a Pydantic model:

```python
class OrderIntent(BaseModel):
    order_id: str
    intent: str
    urgency: str
    requires_action: bool
```

Initially this looked mysterious.

How can a remote LLM understand a Python class?

The answer was:

**It doesn't.**

When we write:

```python
text_format=OrderIntent
```

we are passing the Python class object to the SDK.

Because `OrderIntent` extends Pydantic's `BaseModel`, its structure can be represented as JSON Schema.

Conceptually:

```text
OrderIntent
Python class
     │
     ▼
Pydantic / SDK
     │
     ▼
JSON Schema
     │
     ▼
API
     │
     ▼
Model
```

On the return path:

```text
Model structured output
        │
        ▼
       API
        │
        ▼
       SDK
        │
        ▼
Pydantic parsing
        │
        ▼
OrderIntent instance
```

The mental shortcut is:

> Pydantic model → JSON Schema → model output → Pydantic object.

---

# 8. Why Structured Outputs Matter Architecturally

This pattern creates a bridge between two worlds.

```text
Unstructured World
      │
      │ natural language
      ▼
     LLM
      │
      │ structured interpretation
      ▼
Typed Software World
```

This is one of the ways a probabilistic AI component can participate cleanly in a conventional software architecture.

For example:

```text
Customer Message
      │
      ▼
     LLM
      │
      ▼
 OrderIntent
      │
 ┌────┼────────────┐
 ▼    ▼            ▼
Track Cancel      Return
```

Using enums made this contract even stronger.

Instead of allowing:

```text
intent = any arbitrary string
```

we constrained the vocabulary:

```text
TRACK_ORDER
CANCEL_ORDER
RETURN_ORDER
OTHER
```

The LLM performs interpretation.

The application receives a controlled representation.

---

# 9. Then We Gave the Model Tools

This was the point where the system started moving from understanding toward action.

We defined a tool:

```text
get_order_status(order_id)
```

and described it to the model using:

```text
name
description
parameter schema
```

A critical discovery followed.

The Python function itself was **not sent to the LLM**.

The model only knew:

```text
There is a capability called get_order_status.

It expects:
order_id: string
```

The model then produced:

```text
ResponseFunctionToolCall

type      = function_call
name      = get_order_status
arguments = {"order_id": "ORD-1234"}
call_id   = ...
```

This was not execution.

It was a proposal.

That gave us one of the most important principles of this entire learning journey:

> The model proposes actions. The runtime controls execution.

---

# 10. Cognitive Plane vs Execution Plane

The tool experiment exposed a useful architectural boundary.

```text
        COGNITIVE PLANE

             LLM
              │
              │ proposes
              ▼
 get_order_status("ORD-1234")

════════════════════════════════

        EXECUTION PLANE

          Agent Runtime
              │
              ▼
      get_order_status()
              │
              ▼
         Order System
```

The LLM decides that information is needed.

Our runtime determines whether the requested action should actually happen.

In a production system, the runtime might ask:

```text
Is this tool allowed?
Are the arguments valid?
Is the user authorized?
Does this action require approval?
Is this a duplicate request?
Does a guardrail permit execution?
```

Only then does execution occur.

This is why giving an LLM tools does not mean surrendering control to the LLM.

---

# 11. Tool Arguments Cross the Boundary as Data

The model returned:

```python
arguments='{"order_id":"ORD-1234"}'
```

Notice that this is JSON text.

Our runtime performed:

```python
arguments = json.loads(tool_call.arguments)
```

giving us a Python dictionary:

```python
{
    "order_id": "ORD-1234"
}
```

Then:

```python
get_order_status(**arguments)
```

effectively became:

```python
get_order_status(
    order_id="ORD-1234"
)
```

Again, the SDK/API boundary becomes visible:

```text
Serialized Data
      ↓
Python Representation
      ↓
Application Execution
```

---

# 12. Tool Results Become Observations

Executing the tool was not enough.

The model had requested information but had not yet seen the result.

Therefore we passed the tool result back to the model.

Conceptually:

```text
LLM
 │
 │ get_order_status
 ▼
Runtime
 │
 ▼
Tool
 │
 │ status = shipped
 ▼
Runtime
 │
 │ observation
 ▼
LLM
```

The `call_id` connects a tool result to the tool call that requested it.

Think of it conceptually as correlation:

```text
Tool Call
call_id = ABC
     │
     ▼
Execution
     │
     ▼
Tool Result
call_id = ABC
```

Now the model can reason over the new observation and answer:

```text
Your order has shipped and is expected on September 11.
```

This completed our first tool cycle:

```text
Reason
  ↓
Act
  ↓
Observe
  ↓
Reason
```

---

# 13. Why We Needed a Loop

Our first implementation assumed exactly one tool call.

But consider:

```text
Where is my order, and if it is delayed,
am I eligible for compensation?
```

Solving this might require:

```text
get_order_status()
       ↓
observe
       ↓
get_delivery_exception()
       ↓
observe
       ↓
get_compensation_policy()
       ↓
observe
       ↓
answer
```

We do not necessarily know the number of steps beforehand.

Therefore:

```python
while ...
```

appeared naturally.

Conceptually:

```text
        ┌──────────────┐
        │     LLM      │◄─────────────┐
        └──────┬───────┘              │
               │                      │
               ▼                      │
        What next?                    │
          /      \                    │
       Tool       Answer              │
        │           │                 │
        ▼           ▼                 │
     Execute       STOP               │
        │                             │
        ▼                             │
    Observation ──────────────────────┘
```

The reason for the loop is simple:

> We may not know the exact number of steps required to complete the task.

---

# 14. The Tool Registry

Initially we could write:

```python
if tool_call.name == "get_order_status":
    ...
elif tool_call.name == "cancel_order":
    ...
```

But this does not scale.

Instead we introduced:

```python
tool_registry = {
    "get_order_status": get_order_status,
    "cancel_order": cancel_order
}
```

This also reinforced a Python concept:

**Functions are first-class objects.**

A function can be:

- assigned to a variable
- stored in a dictionary
- passed as an argument
- retrieved dynamically
- invoked later

Therefore:

```python
tool_function = tool_registry.get(tool_call.name)
```

can retrieve the appropriate implementation.

Then:

```python
tool_function(**arguments)
```

executes it.

This creates a simple dispatcher:

```text
Model Tool Name
      ↓
Tool Registry
      ↓
Function Object
      ↓
Execution
```

There are also two different structures that must not be confused:

```text
tools
  ↓
describes capabilities to the MODEL

tool_registry
  ↓
maps capability names to implementations
for OUR RUNTIME
```

The model never needs access to the registry.

---

# 15. Output Items and Their Types

While building the loop we revisited:

```python
response.output
```

This is a collection of output items.

Each item can have a semantic type.

For our current learning, the two important ideas are:

```text
message
   ↓
model produced communication

function_call
   ↓
model requested an action
```

Our loop therefore filters:

```python
tool_calls = [
    item
    for item in response.output
    if item.type == "function_call"
]
```

`item` itself is merely our Python variable name.

The important thing is:

```python
item.type
```

The SDK may represent a function call as a Python object such as:

```text
ResponseFunctionToolCall
```

while the protocol-level discriminator remains:

```text
type = "function_call"
```

Mental model:

```text
API / Serialized Representation

"type": "function_call"
          │
          ▼
      OpenAI SDK
          │
          ▼
Python Representation

ResponseFunctionToolCall(...)
```

---

# 16. How Does the Agent Know When to Stop?

Our loop needed a termination condition.

The natural completion condition was:

```python
if not tool_calls:
    break
```

Meaning:

> The model no longer requires an action and has produced its answer.

But during development we accidentally placed the next model invocation outside the loop.

The result was educational.

The runtime inspected the same response five times:

```text
response 1
   ↓
tool call

iteration 1 → response 1
iteration 2 → response 1
iteration 3 → response 1
iteration 4 → response 1
iteration 5 → response 1
```

Moving the second model invocation inside the loop fixed the control flow:

```text
Iteration 1

LLM
 ↓
Tool Call
 ↓
Execute
 ↓
Tool Result
 ↓
Call LLM again


Iteration 2

LLM
 ↓
Final Answer
 ↓
No Tool Calls
 ↓
BREAK
```

This was also a useful reminder:

> In Python, indentation is part of the program's control flow.

---

# 17. Why Maximum Iterations Still Matter

Even when semantic completion works, we should not allow unlimited execution.

Therefore the runtime also has:

```python
max_iterations = 5
```

This gives us two termination mechanisms.

## Semantic termination

```text
Model has enough information
        ↓
No more tool calls
        ↓
Final answer
        ↓
STOP
```

## Hard runtime termination

```text
Model continues requesting actions
        ↓
Maximum iterations reached
        ↓
Runtime forces STOP
```

This leads to another important principle:

> Agent autonomy should operate inside deterministic boundaries.

---

# 18. So What Is an Agent?

We started this journey with an LLM.

Now we can see why:

```text
LLM ≠ Agent
```

An LLM provides reasoning and generation capability.

Our primitive agent now contains:

```text
               AGENT

                 LLM
                  │
        ┌─────────┼──────────┐
        │         │          │
     Context    Tools      State
        │         │          │
        └─────────┼──────────┘
                  │
             Agent Loop
                  │
                  ▼
              Runtime
```

The cognitive cycle looks like:

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
   └──────→ REASON AGAIN
```

And the runtime surrounds that cognition with control.

---

# 19. The Most Important Mental Model

If only one picture survives from this phase, let it be this:

```text
                  USER
                    │
                    ▼
             ┌────────────┐
             │    LLM     │
             │ cognition  │
             └─────┬──────┘
                   │
             proposes action
                   │
                   ▼
          ┌──────────────────┐
          │  AGENT RUNTIME   │
          │                  │
          │ validate         │
          │ authorize        │
          │ guard            │
          │ control          │
          │ execute          │
          └────────┬─────────┘
                   │
                   ▼
                 TOOL
                   │
                   ▼
          Enterprise System
                   │
                   ▼
                RESULT
                   │
                   │ observation
                   ▼
                  LLM
```

The LLM supplies cognition.

The runtime supplies control.

The tools supply capabilities.

Enterprise systems supply business truth and action.

---

# 20. The 80/20 Summary

Remember these principles:

**1. SDK → API → Model**

The SDK is an abstraction over remote platform interaction.

**2. A response is structured, not merely text.**

`output_text` is a convenience view.

**3. Context ≠ State ≠ Memory**

Treat them as separate architectural concerns.

**4. Natural Language → LLM → Typed Contract → Software**

Structured outputs bridge probabilistic interpretation and conventional software.

**5. Pydantic Model → JSON Schema → Model Output → Pydantic Object**

The remote model does not understand our Python class directly.

**6. Model Proposes → Runtime Executes**

Tool calling is an action-request protocol, not magical remote Python execution.

**7. Tool Result = Observation**

The model reasons again after observing the external result.

**8. Reason → Act → Observe → Reason**

This is the heart of our primitive cognitive loop.

**9. Unknown number of steps → Agent Loop**

A loop allows iterative reasoning and action.

**10. Autonomy Lives Inside Deterministic Boundaries**

The model may decide what it wants to do next. The runtime determines what it is allowed to do.

---

# What Comes Next

We deliberately built these mechanics ourselves before using an agent framework.

The next question is:

> How much of this code should we really have to write ourselves?

That takes us to the next stage:

**OpenAI Agents SDK**

There we will look for abstractions corresponding to concepts we already understand:

```text
Our Manual Implementation      Framework Concept

LLM call                  →    Agent / model execution
tools list                →    Tools
tool registry             →    Tool registration
while loop                →    Runner / execution loop
tool result               →    Observation
conversation state        →    Sessions / context
runtime controls          →    Guardrails
agent transitions         →    Handoffs
```

Instead of memorizing a new framework, we will ask:

> What part of the system we just built is this framework abstracting?

That is the foundation for understanding agent frameworks rather than merely knowing how to use them.