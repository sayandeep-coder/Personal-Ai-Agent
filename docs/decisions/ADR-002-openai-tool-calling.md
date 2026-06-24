# ADR-002: Why OpenAI Tool Calling instead of LangChain Agents

## Status

Accepted for Phase 1.

## Context

Personal-AI-Agent needs an agent runtime that can plan, select tools, execute integrations, and generate responses. The project uses Python and OpenAI, with tools for Gmail, Calendar, Drive, Docs, Sheets, GitHub, Weather, Maps, Memory, and Playwright.

Two implementation paths were considered:

| Option | Summary |
| --- | --- |
| OpenAI tool calling | Use OpenAI-native tool schemas and execute selected tools in our own runtime. |
| LangChain Agents | Use LangChain's agent abstractions, tool wrappers, chains, and agent executors. |

## Decision

Use OpenAI tool calling as the Phase 1 agent interface and implement orchestration, tool registry, policy checks, persistence, retries, and observability in our own application code.

LangChain may still be used selectively for isolated utilities if it proves valuable, but it should not own the core agent loop.

## Rationale

The core product requirement is controlled execution of personal tools with strong auditability. The system needs explicit control over permissions, confirmation gates, tool execution records, retries, memory injection, and failure modes. OpenAI tool calling provides a stable model-facing schema mechanism while keeping the critical runtime behavior inside our codebase.

## Pros

| Pro | Impact |
| --- | --- |
| Direct control of execution | Tool calls pass through local validation, policy, and audit layers. |
| Smaller abstraction surface | Fewer framework concepts between product logic and model behavior. |
| Better auditability | `agent_runs` and `tool_executions` map directly to our runtime. |
| Predictable failure handling | Retries, idempotency, and confirmation gates are explicit. |
| Easier security review | Tool permissions and side effects are implemented in one owned registry. |
| Lower dependency risk | Core behavior does not depend on fast-changing agent framework internals. |
| Strong schema alignment | OpenAI tool schemas are the contract the model actually sees. |

## Cons

| Con | Mitigation |
| --- | --- |
| More orchestration code to write | Keep the agent loop small and heavily tested. |
| Fewer prebuilt integrations | Implement only production-needed tools behind clean adapters. |
| Less framework convenience | Add targeted helpers for prompts, retries, and tracing. |
| Requires prompt/tool discipline | Version planner prompts and tool schemas. |
| Must build evaluation harness | Add golden tests and recorded tool-call fixtures. |

## Consequences

### Immediate Consequences

- The `agent/tools` package owns the Tool Registry.
- Each tool defines JSON schemas compatible with OpenAI tool calling.
- The agent loop must handle tool calls, tool results, and follow-up model calls.
- Tool execution must be recorded in `tool_executions`.
- OpenAI prompts and schemas require versioning.

### Long-Term Consequences

- The system has a stable internal agent runtime that can support multiple model providers later.
- The project can add a policy engine without fighting a framework's execution model.
- More implementation responsibility remains in the codebase, so tests and observability are mandatory.

## Alternatives Considered

### LangChain Agents

LangChain provides mature agent abstractions and many integrations. It was not selected as the primary runtime because Personal-AI-Agent requires tight control over execution boundaries, durable audit trails, and user-specific permission gates. Framework-owned loops can make it harder to reason about exactly when and why a tool executed.

LangChain may be reconsidered for:

- Document loaders or parsers.
- Evaluation helpers.
- One-off integration utilities.
- Non-critical prototypes.

### Fully Custom Model Prompting Without Tool Calling

Prompting the model to output ad hoc JSON was rejected because OpenAI tool calling already provides a structured, model-native schema contract. Ad hoc JSON would increase parsing failures and reduce clarity around tool availability.

## Review Trigger

Revisit this decision when:

- OpenAI tool calling no longer satisfies required planning behavior.
- A framework demonstrably reduces complexity without weakening audit/control.
- The project needs provider-neutral agent orchestration at a higher abstraction level.
- LangChain or another framework offers a production-grade execution model that maps cleanly to our policy and persistence requirements.

