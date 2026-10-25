# Microsoft Foundry Study Guide for AI-103: Developing AI Apps and Agents on Azure

_Last updated: 24 October 2026_

> Uses current **Microsoft Foundry** terminology (older material may say **Azure AI Foundry**). The structure follows the **AI-103** exam domains.

## How this guide maps to the AI-103 exam

| Exam domain (weight) | Covered in |
|---|---|
| **Plan and manage an Azure AI solution** (25–30%) | Parts I–III |
| **Implement generative AI and agentic solutions** (30–35%) | Parts IV–VIII |
| **Implement computer vision solutions** (10–15%) | Part IX |
| **Implement text analysis solutions** (10–15%) | Parts X–XI |
| **Implement information extraction solutions** (10–15%) | Parts XII–XIII |

---

# Part I: Foundations and model selection

## 1. The big picture

A **model** generates a response. An **agent** wraps a model with instructions, conversation state, knowledge, tools, orchestration, identity, and monitoring. Agent safety must therefore cover not only prompts and answers, but also proposed tool calls and returned tool data.

```text
User
  -> input guardrail
  -> agent/model
       -> tool-call guardrail (agent only)
       -> tool
       -> tool-response guardrail (agent only)
  -> output guardrail
  -> user
```

Everything else in this guide hangs off this picture: you **choose a model**, **deploy** it, **secure and monitor** it (Parts II–III), **build apps and agents** on it (Parts IV–VI), make it **responsible/safe** (Part VII), optionally **fine-tune** it (Part VIII), and add **vision, language, speech, and retrieval** capabilities (Parts IX–XIII).

## 2. Choosing a model

Foundry's model catalog spans several families. Pick by **task + modality + cost/latency**, not by brand.

| Model type | What it is | Choose it when |
|---|---|---|
| **LLM (large language model)** | High-capability text model (e.g. GPT-4o, GPT-4.1). | Complex reasoning, broad knowledge, high-quality generation. |
| **SLM (small language model)** | Smaller, cheaper, faster model (e.g. Phi family). | High volume, low latency, edge/cost-sensitive, narrow tasks; can be fine-tuned to punch above its size. |
| **Reasoning model** | Optimised for multi-step logic (e.g. o-series). | Hard math, planning, tool-use chains where correctness beats speed/cost. |
| **Multimodal model** | Accepts/produces more than text — images, audio (e.g. GPT-4o, GPT-image, Sora). | Vision understanding, image/video generation, audio-native interactions. |
| **Code model** | Tuned for code generation/completion. | Code-heavy generation, refactoring, structured function calling. |
| **Embedding model** | Turns text/images into vectors. | Vector/semantic search and RAG retrieval (not generation). |
| **Foundry Tools / task models** | Managed task capabilities (Translator, Speech, Content Understanding, Document Intelligence, etc.). | Well-defined tasks where a purpose-built service beats prompting an LLM. |

**Selection rule of thumb:** start with the **smallest/cheapest model that meets quality**, measure with evaluations (Part VII), then move up only if needed. Match **modality** to the task, and prefer a **Foundry Tool** over a general LLM for a well-defined task (translation, OCR, transcription).

## 3. Choosing the right Foundry capability

| Task | Use |
|---|---|
| Generate text / chat / reasoning | A deployed LLM/SLM via the inference APIs (Part V) |
| Ground answers on your data (RAG) | Azure AI Search + embeddings, or **Foundry IQ** (Part XIII) |
| Vector / hybrid / semantic search | Azure AI Search (Part XIII) |
| Orchestrate tools + memory + autonomy | Foundry **agents** (Part VI) |
| Image/video generation or editing | Image/video generation models (Part IX) |
| Understand images/video | Multimodal models / Content Understanding (Part IX) |
| Analyse or translate text | Language service / Translator / LLM prompting (Part X) |
| Speech in/out | Azure AI Speech (Part XI) |
| Extract structured data from documents | Document Intelligence / Content Understanding (Part XII) |

---

# Part II: Model and agent deployment

## 4. What deployment type controls

For serverless Microsoft Foundry model deployments, type determines:

- where inference data can be processed;
- usage-based versus reserved-capacity billing;
- throughput and latency characteristics;
- synchronous versus asynchronous processing.

Open-source and custom models on managed compute use a different deployment approach and do not use all these serverless SKUs.

## 5. Three independent dimensions

### 1. Processing scope

- **Global:** inference may run in any Azure region.
- **Data Zone:** inference stays within a Microsoft-defined zone, such as EU, US, or Asia Pacific.
- **Azure geography/regional:** prompts and responses remain in the customer-specified Azure geography, though processing may move between regions within it.

For all types, data at rest remains in the designated Azure geography. The distinction concerns inference processing.

### 2. Capacity and billing

- **Standard:** pay per token on shared/serverless capacity.
- **Provisioned:** reserved capacity using Provisioned Throughput Units (PTUs) for predictable throughput and lower latency variation.
- **Batch:** discounted asynchronous processing for delay-tolerant bulk work.

### 3. Special purpose

- **Developer:** temporary evaluation of a fine-tuned model, without normal production guarantees.
- **Instant access:** preview capability to call supported models without a deployment. It is not a deployment type.

## 6. Deployment comparison

| Deployment type | Typical SKU | Processing | Billing/capacity | Best fit |
|---|---|---|---|---|
| **Global Standard** | `GlobalStandard` | Any Azure region | Pay per token | Default starting point, broad availability/quota |
| **Data Zone Standard** | `DataZoneStandard` | Selected data zone | Pay per token | Online workloads needing zone processing boundaries |
| **Standard** | `Standard` | Selected Azure geography | Pay per token | Geography-specific processing requirements |
| **Global Provisioned** | `GlobalProvisionedManaged` | Any Azure region | Reserved PTUs | Stable high-throughput global workloads |
| **Data Zone Provisioned** | `DataZoneProvisionedManaged` | Selected data zone | Reserved PTUs | Predictable throughput plus zone boundary |
| **Regional Provisioned** | `ProvisionedManaged` | Selected Azure geography | Reserved PTUs | Predictable throughput plus geography boundary |
| **Global Batch** | `GlobalBatch` | Any Azure region | Discounted asynchronous | Large global offline jobs |
| **Data Zone Batch** | `DataZoneBatch` | Selected data zone | Discounted asynchronous | Large offline jobs with zone restriction |
| **Developer** | `DeveloperTier` | See current model documentation | Pay per token | Short-lived fine-tuned-model evaluation (about 24-hour lifetime, no SLA or residency guarantee) |

Availability is model- and region-specific.

## 7. Simple selection guide

```text
Need a normal online endpoint?
  -> Start with Global Standard
       |
       +-- Inference must remain in EU/US/APAC zone?
       |     -> Data Zone Standard
       |
       +-- Inference must remain in an Azure geography?
       |     -> Standard
       |
       +-- Need stable reserved throughput at scale?
             -> Matching Provisioned type

Need large, delay-tolerant offline processing?
  -> Global Batch or Data Zone Batch

Only validating a fine-tuned model temporarily?
  -> Developer, if supported
```

## 8. Key trade-offs

- **Global Standard:** broad capacity and early model availability, but global processing can violate residency requirements.
- **Data Zone Standard:** zone-level processing with usage billing, but availability and quota can differ.
- **Standard/geography:** geography-level processing, but new models and capacity can arrive later.
- **Provisioned:** predictable throughput, but requires capacity planning and commitment.
- **Batch:** lower-cost bulk processing, but asynchronous and unsuitable for interactive chat.
- **Developer:** useful for evaluation, but temporary and not for normal production.

## 9. Standard (pay-as-you-go) and quota

With a **Standard** deployment you pay **per token** and share capacity with other customers. You don't reserve anything.

Your limit is a **TPM quota** (Tokens Per Minute), granted per **subscription + region + model**:

- It's a **ceiling** on how many tokens/min you may consume — not reserved capacity.
- Both input and output tokens count against it.
- Go over it → requests are **throttled (HTTP 429)**; wait and retry.
- Actual speed also depends on free shared capacity at that moment, so it can vary under load.

**Good for:** low, spiky, or unpredictable traffic — you only pay for what you use.

## 9a. Handling 429: retry with exponential backoff and jitter

A **429 (Too Many Requests)** means you hit a rate limit (TPM/RPM quota, or shared-capacity pressure). The fix is a **retry strategy**, not more immediate calls.

- **Exponential backoff:** wait progressively longer between retries (e.g. 1s → 2s → 4s → 8s), capped at a max.
- **Jitter:** add a small **random** offset to each wait so many clients don't retry at the exact same instant.
- **Respect `Retry-After`:** if the response carries a `Retry-After` header, wait at least that long.

**Why not retry immediately?** Immediate retries pile more load onto an already-throttled endpoint and just earn more 429s. **Why jitter?** Without it, all throttled clients retry in lockstep, creating **retry storms** (synchronized spikes) that re-trigger throttling.

**Exam clues → answer:**

- "requests fail with **429** / rate limited" → **retry with exponential backoff**.
- "many clients retry at once / thundering herd / retry storm" → **add jitter**.
- "need to **avoid 429 entirely / guaranteed throughput**" → **Provisioned (PTU)** (§10) or raise quota.

**Distractors:** retry instantly, retry on a fixed short delay, or raise `max_tokens` — none address rate limiting.

## 10. Provisioned (PTU) and how it works

A **PTU (Provisioned Throughput Unit)** is a block of **reserved throughput** you buy for a model — guaranteed tokens/min that are yours alone, not shared.

- More PTUs = more throughput.
- You pay for the block **even when idle**.
- Gives **guaranteed throughput** and **stable latency**.

**How you use it:**

1. Put peak **requests/min** + **input/output tokens** into the Foundry **capacity calculator** → it tells you how many PTUs you need (e.g. **100**).
2. Each model has a **minimum** PTU and an **increment** (step size). You can't start below the minimum, and you can only add capacity in whole steps — so if the step is 5, valid sizes are 15, 20, 25… (round up, e.g. 102 → 105). Numbers are model- and region-specific.
3. You need **PTU quota ≥** that number. PTU quota is a **separate bucket** from Standard TPM quota — having lots of TPM quota gives you zero PTU quota. Request an increase if it's too low.
4. Create the deployment → that throughput is locked and yours.
5. Traffic **over** your PTUs → throttled (429), or spills over to a Standard deployment if configured.
6. A monthly/yearly **reservation** only lowers the price — it doesn't change capacity.

**Good for:** high, steady, production traffic needing guaranteed speed and predictable cost.

> **Quota in one line:** quota = your allowance (max you may deploy/consume). Standard **TPM** quota and Provisioned **PTU** quota are **separate buckets**.

## 11. Model version upgrade policy

**Model version upgrade policy** controls what a deployment does when Azure releases a **new version of the same model** (e.g. a newer `gpt-4o` snapshot). You set it per deployment.

| Policy | What it does |
|---|---|
| **`OnceNewDefaultVersionAvailable`** (default) | Auto-upgrades to the new version shortly after Azure makes it the default. |
| **`OnceCurrentVersionExpired`** | Stays on the current version and only upgrades when that version is **retired/expired**. |
| **`NoAutoUpgrade`** (pin / "None") | Never auto-upgrades. You stay on the exact version and upgrade **manually**. |

**Why it matters:**

- **Agents on that model:** if the deployment auto-upgrades, an agent built on it suddenly runs on a new model version — outputs and behaviour can shift, so **re-run your evaluations/regression tests** after an upgrade. Pinning (`NoAutoUpgrade`) gives stable, reproducible behaviour.
- **Fine-tuning:** a fine-tuned model is tied to a **specific base-model version**, so it is effectively **pinned** — auto-upgrade doesn't silently swap the base. To move to a newer base version you generally **re-tune**.

> One line: auto-upgrade = always current but can change behaviour; pin = stable but you own the upgrade. Fine-tunes are pinned to their base version.

---

# Part III: Security, identity, and operations

## 12. Identity and keyless authentication

Foundry resources support two auth styles. **Keyless (Microsoft Entra ID) is strongly preferred** for production.

| Approach | How | Notes |
|---|---|---|
| **API keys** | Static key in the request header. | Simple, but a long-lived secret to store/rotate/leak. Good for quick tests only. |
| **Microsoft Entra ID (keyless)** | Caller presents an Entra token; no secret in code. | Preferred. Use **managed identity** for Azure-hosted apps, or developer identity locally. |

- **Managed identity** gives an Azure resource (Container App, Function, VM, App Service) its own Entra identity — no credentials in code. System-assigned (tied to the resource) or user-assigned (shared across resources).
- In the SDK, **`DefaultAzureCredential`** automatically uses managed identity in Azure and your signed-in developer identity locally — the same code works in both.
- **Disable local auth** (turn off key-based access) to force Entra-only, and store any remaining secrets in **Azure Key Vault**.

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

project_client = AIProjectClient(
    endpoint=foundry_project_endpoint,
    credential=DefaultAzureCredential(),   # managed identity in Azure, dev identity locally
)
```

## 13. Network isolation

- **Private endpoints** put the resource on your VNet with a private IP; traffic avoids the public internet.
- **Disable public network access** so the resource is reachable only through the private endpoint.
- Combine with VNet integration for the compute (agent host, function, container app) so the whole path is private.
- Hosted agents can add **network-egress controls** (preview) to restrict what the agent can call out to.

## 14. RBAC roles

Access is granted with **Azure RBAC** at subscription/resource-group/resource scope — assign the **least-privilege** built-in role rather than Owner.

| Role (example) | Grants |
|---|---|
| **Azure AI Developer** | Build/run in a Foundry project (agents, deployments, inference) without full management. |
| **Cognitive Services User** | Call the data plane (inference) of an AI Services resource. |
| **Cognitive Services Contributor** | Manage AI Services resources. |
| **Search Index Data Reader / Contributor** | Read / write Azure AI Search index data (for RAG). |
| **Storage Blob Data Reader/Contributor** | Read/write blob content used as knowledge sources. |

Give the app's **managed identity** the specific data-plane roles it needs (e.g. *Cognitive Services User* + *Search Index Data Reader*), not broad management roles.

## 14a. RBAC quick reference: create vs configure vs deploy vs manage access

Pick the **least-privileged** role that covers the exact verb in the scenario.

| Role | Create/manage resources | Configure/deploy | Data plane (inference) | Assign roles (manage RBAC) |
|---|:--:|:--:|:--:|:--:|
| **Owner** | ✅ | ✅ | ✅ | ✅ |
| **Contributor** | ✅ | ✅ | ✅ | ❌ |
| **Cognitive Services Contributor** | ✅ (AI Services) | ✅ | ✅ | ❌ |
| **Cognitive Services User** | ❌ | ❌ | ✅ | ❌ |
| **Azure AI Developer** | ❌ | build/run in a project | ✅ | ❌ |

**Decision rules:**

- "**create / provision / configure / deploy** a resource" → **Contributor** (or *Cognitive Services Contributor* for AI Services).
- "**call the model / analyse text / use the endpoint**" (data plane only) → **Cognitive Services User**.
- "**assign roles / grant others access / manage RBAC**" → **Owner** (or *User Access Administrator*).
- The phrase "**least privilege**" is usually the deciding clue — never pick Owner when a narrower role fits.

**Trap:** Owner and Contributor both manage resources, but **only Owner can assign roles**. A management role (Contributor) does **not** imply the ability to grant access.

## 15. CI/CD for Foundry projects

- Keep agent definitions, prompts, infra (Bicep/Terraform), and eval datasets in **source control**.
- In the pipeline: provision/update infra → deploy model/agent versions → **run the evaluation suite** (Part VII) → **gate promotion** on quality/safety thresholds → publish a versioned agent.
- Version everything together: agent definition, dataset, evaluator, judge model, and thresholds, so results are reproducible.
- Automation must **enforce** the gate — an eval threshold is only a release gate if the pipeline blocks on it.

## 16. Monitoring and observability

Watch two layers in production:

- **Operational:** latency, throughput, errors, **token usage/cost**, 429 throttling, tool failures.
- **Quality & safety:** **groundedness**, task adherence, **model drift**, harmful-content/safety-event rates, refusal rates.
- **Retrieval health (for RAG):** data-ingestion quality, **search index health**, and relevance performance.

Implement it with **tracing** (per-call timings, dependencies, tool steps), telemetry to **Application Insights / Azure Monitor**, and **continuous/online evaluation** on sampled production traffic. Re-evaluate after changing the model, instructions, tools, data, retrieval, or guardrails.

## 16a. Token usage vs evaluation (cost vs quality)

Two concerns that look similar in scenarios but need different answers:

| The scenario is about… | It's a… | Measure with |
|---|---|---|
| **Rising cost, bill, spend, capacity, 429s** | **Token usage** metric | token counts / cost telemetry (monitoring) |
| **Is the answer good, correct, grounded, relevant** | **Evaluation** | evaluators (§33–38) |

**Decision rules:**

- "costs are **increasing** / reduce spend / too many tokens / hitting quota" → **token usage** (operational metric).
- "answers are **wrong / ungrounded / low quality / hallucinating**" → **evaluation** (quality/groundedness).

**Trap:** an evaluator does **not** measure cost, and a token counter does **not** measure quality. Match the metric to whether the concern is **money/throughput** (tokens) or **answer goodness** (evaluation).

## 16b. Tracing and content recording (`enable_content_recording`)

Tracing normally records **metadata** (timings, spans, token counts, tool names) but **not** the message content. Turning on **content recording** captures the actual payloads.

- `enable_content_recording=true` (OpenTelemetry / agent tracing) records **prompts, model responses, and tool-call inputs/outputs** into the traces.
- **Use it for:** debugging, quality analysis, and building evaluation datasets from real traffic.
- **Compliance implication:** recorded prompts/responses/tool payloads may contain **PII or sensitive data**, so it is governed by privacy/data-handling policy — enable deliberately, restrict access, and apply retention/redaction. Many orgs keep it **off by default in production**.

**Exam clue:** "capture the **actual prompts and responses** for debugging/evaluation" → **enable content recording**; "but beware **sensitive data**" → the compliance caveat.

---

# Part IV: Foundry SDK clients

A frequent confusion: the difference between `AIProjectClient`, `get_openai_client()`, and a standalone `AzureOpenAI`. The split is simple: **one manages the project, two run inference.**

## 17. The three clients

| Client | Plane | Use it to |
|---|---|---|
| **`AIProjectClient`** | Control (manage) | Manage project resources: `.agents`, `.connections`, datasets, indexes, evaluations, deployments. |
| **`project_client.get_openai_client()`** | Data (run) | Run inference **inside** a Foundry project — endpoint + auth already wired for you. |
| **`AzureOpenAI`** | Data (run) | Run inference against an Azure OpenAI endpoint **with no project** — you set `azure_endpoint`, `api_version`, and auth yourself. |

Imports: `from azure.ai.projects import AIProjectClient` · `from openai import AzureOpenAI`.

```text
AIProjectClient            # control plane: agents, connections, eval, data
   └── get_openai_client() # data plane: inference (OpenAI-compatible)
         ≈ AzureOpenAI     # same inference methods, but project-wired for you
```

- `AIProjectClient` is the **entry point**; `get_openai_client()` hands you a project-scoped OpenAI client, so you never hard-code the model endpoint or redo auth.
- `AzureOpenAI` is the same inference surface (`.responses`, `.chat.completions`, `.embeddings`, …) **without** the project layer — no `.agents`, no `.connections`.
- Plain **`OpenAI`** points at OpenAI.com, not Azure — not used for Foundry work.

| Goal | Client |
|---|---|
| Create/version agents, manage connections, run evaluations | `AIProjectClient` |
| Run inference **inside** a Foundry project | `project_client.get_openai_client()` |
| Call an Azure OpenAI endpoint **with no project** | `AzureOpenAI` |

---

# Part V: Inference APIs and prompt engineering

## 18. The four calls

These four calls look similar but sit at different layers. Understanding how they **combine** is the point.

| Call | Layer | What it does |
|---|---|---|
| **`chat.completions.create(...)`** | Stateless inference | The classic Chat Completions API. You send the full message list every time; the server keeps **no** state. `.parse(...)` is the structured-output variant that validates the reply against a schema/Pydantic model. |
| **`responses.create(...)`** | Stateless or stateful inference | The newer **Responses API**. Simpler input (`input=`, `instructions=`), supports tools, streaming, and can attach to a server-side `conversation`. Preferred for new Foundry work. |
| **`conversations.create(...)`** | Server-side state | Creates a **conversation object** that stores turn history on the server. You then pass its `id` to `responses.create(conversation=...)` instead of resending history. |
| **`agents.create_version(...)`** | Control plane (definition) | Creates/updates a **durable agent version** (model + instructions + tools + policy) via `AIProjectClient.agents`. It does **not** run inference — it defines the agent you later invoke. |

## 19. How they differ and combine

- **chat.completions**: you manage history yourself (resend every message). `.parse` gives typed/structured output.
- **responses**: newer, cleaner input shape, native tools + streaming, optional server-side conversation state. Prefer **responses** for Foundry unless you need chat.completions compatibility.
- **conversations.create()** is **not** an inference call — it returns a state container you attach to `responses.create`.
- **agents.create_version** defines the agent once (control plane); you **invoke** it via `responses.create` with an `agent_reference`, optionally inside a conversation.

```python
# 1. Define the agent (control plane, once)
agent = project_client.agents.create_version(
    agent_name="MCP-Integrated-Agent",
    definition=PromptAgentDefinition(
        model=model_deployment_name,
        instructions="You are a helpful AI Assistant with tools integration.",
        tools=[mcp_tool],
    ),
)

# 2. Keep per-user state (data plane)
conversation = openai_client.conversations.create()

# 3. Invoke the agent version in that conversation (data plane)
openai_client.responses.create(
    conversation=conversation.id,
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    input=user_input,
    stream=True,
)
```

```text
agents.create_version   = define the agent      (control plane, durable)
conversations.create    = remember the session  (data plane, state)
responses.create        = run a turn            (data plane, execution)
chat.completions.create = run a stateless turn  (data plane, no server state)
       .parse           = same, but typed/structured output
```

## 20. Prompt engineering and model parameters

Before fine-tuning (Part VIII), shape behaviour with **prompting** and **parameters** — cheaper and faster to iterate.

### Prompting techniques

- **System / instructions message:** sets role, rules, and constraints. The strongest lever on behaviour.
- **Few-shot examples:** include input→output examples to teach format and style.
- **Grounding:** inject retrieved context (RAG) and tell the model to answer only from it — reduces fabrication.
- **Chain-of-thought / step-by-step:** ask for reasoning on hard tasks (or use a reasoning model).
- **Structured outputs:** request JSON against a schema (`responses` structured output / `chat.completions.parse`) for reliable machine-readable results.

### Key model parameters

| Parameter | Effect |
|---|---|
| **`temperature`** | Randomness. Low (0–0.3) = focused/deterministic; high (0.7–1) = creative/varied. |
| **`top_p`** | Nucleus sampling — alternative to temperature (sample from the top *p* probability mass). Tune one, not both. |
| **`max_tokens` / `max_output_tokens`** | Caps the response length (and cost). |
| **`stop`** | Sequences that end generation. |
| **`seed`** | Requests more reproducible output for the same input. |
| **`frequency_penalty` / `presence_penalty`** | Reduce repetition / encourage new topics. |

> Rule of thumb: for **factual/extraction** tasks use **low temperature**; for **creative** tasks raise it. Control length and cost with **max_tokens**, and prefer **structured outputs** when another system consumes the result.

---

# Part VI: Agents — lifecycle, tools, and orchestration

An **agent** is a durable **definition/version** (model + instructions + tools + policy). A **session/conversation** gives continuity across turns; a **run/response** performs one task.

## 21. Development and operational lifecycle

1. **Define use case and risk**: task, users, data, autonomy, forbidden actions, success criteria, and approval points.
2. **Choose agent type**: prompt, voice-based prompt, or hosted agent.
3. **Choose and deploy the model**: balance quality, tools, latency, cost, capacity, and data-processing needs.
4. **Create the agent**: configure instructions, model, tools, knowledge, identity, and session behaviour.
5. **Add data and tools**: connect only what is required and apply least privilege.
6. **Add guardrails and deterministic controls**: cover inputs, tools, outputs, schemas, approvals, and limits.
7. **Test and trace**: use normal, edge, adversarial, and failure cases; inspect model and tool calls.
8. **Evaluate**: measure quality, safety, retrieval, task outcome, and tool behaviour against repeatable tests.
9. **Optimize hosted agents (preview)**: tune hosted-agent configuration and performance before publishing.
10. **Version and publish**: save a known version and expose a stable integration.
11. **Monitor production**: watch latency, errors, token usage, safety signals, tool failures, and quality drift.
12. **Improve or roll back**: change model, instructions, tools, retrieval, or policy; then rerun regression tests.
13. **Retire**: remove access, revoke connections/identities, preserve required audit evidence, and migrate users.

## 22. Runtime lifecycle of one agent request

```text
Receive input
  -> inspect input
  -> load session/context
  -> model plans or selects next step
  -> optional tool call
  -> inspect and authorise tool call
  -> execute tool
  -> inspect tool response
  -> model continues with updated context
  -> repeat until complete or stopped
  -> inspect final output
  -> return response and record telemetry
```

Possible end states include successful completion, blocked content, tool failure, timeout, cancellation, exceeded limits, refusal, or human escalation.

## 23. Versions, sessions, and runs

- **Agent definition/version:** durable configuration containing model, instructions, tools, and policy references.
- **Session/conversation:** persistent context connecting multiple user turns (the agent's **memory**).
- **Run/response:** one execution in a session, potentially containing several model and tool steps.
- **Trace:** observability record of calls, timings, dependencies, and errors.

The definition provides behaviour, the session provides continuity, and the run performs the current task.

## 24. Tools and knowledge integration

Agents become useful by calling **tools** and **knowledge**:

- **Function calling / custom functions:** the model proposes a call with arguments against a **tool schema**; your app executes it and returns the result. Give the model precise schemas.
- **Knowledge stores / search:** connect Azure AI Search or **Foundry IQ** (Part XIII) so the agent can retrieve and ground answers.
- **Content Understanding / Document Intelligence:** let the agent extract from documents and images.
- **MCP (Model Context Protocol) tools:** connect external tool servers (e.g. a knowledge base exposed as `knowledge_base_retrieve`) with `require_approval` and `allowed_tools` controls.
- **APIs / OpenAPI tools:** call external services.

Apply **least privilege**: connect only the tools required, and guard consequential ones with schemas, validation, approvals, and limits (Part VII).

## 24a. Tool choice: `auto` vs `required` vs `none`

`tool_choice` controls **whether the model may, must, or can't call a tool** on a turn.

| Value | Meaning | Use when |
|---|---|---|
| **`auto`** (default) | Model decides whether to call a tool or answer directly. | Normal behaviour — tools used only when helpful. |
| **`required`** | Model **must** call a tool (at least one) before answering. | The answer must **always** come from a tool/knowledge source. |
| **`none`** | Model **may not** call any tool; answers from the model only. | Force a plain completion / disable tools this turn. |

**Exam clues → `required`:** "must **always** search", "must **always** retrieve", "must **always** provide citations", "must **always** use the knowledge source", "every answer must be grounded in the tool". Any **always / every** + tool/search/citation → **`required`**.

**Clues → `none`:** "do **not** use tools", "answer without calling functions". **Clues → `auto`:** "use the tool **when needed / if relevant**".

**Distractors:** writing "always search" in the **instructions** does **not** guarantee a tool call — only `tool_choice="required"` enforces it. Don't confuse with `require_approval` (that gates **execution**, not whether the model calls the tool).

## 24b. File Search vs Azure AI Search

Both retrieve content, but they target different scales:

| Clue in the scenario | Use |
|---|---|
| Files **uploaded into the conversation/agent**, ad-hoc documents, "attach these files", a small set | **File Search** (the agent's built-in file tool) |
| **Enterprise/organisational document collection**, indexed corpus, millions of docs, reused across apps, needs vector/semantic/hybrid + filters | **Azure AI Search** (§58) |

**Decision rules:**

- "user **uploads** a few files to ask about" / "files added to the agent" → **File Search**.
- "search our **knowledge base / document library / indexed collection**" → **Azure AI Search**.

**Trap:** don't reach for Azure AI Search just because the word "search" appears. Uploaded, conversation-scoped files are **File Search**; a managed, pre-indexed enterprise corpus is **Azure AI Search**.

## 24c. Connections: how tools get credentials

A **Connection** is a stored, reusable link to an external resource (Azure AI Search, Storage, an API, another AI service) **that holds the credentials** (key, managed identity, or token config) in the Foundry project — not in your code.

```text
Connection (stores credentials)  ->  Tool (references the connection)  ->  Agent (uses the tool)
```

- **Credentials live in the Connection**, centrally managed and reusable across tools/agents.
- A **Tool** consumes a Connection to reach its backend; the **Agent** calls the Tool.
- At runtime the tool authenticates **via the connection** — you never paste keys into the agent or the request.

**Exam clues → "the tool isn't linked to the connection":**

- "the **API key already exists** / the **connection is already configured**, but the tool still fails to authenticate" → the **tool is not wired to the connection** (fix: attach the connection to the tool) — **not** "add another key".
- "**authentication header missing**" while a valid connection exists → the tool isn't using the connection.

**Trap:** the fix is rarely "hardcode the key" — if a connection exists, **associate the tool with that connection**.

## 24d. OpenAPI tool authentication (`securitySchemes`)

When you add a REST API as an **OpenAPI tool**, auth is declared in the spec's **`securitySchemes`** and supplied through a **connection** — never hardcoded.

| `securityScheme` type | Use when the API expects… |
|---|---|
| **`apiKey`** | A key in a **header** (or query/cookie), e.g. `Ocp-Apim-Subscription-Key: <key>`. |
| **`http` (bearer)** | A **Bearer token** in the `Authorization` header. |
| **`oauth2`** | A full **OAuth 2.0** flow (token obtained from an identity provider, scopes). |

**Decision rules:**

- "API expects an **API key in a header**" → **`apiKey`** scheme (key stored in a connection).
- "API uses **OAuth 2.0 / token endpoint / scopes**" → **`oauth2`**.
- "API expects a **Bearer token**" → **`http` bearer**.

**Traps:** do **not** embed the secret in the spec, hardcode the header value, or inject the key via the prompt/instructions. The secret lives in a **connection**; the scheme only tells the tool **where** to put it.

## 25. Multi-agent orchestration and A2A

For complex work, split responsibilities across **multiple agents** (e.g. a planner/orchestrator that calls specialist agents). Patterns include sequential hand-off, routing, and parallel fan-out/fan-in, with **safeguards and approval flow controls** between steps.

**Agent-to-Agent (A2A)** is an open protocol that lets one agent discover and call another over HTTP. A Foundry agent is wrapped in an A2A **server** so other agents/clients can invoke it in a standard way.

| Part | Type / class | Role |
|---|---|---|
| **Skill** | `AgentSkill` | A single capability the agent advertises: `id`, `name`, `description`, `tags`, `examples`. A **description** of what it can do, not the implementation. |
| **Agent Card** | `AgentCard` | The agent's public "business card" at a well-known URL: `name`, `url`, `version`, input/output modes, `capabilities` (e.g. streaming), and the `skills`. Others **read the card to discover** it. |
| **Executor** | `AgentExecutor` subclass | The **implementation**. `execute(context, event_queue)` reads input, calls the underlying Foundry agent, and streams results back as events. Also implements `cancel(...)`. |
| **Request Handler** | `DefaultRequestHandler` | The **wiring** between protocol and executor. Takes the `agent_executor` plus a `task_store` and manages the task lifecycle. |
| **Server** | `A2AStarletteApplication` + `uvicorn` | The **HTTP app**. Combines the `agent_card` and the request handler and serves them. |

```text
Caller reads the Agent Card (discovery)
  -> HTTP request hits the A2A server
  -> Request Handler creates/tracks a Task
  -> Executor.execute(context, event_queue)
        - context.get_user_input()
        - invoke underlying Foundry agent  # responses.create stream
        - enqueue TaskArtifactUpdateEvent  # stream chunks back
  -> Handler emits TaskStatusUpdateEvent(state=completed, final=True)
  -> Response streamed to the caller
```

- **Agent Card = discovery/metadata; Executor = behaviour.** A **skill** is declarative (advertised); the **executor** implements it.
- The request handler needs a **task store** because A2A models work as **tasks** with lifecycle states and streamed artifacts/status events.
- `capabilities=AgentCapabilities(streaming=True)` tells callers the agent can stream; the executor then yields `TaskArtifactUpdateEvent`s.

---

# Part VII: Responsible AI, guardrails, evaluations, and red teaming

Responsible AI (RAI) is the governance layer *around* the whole system. **Guardrails** (runtime blocking), **evaluations** (measuring behaviour), and **red teaming** (attack testing) are concrete tools that implement RAI principles — they are *not* the same as RAI itself.

## 26. The six Responsible AI principles

| Principle | In plain words | Where it shows up in Foundry |
|---|---|---|
| **Fairness** | Treat people equitably; avoid biased or discriminatory outcomes. | `Hate and Unfairness` evaluator; custom decision-fairness tests (§35). |
| **Reliability & Safety** | Behave as intended, even on edge/adversarial input; fail safely. | Guardrails, content filters, Prompt Shields, evaluations, tracing. |
| **Privacy & Security** | Protect personal and sensitive data; secure the system. | PII controls, data-residency via deployment type (Part II), least-privilege identity (Part III). |
| **Inclusiveness** | Work for people of all abilities and backgrounds. | Accessibility review, diverse test data, multilingual/edge-case evaluation. |
| **Transparency** | People can understand how and why the system behaves. | Tracing/observability, model cards, documented limitations, disclosure to users. |
| **Accountability** | Humans remain responsible; there is oversight and recourse. | Human-in-the-loop approvals, audit logs, impact assessments, rollback paths. |

```text
Responsible AI principles (why + governance)
  -> Impact assessment            (identify harms before building)
  -> Guardrails / Content Safety  (block harm at runtime)        <- §27–32
  -> Evaluations                  (measure harm/quality)         <- §33–38
  -> Red teaming                  (attack-test the defences)     <- §39
  -> Deterministic controls       (limits, approvals, schemas)   <- §31
  -> Monitoring + audit           (detect drift, keep records)   <- §16
```

- The RAI framework lists **six principles**; **Transparency** and **Accountability** are "overarching" and apply to all the others.
- **Content Safety** is the classifier service behind many guardrails and safety evaluators — a *tool*, not the whole of RAI.
- A **Responsible AI Impact Assessment** is done **before** development to identify intended uses, stakeholders, and potential harms.
- RAI is **not** solved by the model's built-in alignment alone; it needs system-level design, testing, and operations.

## 27. What is a guardrail?

A **guardrail** is a named collection of **controls**. Each control defines:

1. a **risk** to detect;
2. one or more **intervention points** to inspect;
3. the **action** taken when the risk is detected.

Guardrails use safety classifiers, including Azure AI Content Safety capabilities. They are an extra runtime layer around the workload. They do not retrain the model and are not the same as system instructions or the model's built-in alignment.

## 28. Model guardrails versus agent guardrails

**Model guardrails** have two relevant intervention points:

- **User input:** the prompt before inference.
- **Output:** the model completion before it is returned.

**Agent guardrails** can have up to four:

- **User input:** the request before agent processing.
- **Tool call:** the action/data the agent proposes to send to a tool. Agent-only, preview.
- **Tool response:** content returned by a tool before the agent uses it. Agent-only, preview.
- **Output:** the final answer before it reaches the user.

Tool-call and tool-response moderation depends on support in the relevant agent and tool path. Do not assume every custom tool is automatically covered.

## 29. Default behaviour

- **Model deployments** are assigned **Microsoft.DefaultV2** by default — baseline filtering on supported inputs and outputs.
- **Foundry agents** depend on type/config: with inheritance, an agent without its own policy uses the model deployment's guardrail; a custom agent policy **overrides** the model policy for the agent flow; a **hosted agent** has an optional `rai_config` — omitting it means **no platform content-safety guardrail**, while `rai_config` present with no policy name applies `Microsoft.DefaultV2`.

> So "all agents use DefaultV2 by default" is too broad. Always check the agent type and attached RAI policy.

## 30. What happens with custom guardrails?

- **Custom on model, none on agent:** inheriting agent types follow the model policy for input/output; tool-call/response protection exists only where supported.
- **Custom on both:** the **agent policy overrides the model policy for the agent flow** — policies are **not merged**. A stricter model policy does not fill gaps in a weaker agent policy.
- **Default model + custom agent:** the agent policy governs the agent flow; it must explicitly contain every required risk and intervention point.
- **Direct model calls outside the agent:** still use the model deployment's guardrail; an agent policy does not protect unrelated direct calls.

**Practical rule:** treat model and agent entry points as separate attack surfaces — configure the model for direct use, configure the agent for prompts/tool calls/tool responses/final answers, test both paths, and never assume the policies are merged.

## 31. Annotate versus block

| Action | Models | Agents (Preview) |
|---|---:|---:|
| Annotate | ✅ | ❌ |
| Annotate and block | ✅ | ✅ |

- **Annotate** detects and labels a risk but lets content continue; the app inspects/logs the safety metadata and decides. Model-only as a standalone action.
- **Annotate and block** records the detection and **stops the flow** at that intervention point (input blocked before reaching the model/agent; model output blocked; tool call not executed; unsafe tool response not passed on; agent output not delivered).

**Why agents need more than content filters:** an agent can affect external systems. For consequential tools, combine guardrails with **deterministic controls** — allow-listed tools/destinations, strict schemas and business validation, least-privilege identity, human confirmation before high-impact actions, transaction limits and idempotency, and audit logs/traces/rollback. A probabilistic classifier should not be the only authorisation boundary around an action.

## 32. Common guardrail controls

- hate/unfairness, violence, sexual, and self-harm content filters;
- **Prompt Shields** for direct and indirect prompt attacks;
- protected-material detection;
- custom blocklists;
- groundedness-related checks where supported;
- PII or sensitive-information controls where supported;
- network-egress controls for hosted agents (preview).

Availability varies by model, region, agent type, and preview status.

## 33. What an evaluator measures

An evaluator scores one dimension of quality, safety, retrieval, or agent behaviour. Some are deterministic; others use an **LLM-as-judge** or Azure AI Content Safety. Use several metrics because one score cannot represent overall correctness, usefulness, and safety.

### General quality evaluators

**Coherence** and **Fluency** check the writing itself (no reference needed):

| Evaluator | In plain words |
|---|---|
| **Coherence** | Does the answer make sense and flow logically, without contradicting itself? |
| **Fluency** | Is the language smooth and natural (grammar, wording)? |

**Similarity, F1, BLEU/GLEU, ROUGE, METEOR** all compare the answer to a **reference answer** — they just match differently. Running example reference: **"The cat sat on the mat."**

| Evaluator | What it looks at | On the example |
|---|---|---|
| **Similarity** | **Meaning**, not exact words (AI judge). | "A feline rested on the rug" → same meaning → **high**. |
| **F1** | **Single words** that match, without junk. | "The cat sat on the big red soft mat indoors" → extra words → **lower**. |
| **BLEU / GLEU** | **Short phrases in order.** Common for **translation**. | "on the mat" in order scores; "mat the on" less. |
| **ROUGE** | **Coverage** of the reference's content. Common for **summaries**. | Did the summary include the key points? |
| **METEOR** | Same idea, **most forgiving** — accepts **synonyms**/order. | "big" vs "large" → still counts. |

**Takeaway:** Similarity = meaning; the other four = word matching against a reference, from strict (F1, BLEU) to generous (METEOR).

## 34. RAG and grounding evaluators

**What is RAG?** The system **searches for documents**, then the model **answers using them**. Two things to check: did it **find the right documents**, and did it **use them properly**? (Like an open-book exam: pick the right page, then answer from it.)

**Did it find the right documents?**

| Evaluator | In plain words |
|---|---|
| **Retrieval** | Did the search bring back useful, relevant documents (best ones near the top)? |
| **Document Retrieval** | Same, but scored against a known list of correct documents (a facit). |

**Did it answer properly from them?**

| Evaluator | In plain words |
|---|---|
| **Groundedness** | Is the answer backed up by the documents it was given? Scored **1–5** by a judge model. |
| **Groundedness Pro** | Same, but **pass/fail** (uses Content Safety, no judge model). Preview. |
| **Relevance** | Does the answer actually address the question? |
| **Response Completeness** | Did it include all important points? Preview. |

Three different questions people mix up:

- **Groundedness** → "Is it supported by *these documents*?"
- **Relevance** → "Does it answer *the question*?"
- **Correctness** → "Is it *actually true* in the real world?"

> Key point: **Groundedness only checks "does the document support this?" — not whether the document itself is right.**

### RAG vs multimodal RAG

- **RAG:** retrieve relevant **text** (usually via Azure AI Search), feed it to the model so the answer is grounded. Text in, text out.
- **Multimodal RAG:** grounding content also includes **images, charts, diagrams, scanned pages, tables, video/audio frames**, using **multimodal embeddings** + parsing services (**Document Intelligence / Content Understanding**) and a multimodal model (e.g. GPT-4o).

> One line: **RAG grounds on text; multimodal RAG grounds on text + images/visual content.**

## 35. Fairness and safety evaluators

Foundry represents fairness-related generative-AI evaluation through **Hate and Unfairness**, not one universal fairness score.

| Evaluator | Short explanation |
|---|---|
| **Hate and Unfairness** | Hateful, discriminatory, biased, or unfair content involving protected/vulnerable groups. |
| **Violence** | Violent content and severity. |
| **Sexual** | Sexual content and severity. |
| **Self-harm** | Self-harm content and severity. |
| **Protected Material** | Possible reproduction of protected text or code. |
| **Indirect Attack / Prompt Injection** | Untrusted retrieved content trying to manipulate the model/agent. |
| **Code Vulnerability** | Insecure patterns in generated code where available. |

**Fairness caveat:** `Hate and Unfairness` checks harmful content; it is **not** a complete fairness test for a business decision. For loans, hiring, benefits, or prioritisation, build domain-specific evaluations comparing outcomes and error rates across groups, with responsible-AI and legal review.

## 36. Agent-specific evaluators

**End-to-end / system:**

| Evaluator | What it measures |
|---|---|
| **Task Completion** | Did the agent complete the task with a usable result? |
| **Task Adherence** | Did it follow instructions, rules, and constraints? |
| **Intent Resolution** | Did it understand and address user intent? |
| **Task Navigation Efficiency** | Did it follow an expected/efficient step sequence (vs ground truth)? |
| **Customer Satisfaction** | Helpfulness, completeness, clarity, tone, resolution, adaptability. |
| **Rubric-based evaluation** | Custom criteria from the agent's role and expected behaviour. |

**Process / tool-use:**

| Evaluator | What it measures |
|---|---|
| **Tool Call Accuracy** | Correct tools, parameters, efficient sequence. |
| **Tool Selection** | Necessary tools selected, unnecessary avoided. |
| **Tool Input Accuracy** | Correct values, types, formats, required fields. |
| **Tool Output Utilisation** | Tool results used correctly in reasoning/answer. |
| **Tool Call Success** | Calls completed without errors/timeouts. |

Some agent evaluators are preview — verify support before using them as production gates.

## 37. Evaluations across the lifecycle

- **Before deployment:** build representative datasets (happy paths, edge cases, adversarial prompts, tool failures, missing data, ambiguity); set a baseline and metric thresholds; compare model/prompt/retrieval/tool/guardrail variants.
- **During CI/CD:** re-run a stable regression suite after material changes; block promotion on failed mandatory gates; version agent, dataset, evaluator, judge model, and threshold.
- **In production:** sample conversations/traces with privacy controls; monitor operational and quality/safety metrics; investigate changes in groundedness, task adherence, tool success, and harmful-content rates; re-evaluate after changes.

## 38. Guardrails are not evaluations

| Guardrails | Evaluations |
|---|---|
| Run in the live request/agent path | Run against datasets, traces, simulations, or production samples |
| Intervene immediately | Measure behaviour and produce scores/results |
| Can block content or actions | Do not normally stop a live request by themselves |
| Protect runtime interactions | Help decide readiness and detect regression |

Evaluation thresholds can become CI/CD release gates, but automation must enforce the gate.

## 39. Red teaming

**Red teaming = you attack your own AI on purpose** to find safety problems **before** real users or attackers do — like a fire drill. It is *testing*, not a live block.

Foundry's **AI Red Teaming Agent** automates it, built on **PyRIT** (Python Risk Identification Tool).

- **When:** before you deploy, and after big changes.
- **What it does:** sends lots of "bad" prompts to your target, then uses Content Safety to grade whether the answer was harmful.
- **Target:** a deployed model, a function, or an agent.

**Filters it tests** (the same content-safety categories as guardrails): **Hate & unfairness, Violence, Sexual, Self-harm**. A separate filter, **Prompt Shields**, catches *jailbreak* / prompt-injection attempts.

**Attack difficulty:** it asks the bad question plainly (**Baseline**), then **disguises** it at rising difficulty (**Easy → Moderate → Difficult**) using:

| Technique | What it does | "hello" |
|---|---|---|
| **Base64** | Encodes text into a letters/numbers string. | `aGVsbG8=` |
| **Morse code** | Letters → dots/dashes. | `.... . .-.. .-.. ---` |
| **ROT13 / Caesar** | Shifts letters a fixed number of steps. | `uryyb` |
| **Character flip / swap** | Reverses/scrambles letters. | `olleh` |
| **Unicode / leetspeak** | Look-alike symbols/numbers. | `h3ll0` |
| **Jailbreak prompt** | *Talks the model out of its rules* (prompt injection → Prompt Shields). | — |

**Key metric — Attack Success Rate (ASR):** of all attacks, how many got a harmful answer through. **Lower = safer** (0% = nothing got past). Reported as a **scorecard** by filter and difficulty.

> Two families of disguise: **encode the words** (Base64, Morse, ROT13, flipping, leetspeak) vs **jailbreak** (argue the model out of its rules).

---

# Part VIII: Fine-tuning

Fine-tuning adapts a pretrained model to a specific task, domain, style, or behaviour using specialized training data. Reach for it after prompting and parameters (Part V) are not enough.

## 40. Supervised Fine-Tuning (SFT)

SFT trains a model on labelled examples in JSONL format. Each example contains a prompt and the desired assistant response, and can include a system message.

```text
System message + user prompt + desired response
```

**Best for:** specific formats/styles/tones; domain-specific behaviour; improving instruction following. Usually the recommended starting point when high-quality labelled examples are available.

## 41. Reinforcement Fine-Tuning (RFT)

The model generates responses and a grader scores them; training updates the model to produce higher-scoring responses. The grader can be an LLM, a rule-based evaluator, custom code, or a combination.

```text
Prompt -> model response -> grader score -> model improvement
```

**Best for:** complex reasoning/problem-solving; tasks with objective checks or clear scoring; cases where ideal labelled responses are hard to produce. Requires a **reliable grader** because the model optimizes what the grader rewards.

## 42. Direct Preference Optimization (DPO)

DPO trains with two responses to the same prompt: one preferred, one not.

```text
Prompt -> preferred response + non-preferred response
```

**Best for:** tasks without one correct answer; improving tone/style/helpfulness; preference data from reviews, comparisons, or logs. Can apply to a base model or an SFT-tuned model.

## 43. Function Calling Fine-Tuning (FFT)

FFT is supervised fine-tuning with tool-calling examples (tool definitions + expected calls/arguments).

```text
User prompt + tool definitions -> expected tool call and arguments
```

**Best for:** improving tool selection; more accurate/consistent function arguments; reducing long tool descriptions in every prompt. The app still executes the function.

## 44. Vision Fine-Tuning (VFT)

VFT extends supervised fine-tuning with image inputs (chat-completions format, images + prompts + desired responses).

```text
Image + user prompt -> desired assistant response
```

**Best for:** domain-specific image understanding; visual classification/inspection; consistent image-based decisions. Images via URL or base64 data URI. Check model/region support.

## 45. Quick comparison

| Method | Training signal | Best fit |
|---|---|---|
| **SFT** | Desired responses | Format, style, domain behaviour, instruction following |
| **RFT** | Grader scores | Reasoning and objectively measurable problem-solving |
| **DPO** | Preferred vs rejected responses | Subjective quality and preference alignment |
| **FFT** | Expected tool calls and arguments | Tool selection and function-call accuracy |
| **VFT** | Images with desired responses | Domain-specific visual understanding |

---

# Part IX: Computer vision

Covers the AI-103 computer-vision domain: generating and editing images/video, understanding visual content, and keeping visual content safe.

## 46. Image generation

- **Text-to-image:** a generation model (e.g. GPT-image / DALL·E family) produces an image from a **text prompt**; you can also provide **reference media** to steer style/content.
- **Generation controls:** size/aspect ratio, number of images (`n`), quality/style, and **transparency** (where supported) to produce images with alpha for compositing.
- Output is returned as image data (URL or base64) that you save or pass downstream.

## 47. Image editing (inpainting and masks)

- **Inpainting / mask-based edits:** supply the original image **plus a mask** marking the region to change; the model regenerates only the masked area from a prompt (replace an object, remove/clean up, extend a scene).
- **Prompt-driven modifications:** change style, lighting, or content via instructions while keeping the rest.
- Choose the right control for the job: full generation vs targeted mask edit vs prompt-only edit.

## 47a. Input fidelity (preserving the reference image)

When editing or generating from a **reference image**, `input_fidelity` controls how closely the output must match the original.

| Setting | Effect | Choose when |
|---|---|---|
| **High fidelity** | Preserve the reference's appearance, layout, faces, and design closely. | Output **must resemble** the original. |
| **Low fidelity** | Looser adherence; more creative freedom, cheaper/faster. | A loose reinterpretation is acceptable. |

**Exam clues → high `input_fidelity`:** "must **resemble** the original image", "**preserve** the design / appearance / branding", "stay **faithful to the reference**", "keep the product looking the same". Any *preserve / faithful / resemble* → **high fidelity**.

**Trap:** more prompt detail does **not** guarantee visual fidelity — when the requirement is *look like the reference*, set **`input_fidelity` high**.

## 48. Video generation and editing

- **Text-to-video:** a video-generation model (e.g. Sora family) produces a short clip from a **text prompt** and optional **reference media**.
- **Editing generated video:** apply platform workflows to trim, extend, or modify clips.
- Video generation is heavier/slower — generation typically runs **asynchronously** (submit a job, poll for the result).

## 49. Multimodal visual understanding

Use a **multimodal model** (e.g. GPT-4o) or vision services to interpret images/video:

- **Captioning:** produce **concise** or **detailed** captions for single or multiple images.
- **Visual question-answering:** answer questions **grounded in the visual evidence** of an image.
- **Alt-text & accessibility:** generate alt-text and extended descriptions aligned to accessibility guidelines.
- **Object/region detection:** identify objects, components, or regions within images or video.
- You pass images to the model by **URL or base64**, alongside the text prompt.

## 50. Content Understanding for vision

**Azure Content Understanding** (a Foundry Tool) extracts structured **visual characteristics** from images and video with a defined **analyzer** (a schema of the fields you want). It runs in two modes.

| | **Standard mode** (single-task) | **Pro mode** |
|---|---|---|
| **What it does** | One analyzer does a **single-pass** extraction of your schema's fields from **one input** file. | **Multi-step reasoning** that can combine **multiple input files** and **reference data/knowledge** in one analysis. |
| **Reasoning** | Direct field extraction, no cross-document inference. | Agentic, multi-step: reasons across inputs, links and **validates** against reference data, enriches results. |
| **Inputs** | A single document/image/video. | Several related inputs analysed together. |
| **Best for** | Straightforward, high-volume extraction (invoice fields, caption, classification). | Complex cases: compare/reconcile documents, cross-reference a knowledge source, decisions needing reasoning. |
| **Cost/latency** | Cheaper, faster. | Higher cost/latency for the extra reasoning. |

- **Video analysis:** process and interpret video **segments** in either mode.
- Both produce clean, structured output you can feed to agents and RAG.

> One line: **standard = one file, direct extraction; pro = multiple files + reference data with multi-step reasoning and validation.**

## 51. Responsible AI for visual content

- **Visual content filters:** classify and block unsafe or disallowed **images** (the content-safety categories applied to vision).
- **Indirect prompt injection via images:** detect/mitigate **text embedded inside an image** that tries to manipulate the model (a visual prompt-injection attack).
- **Visual policy rules:** apply **watermarks**, flag **prohibited symbols**, uphold **brand-usage** requirements, and detect potentially inappropriate content.

---

# Part X: Text analysis

Covers extracting meaning from text and translating it, using the **Language** service, **Translator**, or **LLM prompting** — whichever fits the task.

## 52. Language analysis

Two routes: purpose-built **Language service** capabilities, or **generative prompting** with an LLM (often returning **structured JSON**).

| Task | What it does |
|---|---|
| **Named Entity Recognition (NER)** | Find entities (people, places, organizations, dates, quantities). |
| **Key phrase extraction** | Pull out the main topics/phrases. |
| **Sentiment & opinion mining** | Classify positive/neutral/negative and **tone**; link opinions to targets. |
| **PII detection** | Find and redact personal/sensitive information. |
| **Summarization** | Extractive (pick key sentences) or abstractive (generate a summary). |
| **Language detection** | Identify the input language. |
| **Custom text classification / custom NER** | Train on your labels for domain categories/entities. |

- **Language service** = reliable, cheaper, trainable for well-defined tasks.
- **LLM prompting** = flexible; extract **entities, topics, summaries, and structured JSON** in one call, and customize for domain tasks (e.g. compliance summarization). Request **structured outputs** for machine-readable results.

## 53. Translation

- **Azure Translator** (a Foundry Tool): fast, scalable **text translation** across many languages, plus **transliteration** and **document translation**; supports custom/glossary terminology.
- **LLM-powered translation:** an LLM can translate with more context/tone control inside a generative flow.
- Choose **Translator** for high-volume, well-defined translation; an **LLM** when you need context-aware or integrated-into-a-prompt translation.

## 53a. Mixed-language content (split → translate → recombine)

When a single segment contains **more than one language**, translating the whole blob at once confuses language detection and lowers quality.

**Pattern:** **detect/split by language → translate each part independently → recombine** in order.

**Why it improves quality:** each part is translated with the **correct source language** and context, so the model/Translator doesn't mis-detect the dominant language or mangle the minority-language spans. It also lets you skip or preserve segments already in the target language.

**Exam clues:** "a single sentence/segment **mixes languages**", "document contains **multiple languages**", "quality drops on **mixed-language** input" → **split by language first, translate separately, then recombine**.

**Trap:** sending mixed-language text in one call and trusting auto-detect — detection picks one language and degrades the rest.

---

# Part XI: Speech

Speech lets agents listen and talk, and translate spoken language — the AI-103 speech skills.

## 54. Speech to text and text to speech

- **Speech-to-text (STT):** transcribe audio to text — real-time (streaming) or batch. The input side of a voice agent.
- **Text-to-speech (TTS):** synthesize natural speech from text, with selectable/neural voices and **SSML** for pronunciation, pace, and emphasis. The output side of a voice agent.
- Together they make **speech an agent modality**: user speaks → STT → agent reasons → TTS → agent speaks.

## 55. Custom speech, translation, and audio-native models

- **Custom speech models:** adapt STT to domain vocabulary, accents, or noisy conditions for better accuracy.
- **Speech translation:** translate spoken input into another language (speech-to-text or speech-to-speech), via the Speech service or LLM/Foundry Tools.
- **Audio-native multimodal models:** some multimodal models reason **directly over audio input** (no separate transcription step), enabling richer audio understanding.

---

# Part XII: Document extraction

Two Azure services turn documents (and, for Content Understanding, other modalities) into structured data. Both follow the **same async poller pattern** and offer **prebuilt** and **custom** options.

## 56. The two services and their analyzers

| Service | SDK / client | What it does | Modalities |
|---|---|---|---|
| **Document Intelligence** | `azure-ai-documentintelligence` → `DocumentIntelligenceClient` | OCR plus **structured field extraction** (key-value pairs, tables, selection marks). | Documents and images. |
| **Content Understanding** | `azure-ai-contentunderstanding` → `ContentUnderstandingClient` | Newer **multimodal** extraction/understanding; can generate fields with a backing model and **markdown/structured** output. | Documents, images, audio, video. |

**Prebuilt vs custom:**

- **Prebuilt = ready to use, no training.** Common ids: `prebuilt-read` (raw text/OCR), `prebuilt-layout` (text + **tables + structure**), `prebuilt-invoice`, `prebuilt-receipt`, `prebuilt-idDocument`, `prebuilt-businessCard`, `prebuilt-tax.*`. `prebuilt-read` → just words; `prebuilt-layout` → words **plus** structure; domain analyzers → **named fields** (total, vendor, date).
- **Custom = trained on your own labelled documents**, called by a custom id (Document Intelligence `model_id`; Content Understanding `analyzer_id`).

```python
# Document Intelligence
poller = client.begin_analyze_document(
    model_id="prebuilt-invoice",
    body=AnalyzeDocumentRequest(bytes_source=document_bytes),  # or url_source=
)

# Content Understanding
poller = client.begin_analyze(
    analyzer_id="prebuilt-read",
    inputs=[AnalysisInput(url=file_url)],  # or data=bytes, name=, mime_type=
)
```

## 57. The poller and the result

Both `begin_analyze_document` and `begin_analyze` are **long-running operations (LROs)**:

```text
begin_analyze(...)   # kicks off the job, returns immediately
      -> poller      # handle to the running operation
poller.result()      # BLOCKS until finished, returns the typed result
```

- **Document Intelligence** → `AnalyzeResult` with `result.documents` (`doc_type`, `confidence`, `fields` where each field has `type`, `content`/`value_string`, `confidence`).
- **Content Understanding** → `AnalysisResult` with extracted content/fields, usable for **clean, grounded representations** for agents and RAG.
- **Confidence scores** let you route low-confidence extractions to human review.

> Facts: **Prebuilt = no training; custom = trained on your documents.** `prebuilt-read` = OCR only; `prebuilt-layout` = adds tables/structure; domain analyzers = named fields. Analysis is **async** (poller → result). **Document Intelligence** is document/image focused; **Content Understanding** is **multimodal** and newer.

## 57a. Scanned PDFs: OCR + page-aware chunking for RAG

Scanned/image PDFs have **no selectable text**, so you must **OCR** first, then chunk for retrieval.

**Pipeline:** OCR (Document Intelligence `prebuilt-read` / `prebuilt-layout`) → preserve **tables/structure** → **page-aware chunking** → embed → index.

**Decision rules:**

- "**scanned** PDF / image-only / no extractable text" → **OCR first** (`prebuilt-read` for text, `prebuilt-layout` for **tables + structure**).
- "must cite the **page number** / show **page references** / keep **tables** intact" → **page-aware (page-level) chunking**.

**Why page-aware chunking?** Chunking by page keeps each chunk tied to a real **page number** (so answers can cite "see page 7"), avoids splitting **tables** across chunk boundaries, and preserves layout context — all of which improve grounded, citable answers.

**Trap:** feeding a scanned PDF straight into an embedder yields nothing useful — the text must be **OCR'd** before chunking/indexing.

---

# Part XIII: Azure AI Search and grounding

## 58. What it is and the purpose it serves

**Azure AI Search** is a **search-as-a-service**. You load your content once, and it serves fast queries — keyword, filtered, vector, and semantic. It is the **retrieval engine** behind most RAG systems: the "R" that finds the right documents before a model answers (§34).

```text
Your content (blobs, DBs, files)
   -> ingested + AI-enriched
   -> stored in a searchable INDEX
   -> apps/LLMs query it for relevant results
```

Purpose in one line: **make heterogeneous content searchable and retrievable**, so apps can find information and LLMs can be grounded on it.

## 59. The components

| Component | In plain words |
|---|---|
| **Data source** | Connection to where content lives (Blob Storage, SQL, Cosmos DB). |
| **Indexer** | The **crawler/automation**: pulls documents, runs the skillset, pushes results into the index — on a schedule or on demand. |
| **Skillset** | The **AI-enrichment pipeline** during indexing: OCR, key-phrase extraction, entity recognition, **sentiment**, image analysis, embeddings, and **custom skills**. |
| **Index** | The **searchable store + schema**: fields, their attributes, and the enriched documents you query. |

**Field attributes:** **searchable** (full-text), **retrievable** (returned), **filterable** (`$filter`), **sortable / facetable**.

```text
Data source -> Indexer -> Skillset (enrich) -> Index (query this)
```

## 60. Query types and the semantic reranker

- **Keyword (lexical)** matches the **actual words**; "car" won't find a doc that only says "automobile".
- **BM25** (Best Matching 25) is the default **keyword ranking** behind **`@search.score`** — scores on term frequency (diminishing), rarity across the index, and length normalisation. It understands **nothing about meaning**.
- **Semantic** ranks by **meaning/intent**: a language model re-ranks the top keyword results, so "cheap places to stay near the beach" can surface a hotel passage that never uses those words; also powers captions/answers.

| Query type | What it does |
|---|---|
| **Simple** (default) | Keyword search with light operators. Ranked by **BM25**. |
| **Full** (Lucene) | Full **Lucene syntax**: field-scoped (`title:"Dubai Brochure.pdf"`), wildcards (`hote*`), fuzzy (`Dubia~`), boolean. Still keyword/BM25. |
| **Semantic** | Re-ranks the top BM25 results by meaning; can return captions/answers. Needs a **semantic configuration**. |
| **Vector / hybrid** | Embeddings **similarity** search (meaning via vectors), optionally combined with keyword (hybrid) for best recall + precision. |

Filters (OData `$filter`) are **independent** of query type and work on `filterable` fields:

```python
results = search_client.search(
    search_text="travel",
    query_type="semantic",
    semantic_configuration_name=semantic_configuration_name,
    filter="sentiment eq 'positive' and locations/any(o: o eq 'London')",
)
```

**Semantic reranker score:** with `query_type="semantic"`, a second deep-learning reranker reorders results and returns **`@search.reranker_score`** on a **fixed 0–4 scale**. This differs from **`@search.score`** (BM25), which is **unbounded** and only comparable within one query's results.

## 61. Foundry IQ — RAG as a managed knowledge base

**Foundry IQ** is a managed **knowledge base** in Foundry that packages the whole RAG retrieval pipeline. It is **built on Azure AI Search** and turns retrieval + grounding into a single thing an agent can call.

```text
Knowledge sources (Blob, SharePoint, …)
   -> Foundry IQ knowledge base  (Azure AI Search: indexing, vector + semantic retrieval)
   -> exposed as an MCP tool  (knowledge_base_retrieve)
   -> Foundry agent calls it to ground answers with citations
```

- **It is AI Search underneath** — but you configure a **knowledge base** instead of hand-building indexer, skillset, index, and query code.
- **Multiple sources, one base:** **Blob Storage** (indexed) and **SharePoint** (connected as a **remote source** — retrieved **without re-indexing**, respecting **Microsoft Purview** governance).
- **Agentic retrieval:** plans/decomposes a complex question across sources, returning grounded passages **with source URLs**.
- **Consumed as a tool, not plumbing:** surfaced to the agent via an **MCP tool** (`knowledge_base_retrieve`).

> One line: **AI Search = the retrieval engine; Foundry IQ = a managed, multi-source RAG knowledge base built on it, handed to agents as an MCP tool.**

---

# Part XIV: High-value summary

## 62. Facts to remember

1. Choose the **smallest model that meets quality**; match **modality** to the task; prefer a **Foundry Tool** for well-defined tasks.
2. Deployment type combines **processing scope** (Global/Data Zone/geography) with **capacity/billing** (Standard/Provisioned/Batch). Start with **Global Standard**.
3. **Standard TPM** quota and **Provisioned PTU** quota are **separate buckets**; over-limit → **429**.
4. **Version upgrade policy:** `OnceNewDefaultVersionAvailable` (auto, default), `OnceCurrentVersionExpired`, `NoAutoUpgrade` (pinned). Auto-upgrade can change behaviour (re-evaluate); fine-tunes are pinned to their base.
5. Prefer **keyless (Entra ID) auth** with **managed identity** + `DefaultAzureCredential`; disable local auth; use **private endpoints** and **least-privilege RBAC**.
6. Monitor **operational** (latency, tokens, 429, errors) and **quality/safety** (groundedness, drift, safety events, index health).
7. `AIProjectClient` = **control plane**; `get_openai_client()` = **data plane** inference; `AzureOpenAI` = project-less direct inference.
8. `agents.create_version` **defines** an agent (durable); `responses.create` **runs** a turn; `conversations.create` **holds** state (memory); `chat.completions.create` is stateless (`.parse` = typed output).
9. Shape behaviour first with **prompting + parameters** (low `temperature` for factual, `max_tokens` for length/cost, structured outputs) before fine-tuning.
10. Agents add **tools, knowledge, memory, and autonomy**; guard consequential tools with schemas, approvals, and limits.
11. In **A2A**, the **Agent Card** (+ **Skills**) advertises/discovers; the **Executor** implements; the **Request Handler** + task store manage the task; the **Server** serves it over HTTP.
12. **RAI** has **six principles** (**Transparency** & **Accountability** overarching). Guardrails/evaluations/red teaming are *implementations* of RAI, not RAI itself.
13. Guardrail control = **risk + intervention point + action**. Models protect **input/output**; agents can also protect **tool calls/responses**.
14. **Annotate** labels and continues; **annotate and block** stops. Agent policies **override** (not merge with) model policies. Default model policy = **Microsoft.DefaultV2**; omitting hosted-agent `rai_config` = no platform guardrail.
15. **Groundedness** = supported by the supplied docs (not universal truth); **Relevance** = answers the question; **Correctness** = actually true.
16. Evaluate both the **final outcome** and the **tool-use process**; thresholds can gate CI/CD (automation must enforce).
17. **Red teaming** = proactive attack testing (**PyRIT**); probes the four safety filters at rising difficulty (Base64/Morse/ROT13/flip/leetspeak = encode; jailbreak = argue) and reports **Attack Success Rate (ASR)** — lower is safer.
18. Fine-tuning: **SFT** (desired responses), **RFT** (grader scores), **DPO** (preferred vs rejected), **FFT** (tool calls), **VFT** (images).
19. **Computer vision:** text-to-image/video generation; **mask-based inpainting** edits; multimodal **captioning/visual QA/alt-text/object detection**; Content Understanding **single-task vs pro**; visual safety filters, **image prompt-injection**, watermarks/brand rules.
20. **Text analysis:** NER, key phrases, **sentiment/tone**, PII, summarization, custom classification — via Language service or **LLM structured JSON**; **Translator** vs LLM translation.
21. **Speech:** **STT + TTS** make speech an agent modality; **custom speech**, **speech translation**, and **audio-native** multimodal models.
22. Document analysis is **async** (poller → result). **Prebuilt = no training; custom = trained.** `prebuilt-read` = OCR; `prebuilt-layout` = +tables/structure; domain analyzers = named fields. **Content Understanding** is multimodal and newer.
23. Azure AI Search: **Indexer** = ingestion, **Skillset** = enrichment, **Index** = what you query. Field needs **filterable**/`$filter`, **retrievable**/return, **searchable**/full-text. Query types: **simple/full/semantic/vector-hybrid**; semantic adds **`@search.reranker_score`** (0–4) vs unbounded BM25 **`@search.score`**.
24. **Foundry IQ** = a managed, multi-source **RAG knowledge base built on Azure AI Search**, connected to sources (Blob, SharePoint-as-remote-source) and handed to agents as an **MCP tool** (`knowledge_base_retrieve`).

## 63. Recommended study order

1. Foundations: model selection (LLM/SLM/multimodal/reasoning) and choosing the right Foundry capability.
2. Deployment types, quota (TPM vs PTU), and version upgrade policy.
3. Security & ops: keyless/managed-identity auth, private networking, RBAC, CI/CD, monitoring.
4. Foundry SDK clients: `AIProjectClient` vs `get_openai_client()` vs `AzureOpenAI`.
5. Inference APIs (responses/conversations/chat.completions/.parse/agents.create_version) and prompt engineering + parameters.
6. Agents: lifecycle, runtime loop, tools/knowledge/memory, multi-agent orchestration and A2A.
7. Responsible AI principles; guardrails and intervention points; annotate vs block; custom-policy scenarios.
8. Evaluations: quality, RAG/groundedness, fairness/safety, agent task & tool-use; across the lifecycle.
9. Red teaming: AI Red Teaming Agent (PyRIT), filters, attack techniques, ASR.
10. Fine-tuning: SFT, RFT, DPO, FFT, VFT.
11. Computer vision: image/video generation & editing, multimodal understanding, Content Understanding, visual RAI.
12. Text analysis & speech: Language service, Translator, STT/TTS, custom/translated speech.
13. Information extraction: Document Intelligence vs Content Understanding; Azure AI Search and Foundry IQ.

---

# Official sources

- [Guardrails and controls overview](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview)
- [Configure guardrails and controls](https://learn.microsoft.com/en-us/azure/foundry/guardrails/how-to-create-guardrails)
- [Add guardrails to a hosted agent](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/add-hosted-agent-guardrails)
- [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)
- [Agent development lifecycle](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/development-lifecycle)
- [Observability in generative AI](https://learn.microsoft.com/en-us/azure/foundry/concepts/observability)
- [Built-in evaluators reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
- [Evaluate AI agents](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent)
- [Run evaluations in the Foundry portal](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-generative-ai-app)
- [Deployment types for Microsoft Foundry Models](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types)
- [Supervised fine-tuning](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning)
- [Reinforcement fine-tuning](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/reinforcement-fine-tuning)
- [Direct Preference Optimization](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-direct-preference-optimization)
- [Function calling fine-tuning](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-functions)
- [Vision fine-tuning](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-vision)
- [Responsible AI principles (Microsoft)](https://www.microsoft.com/en-us/ai/responsible-ai)
- [Responsible use of AI overview](https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai)
- [Azure AI Content Safety overview](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview)
- [AIProjectClient (azure-ai-projects) reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
- [Get an OpenAI client from a Foundry project](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview)
- [Azure OpenAI with the OpenAI Python SDK](https://learn.microsoft.com/en-us/azure/ai-services/openai/supported-languages)
- [Responses API](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses)
- [Structured outputs (chat.completions parse)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/structured-outputs)
- [Agent-to-Agent (A2A) protocol](https://a2aproject.github.io/A2A/)
- [Document Intelligence overview](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview)
- [Document Intelligence prebuilt models](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/model-overview)
- [Azure AI Content Understanding overview](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/overview)
- [Long-running operations (poller pattern) in the Azure SDK](https://learn.microsoft.com/en-us/azure/developer/python/sdk/lro)
- [What is Azure AI Search?](https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search)
- [Indexers in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-indexer-overview)
- [Skillset concepts (AI enrichment)](https://learn.microsoft.com/en-us/azure/search/cognitive-search-working-with-skillsets)
- [Query types and composition](https://learn.microsoft.com/en-us/azure/search/search-query-overview)
- [Semantic ranking and reranker score](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview)
- [Exam AI-103 study guide](https://aka.ms/AI103-StudyGuide)
- [Authenticate to Azure AI services with Microsoft Entra ID](https://learn.microsoft.com/en-us/azure/ai-services/authentication)
- [Managed identities for Azure resources](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Azure RBAC for Azure AI services](https://learn.microsoft.com/en-us/azure/ai-services/security-controls-policy)
- [Configure private endpoints for Azure AI services](https://learn.microsoft.com/en-us/azure/ai-services/cognitive-services-virtual-networks)
- [How to generate images with Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/dall-e)
- [Azure AI Content Understanding overview](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/overview)
- [Azure AI Vision Image Analysis](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/overview-image-analysis)
- [Azure AI Language service overview](https://learn.microsoft.com/en-us/azure/ai-services/language-service/overview)
- [Azure AI Translator overview](https://learn.microsoft.com/en-us/azure/ai-services/translator/translator-overview)
- [Azure AI Speech service overview](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/overview)