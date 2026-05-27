# SCL Core V2 — Context

## Glossary

**SCL (Structured Cognitive Loop)**
The name for the reasoning engine. SCL is the loop that drives `chat-wonder-v2-api`'s decisions and responses, making the reasoning behind each response observable in real-time.

**R-CCAM Loop**
The ordered sequence of phases that SCL executes for each user turn: Request → Retrieval → Cognition → Control → Action → Memory. Not all phases fire on every turn — Retrieval is skipped when RAG finds no match; Control, Action, and Memory only fire when the LLM proposes a tool call.

**Turn**
One complete R-CCAM execution triggered by a single user message.

**Cycle**
One LLM inference pass within a Turn. A Turn contains at least one Cycle; it gains a second (and possibly more) when a tool call is proposed, executed, and the result fed back to the LLM. Displayed in the tracer as "Cycle N — reasoning over M messages."

**Request (phase)**
The first phase. Broadcasts the incoming user message and session ID to the tracer. Always fires.

**Retrieval (phase)**
RAG lookup against the loaded embeddings (`basic_indexes.pkz`). Reports either the top-N chunks retrieved or "RAG not used" if no match crosses the threshold. Always fires, but may be a no-op.

**Cognition (phase)**
LLM prompt construction and inference. Reports: mode (persona), conversation history depth, available tools, and the proposed tool call (if any). Fires at the start of each Cycle.

**Control (phase)**
The decision gate. Covers all branching logic the loop takes after Cognition: whether to call a tool, escalate to HITL, or answer directly. Also performs deduplication ("no prior identical call found"). Fires only when a tool call is proposed.

**HITL (Human-In-The-Loop)**
One specific Control outcome. When a proposed tool call requires human approval, the loop pauses and emits a pending-approval event. Execution resumes only after the user approves or rejects via `/approve`. HITL is not a separate phase — it is handled within Control.

**Action (phase)**
Tool execution. Runs the approved tool and captures its result. Fires only after Control approves a tool call.

**Memory (phase)**
Stores the tool result as confirmed knowledge within the session. Fires immediately after Action. Memory in this phase refers to intra-session fact accumulation from tool results, not long-term storage or conversation history (which is tracked separately as turn history).

**Session**
A conversation context keyed by UUID, scoped to one user interaction. Holds turn history and accumulated Memory facts. Sessions are managed by `chat-wonder-v2-api`; SCL traces reference them by session ID.

**Tool**
A named, callable function exposed to the LLM. Defined in `basic_functions.zip`. The LLM selects a tool during Cognition; Control gates its execution; Action runs it; Memory records the result.

**Glass-Box Tracer**
The SCL observability layer. `scl_tracer_server.py` (port 8004) relays SSE events from `chat-wonder-v2-api`'s `/trace-stream` endpoint to browser subscribers, showing each R-CCAM phase as it executes.
