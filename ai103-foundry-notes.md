# Microsoft Foundry Study Guide: Guardrails, Agents, Evaluations, Model Deployments, and Fine-Tuning

_Last updated: 20 October 2026_

> This guide uses the current **Microsoft Foundry** terminology. Some older material still says **Azure AI Foundry**.

## 1. The big picture

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

A **model** generates a response. An **agent** wraps a model with instructions, conversation state, knowledge, tools, orchestration, identity, and monitoring. Agent safety must therefore cover not only prompts and answers, but also proposed tool calls and returned tool data.

---

# Part I: Guardrails

## 2. What is a guardrail?

A **guardrail** is a named collection of **controls**. Each control defines:

1. a **risk** to detect;
2. one or more **intervention points** to inspect;
3. the **action** taken when the risk is detected.

Guardrails use safety classifiers, including Azure AI Content Safety capabilities. They are an extra runtime layer around the workload. They do not retrain the model and are not the same as system instructions or the model's built-in alignment.

## 3. Model guardrails versus agent guardrails

### Model guardrails

A model deployment normally has two relevant intervention points:

- **User input:** the prompt before inference.
- **Output:** the model completion before it is returned.

### Agent guardrails

An agent can have up to four intervention points:

- **User input:** the request before agent processing.
- **Tool call:** the action and data the agent proposes to send to a tool. Agent-only and currently preview.
- **Tool response:** content returned by a tool before the agent uses it. Agent-only and currently preview.
- **Output:** the final answer before it reaches the user.

Tool-call and tool-response moderation depends on support in the relevant agent and tool path. Do not assume every custom tool is automatically covered.

## 4. Default behaviour

### Default for a model deployment

Foundry model deployments are assigned **Microsoft.DefaultV2** by default. This provides baseline filtering on supported model inputs and outputs.

### Default for a Foundry agent

The exact default depends on the agent type and configuration:

- For agents covered by Agent Service guardrail inheritance, an agent without its own custom guardrail uses the underlying model deployment's guardrail.
- If the agent has a custom guardrail, that agent policy governs risk detection in the agent flow and overrides the model policy for that flow.
- A **hosted agent** has an optional `rai_config`. Microsoft documents that omitting it means the hosted agent runs without a platform content-safety guardrail. If `rai_config` exists but no policy name is supplied, `Microsoft.DefaultV2` is applied.

So, “all agents use DefaultV2 by default” is too broad. Always check the agent type and attached RAI policy.

## 5. What happens with custom guardrails?

### Scenario A: Custom policy on the model, no custom policy on the agent

For agent types that support inheritance, the agent inherits the model deployment's policy. Input and output filtering follows that policy. Tool-call and tool-response protection exists only where the policy and runtime support those intervention points.

### Scenario B: Custom policy on both model and agent

The **agent policy overrides the model policy for the agent flow**. The policies are not automatically merged.

A stricter model policy therefore does not automatically fill gaps in a weaker agent policy. If the agent policy omits a control or intervention point, that part of the flow might not be examined by the omitted control.

### Scenario C: Default model policy and custom agent policy

The custom agent policy governs the agent flow. It should explicitly contain every required risk and intervention point.

### Scenario D: Direct calls to the model outside the agent

Direct calls still use the guardrail attached to the model deployment. An agent-level policy does not automatically protect unrelated direct model calls.

### Practical rule

Treat model and agent entry points as separate attack surfaces:

- configure the model safely for direct use;
- configure the agent for prompts, tool calls, tool responses, and final answers;
- test both paths;
- never assume the policies are merged.

## 6. Annotate versus block

### Action applicability (models versus agents)

| Action | Models | Agents (Preview) |
|---|---:|---:|
| Annotate | ✅ | ❌ |
| Annotate and block | ✅ | ✅ |

Annotate is a model-only standalone action. Agents only support annotate and block.

### Annotate

**Annotate** detects and labels a risk but lets the content continue. The application can inspect or log the returned safety metadata and decide what to do.

- Supported for model flows.
- Not supported as a standalone agent-guardrail action in the current action-applicability documentation.
- Useful for monitoring and application-controlled handling.
- Unsafe content can continue unless application code acts on the annotation.

### Annotate and block

**Annotate and block** records the detection and stops the flow at that intervention point.

- **Input blocked:** the request does not reach the model or agent.
- **Model output blocked:** the generated completion is not normally returned.
- **Tool call blocked:** the proposed action is not executed.
- **Tool response blocked:** the unsafe or malicious tool result is not passed onward for normal agent use.
- **Agent output blocked:** the final answer is not normally delivered.

### Why agents need more than content filters

An agent can affect external systems. For consequential tools, combine guardrails with deterministic controls:

- allow-listed tools and destinations;
- strict schemas and business validation;
- least-privilege identity;
- human confirmation before high-impact actions;
- transaction limits and idempotency;
- audit logs, traces, and rollback paths.

A probabilistic content classifier should not be the only authorisation boundary around an action.

## 7. Common guardrail controls

Controls can include:

- hate/unfairness, violence, sexual, and self-harm content filters;
- Prompt Shields for direct and indirect prompt attacks;
- protected-material detection;
- custom blocklists;
- groundedness-related checks where supported;
- PII or sensitive-information controls where supported;
- network-egress controls for hosted agents, currently preview.

Availability varies by model, region, agent type, and preview status.

## 8. Guardrails are not evaluations

| Guardrails | Evaluations |
|---|---|
| Run in the live request or agent execution path | Run against datasets, traces, simulations, or production samples |
| Intervene immediately | Measure behaviour and produce scores/results |
| Can block content or actions | Do not normally stop a live request by themselves |
| Protect runtime interactions | Help decide readiness and detect regression |

Evaluation thresholds can become CI/CD release gates, but automation must enforce the gate.

---

# Part II: Agent lifecycle

## 9. Development and operational lifecycle

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

## 10. Runtime lifecycle of one agent request

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

## 11. Versions, sessions, and runs

- **Agent definition/version:** durable configuration containing model, instructions, tools, and policy references.
- **Session/conversation:** persistent context connecting multiple user turns.
- **Run/response:** one execution in a session, potentially containing several model and tool steps.
- **Trace:** observability record of calls, timings, dependencies, and errors.

The definition provides behaviour, the session provides continuity, and the run performs the current task.

---

# Part III: Evaluations

## 12. What an evaluator measures

An evaluator scores one dimension of quality, safety, retrieval, or agent behaviour. Some are deterministic; others use an LLM-as-judge or Azure AI Content Safety. Use several metrics because one score cannot represent overall correctness, usefulness, and safety.

## 13. General quality evaluators

**Coherence** and **Fluency** just check the writing itself (no reference needed):

| Evaluator | In plain words |
|---|---|
| **Coherence** | Does the answer make sense and flow logically, without contradicting itself? |
| **Fluency** | Is the language smooth and natural (grammar, wording)? |

### Similarity, F1, BLEU/GLEU, ROUGE, METEOR — one idea, five flavours

These all do **one thing**: compare the model's answer to a **reference answer** (a "correct" example you provide) and measure how much they match. They just match in different ways.

Running example — the reference answer is **"The cat sat on the mat."**

| Evaluator | What it looks at | On the example |
|---|---|---|
| **Similarity** | The **meaning**, not the exact words (uses AI to judge). | "A feline rested on the rug" → different words, same meaning → **high**. (Similar ≠ factually true, just close to the reference.) |
| **F1** | **Single words** that match — did you include the right words, without adding junk? | "The cat sat on the big red soft mat indoors" → right words present but lots of extra → **lower**. |
| **BLEU / GLEU** | **Short word-sequences (phrases) in order.** Common for **translation**. | "on the mat" in order scores; "mat the on" scores less. |
| **ROUGE** | **Coverage** — how much of the reference's content you captured. Common for **summaries**. | Did your summary include the key points from the source? |
| **METEOR** | Same idea but **most forgiving** — accepts **synonyms** and different word order. | reference "big", answer "large" → METEOR still counts it; the stricter ones would miss it. |

**Simplest takeaway:** Similarity = meaning. The other four = word matching against a reference, from strict (F1, BLEU) to generous (METEOR).

## 14. RAG and grounding evaluators

**First, what is RAG?** The system **searches for documents** and then the model **answers using them**. So there are two things to check: did it **find the right documents**, and did it **use them properly**?

Think of it like an open-book exam: first you pick the right page, then you answer from what's on it.

### Did it find the right documents? (the search step)

| Evaluator | In plain words |
|---|---|
| **Retrieval** | Did the search bring back useful, relevant documents (and put the best ones near the top)? |
| **Document Retrieval** | The same, but scored against a known list of "these are the correct documents" (a facit). |

### Did it answer properly from them? (the answer step)

| Evaluator | In plain words |
|---|---|
| **Groundedness** | Is the answer actually backed up by the documents it was given? Scored **1–5** by a judge model. |
| **Groundedness Pro** | Same question, but a simple **pass/fail** (uses Content Safety, no judge model needed). Preview. |
| **Relevance** | Does the answer actually address the question asked? |
| **Response Completeness** | Did the answer include all the important points, or leave something out? Preview. |

### The one distinction people mix up

Three different questions:

- **Groundedness** → "Is it supported by *these documents*?"
- **Relevance** → "Does it answer *the question*?"
- **Correctness** → "Is it *actually true* in the real world?"

They don't always agree. An answer can be:
- **relevant but ungrounded** (on-topic, but not backed by the documents),
- **grounded but incomplete** (true to the docs, but missing key points),
- **grounded in a wrong source** (faithfully repeats a document that happens to be incorrect).

> Key point: **Groundedness only checks "does the document support this?" — not whether the document itself is right.**

### RAG vs multimodal RAG

- **RAG (Retrieval-Augmented Generation):** retrieve relevant **text** (usually via Azure AI Search), feed it to the model so the answer is grounded in your documents. Text in, text out.
- **Multimodal RAG:** the grounding content isn't only text — it also includes **images, charts, diagrams, scanned pages, tables, video/audio frames**. It uses **multimodal embeddings** (image + text) and parsing services (**Document Intelligence / Content Understanding**) so the system can retrieve *and reason over visuals*, with a multimodal model (e.g. GPT-4o) producing the answer.

> One line: **RAG grounds on text; multimodal RAG grounds on text + images/visual content.**

## 15. Fairness and safety evaluators

Foundry commonly represents fairness-related generative-AI evaluation through **Hate and Unfairness**, rather than one universal fairness score.

| Evaluator | Short explanation |
|---|---|
| **Hate and Unfairness** | Detects hateful, discriminatory, biased, or unfair generated content involving protected or vulnerable groups. |
| **Violence** | Detects violent content and severity. |
| **Sexual** | Detects sexual content and severity. |
| **Self-harm** | Detects self-harm content and severity. |
| **Protected Material** | Detects possible reproduction of protected text or code. |
| **Indirect Attack / Prompt Injection** | Detects untrusted retrieved content attempting to manipulate the model or agent. |
| **Code Vulnerability** | Assesses generated code for insecure patterns where available. |

### Fairness caveat

`Hate and Unfairness` checks harmful generated content. It is not a complete fairness test for a business decision. For loans, hiring, benefits, or prioritisation, create domain-specific evaluations comparing outcomes and error rates across relevant groups, with responsible-AI and legal review.

## 16. Agent-specific evaluators

### End-to-end/system evaluation

| Evaluator | What it measures |
|---|---|
| **Task Completion** | Whether the agent completed the task and produced a usable result. |
| **Task Adherence** | Whether it followed instructions, rules, and constraints. |
| **Intent Resolution** | Whether it correctly understood and addressed user intent. |
| **Task Navigation Efficiency** | Whether it followed an expected or efficient step sequence, usually against ground truth. |
| **Customer Satisfaction** | Helpfulness, completeness, clarity, tone, resolution, and adaptability. |
| **Rubric-based evaluation** | Custom criteria derived from the agent's role and expected behaviour. |

Some agent evaluators are preview features. Verify support before using them as production gates.

### Process/tool-use evaluation

| Evaluator | What it measures |
|---|---|
| **Tool Call Accuracy** | Correct tools, parameters, and efficient call sequence. |
| **Tool Selection** | Necessary tools selected and unnecessary tools avoided. |
| **Tool Input Accuracy** | Correct values, types, formats, and required fields. |
| **Tool Output Utilisation** | Tool results used correctly in the reasoning and answer. |
| **Tool Call Success** | Calls completed without errors or timeouts. |

## 17. Evaluations across the lifecycle

### Before deployment

- Build representative datasets.
- Include happy paths, edge cases, adversarial prompts, tool failures, missing data, and ambiguity.
- Establish a baseline and metric-specific thresholds.
- Compare model, prompt, retrieval, tool, and guardrail variants.

### During CI/CD

- Re-run a stable regression suite after material changes.
- Prevent promotion when mandatory quality or safety gates fail.
- Version the agent, dataset, evaluator, judge model, and threshold.

### In production

- Sample conversations and traces with appropriate privacy controls.
- Monitor operational and quality/safety metrics.
- Investigate changes in groundedness, task adherence, tool success, and harmful-content rates.
- Re-evaluate after changing the model, instructions, tools, data, retrieval, or guardrails.

---

# Part IV: Model deployment types

## 18. What deployment type controls

For serverless Microsoft Foundry model deployments, type determines:

- where inference data can be processed;
- usage-based versus reserved-capacity billing;
- throughput and latency characteristics;
- synchronous versus asynchronous processing.

Open-source and custom models on managed compute use a different deployment approach and do not use all these serverless SKUs.

## 19. Three independent dimensions

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

## 20. Deployment comparison

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

## 21. Simple selection guide

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

## 22. Key trade-offs

- **Global Standard:** broad capacity and early model availability, but global processing can violate residency requirements.
- **Data Zone Standard:** zone-level processing with usage billing, but availability and quota can differ.
- **Standard/geography:** geography-level processing, but new models and capacity can arrive later.
- **Provisioned:** predictable throughput, but requires capacity planning and commitment.
- **Batch:** lower-cost bulk processing, but asynchronous and unsuitable for interactive chat.
- **Developer:** useful for evaluation, but temporary and not for normal production.

## 22a. Standard (pay-as-you-go) and quota

With a **Standard** deployment you pay **per token** and share capacity with other customers. You don't reserve anything.

Your limit is a **TPM quota** (Tokens Per Minute), granted per **subscription + region + model**:

- It's a **ceiling** on how many tokens/min you may consume — not reserved capacity.
- Both input and output tokens count against it.
- Go over it → requests are **throttled (HTTP 429)**; wait and retry.
- Actual speed also depends on free shared capacity at that moment, so it can vary under load.

**Good for:** low, spiky, or unpredictable traffic — you only pay for what you use.

## 22b. Provisioned (PTU) and how it works

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

### Quota in one line

**Quota = your allowance (max you may deploy/consume). Standard TPM quota and Provisioned PTU quota are separate buckets.**

## 22c. Model version upgrade policy

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

# Part V: Fine-tuning

Fine-tuning adapts a pretrained model to a specific task, domain, style, or behaviour using specialized training data.

## 23. Supervised Fine-Tuning (SFT)

SFT trains a model on labelled examples in JSONL format. Each example contains a prompt and the desired assistant response, and can also include a system message.

```text
System message + user prompt + desired response
```

**Best suited for:**
- specific formats, styles, and tones;
- domain-specific behaviour;
- improving instruction following.

SFT is usually the recommended starting point when high-quality labelled examples are available.

## 24. Reinforcement Fine-Tuning (RFT)

In RFT, the model generates responses and a grader scores them. Training updates the model to produce responses that achieve higher scores.

The grader can be an LLM, a rule-based evaluator, custom code, or a combination of multiple graders.

```text
Prompt -> model response -> grader score -> model improvement
```

**Best suited for:**
- complex reasoning and problem-solving;
- tasks with objective checks or clear scoring criteria;
- cases where ideal labelled responses are difficult to produce.

RFT requires a reliable grader because the model learns to optimize what the grader rewards.

## 25. Direct Preference Optimization (DPO)

DPO trains a model with two responses to the same prompt: one preferred response and one non-preferred response.

```text
Prompt -> preferred response + non-preferred response
```

**Best suited for:**
- tasks without one clearly correct answer;
- improving tone, style, helpfulness, or response quality;
- preference data collected from reviews, comparisons, or logs.

DPO can be applied to a supported base model or an SFT-tuned model.

## 26. Function Calling Fine-Tuning (FFT)

FFT is supervised fine-tuning with tool-calling examples. Training data includes tool definitions and examples of the tool calls and arguments the model should produce.

```text
User prompt + tool definitions -> expected tool call and arguments
```

**Best suited for:**
- improving tool selection;
- producing more accurate and consistent function arguments;
- reducing reliance on long tool descriptions in every prompt.

The application still executes the function. Fine-tuning improves the model's ability to select and format the call.

## 27. Vision Fine-Tuning (VFT)

VFT extends supervised fine-tuning with image inputs. Training examples use the chat-completions format and include images with prompts and desired assistant responses.

```text
Image + user prompt -> desired assistant response
```

**Best suited for:**
- domain-specific image understanding;
- visual classification or inspection;
- consistent descriptions or decisions based on images.

Images can be referenced by accessible URLs or included as base64 data URIs. Model and region support must be checked before use.

## 28. Quick comparison

| Method | Training signal | Best fit |
|---|---|---|
| **SFT** | Desired responses | Format, style, domain behaviour, and instruction following |
| **RFT** | Grader scores | Reasoning and objectively measurable problem-solving |
| **DPO** | Preferred versus rejected responses | Subjective quality and preference alignment |
| **FFT** | Expected tool calls and arguments | Tool selection and function-call accuracy |
| **VFT** | Images with desired responses | Domain-specific visual understanding |

---

# Part VI: Responsible AI

## 29. The six Microsoft Responsible AI principles

Responsible AI (RAI) is the governance layer *around* everything else in this guide. Guardrails and evaluations are two concrete tools you use to satisfy it, but RAI is broader: it covers how you design, build, ship, and operate a system.

| Principle | In plain words | Where it shows up in Foundry |
|---|---|---|
| **Fairness** | Treat people equitably; avoid biased or discriminatory outcomes. | `Hate and Unfairness` evaluator; custom decision-fairness tests (§15). |
| **Reliability & Safety** | Behave as intended, even on edge/adversarial input; fail safely. | Guardrails, content filters, Prompt Shields, evaluations, tracing. |
| **Privacy & Security** | Protect personal and sensitive data; secure the system. | PII controls, data-residency via deployment type (§18–22), least-privilege identity. |
| **Inclusiveness** | Work for people of all abilities and backgrounds. | Accessibility review, diverse test data, multilingual/edge-case evaluation. |
| **Transparency** | People can understand how and why the system behaves. | Tracing/observability, model cards, documented limitations, disclosure to users. |
| **Accountability** | Humans remain responsible; there is oversight and recourse. | Human-in-the-loop approvals, audit logs, impact assessments, rollback paths. |

### How RAI connects to the rest of this guide

```text
Responsible AI principles (why + governance)
  -> Impact assessment            (identify harms before building)
  -> Guardrails / Content Safety  (block harm at runtime)        <- Part I
  -> Evaluations                  (measure harm/quality)         <- Part III
  -> Deterministic controls       (limits, approvals, schemas)   <- Section 6
  -> Monitoring + audit           (detect drift, keep records)   <- Sections 9, 17
```

### Exam-relevant facts

- Microsoft's RAI framework lists **six principles**; two of them (**Transparency**, **Accountability**) are "overarching" and apply to all the others.
- **Content Safety** is the classifier service behind many guardrails and safety evaluators; it is a *tool* that serves the Reliability & Safety and Fairness principles, not the whole of RAI.
- A **Responsible AI Impact Assessment** is done **before** development to identify intended uses, stakeholders, and potential harms.
- Guardrails ≠ RAI and evaluations ≠ RAI; they are **implementations** of RAI principles. Governance, documentation, and human accountability are also required.
- RAI is **not** solved by the model's built-in alignment alone; it needs system-level design, testing, and operations.

---

# Part VII: Foundry SDK clients — which client does what

Three clients get confused: `AIProjectClient`, `get_openai_client()`, and `AzureOpenAI`. The split is simple: **one manages the project, two run inference.**

## 30. The three clients

| Client | Plane | Use it to |
|---|---|---|
| **`AIProjectClient`** | Control (manage) | Manage project resources: `.agents`, `.connections`, datasets, indexes, evaluations, deployments. |
| **`project_client.get_openai_client()`** | Data (run) | Run inference **inside** a Foundry project — endpoint + auth already wired for you. |
| **`AzureOpenAI`** | Data (run) | Run inference against an Azure OpenAI endpoint **with no project** — you set `azure_endpoint`, `api_version`, and auth yourself. |

Imports: `from azure.ai.projects import AIProjectClient` · `from openai import AzureOpenAI`.

### Mental model

```text
AIProjectClient            # control plane: agents, connections, eval, data
   └── get_openai_client() # data plane: inference (OpenAI-compatible)
         ≈ AzureOpenAI     # same inference methods, but project-wired for you
```

- `AIProjectClient` is the **entry point**; `get_openai_client()` hands you a project-scoped OpenAI client, so you never hard-code the model endpoint or redo auth.
- `AzureOpenAI` is the same inference surface (`.responses`, `.chat.completions`, `.embeddings`, …) **without** the project layer — no `.agents`, no `.connections`.
- Plain **`OpenAI`** points at OpenAI.com, not Azure — not used for Foundry work.

### Which to pick

| Goal | Client |
|---|---|
| Create/version agents, manage connections, run evaluations | `AIProjectClient` |
| Run inference **inside** a Foundry project | `project_client.get_openai_client()` |
| Call an Azure OpenAI endpoint **with no project** | `AzureOpenAI` |

---

# Part VIII: Inference APIs — responses, conversations, chat.completions, agents.create_version

These four calls look similar but sit at different layers. Understanding how they **combine** is the point.

## 31. The four calls

| Call | Layer | What it does |
|---|---|---|
| **`chat.completions.create(...)`** | Stateless inference | The classic Chat Completions API. You send the full message list every time; the server keeps **no** state. `.parse(...)` is the structured-output variant that validates the reply against a schema/Pydantic model. |
| **`responses.create(...)`** | Stateless or stateful inference | The newer **Responses API**. Simpler input (`input=`, `instructions=`), supports tools, streaming, and can attach to a server-side `conversation`. Preferred for new Foundry work. |
| **`conversations.create(...)`** | Server-side state | Creates a **conversation object** that stores turn history on the server. You then pass its `id` to `responses.create(conversation=...)` instead of resending history. |
| **`agents.create_version(...)`** | Control plane (definition) | Creates/updates a **durable agent version** (model + instructions + tools + policy) via `AIProjectClient.agents`. It does **not** run inference — it defines the agent you later invoke. |

## 32. How they differ and combine

### chat.completions vs responses

- **chat.completions**: you manage history yourself (resend every message). `.parse` gives typed/structured output.
- **responses**: newer, cleaner input shape, native tools + streaming, and optional server-side conversation state. For Foundry, prefer **responses** unless you specifically need chat.completions compatibility.

### Where conversations fit

`conversations.create()` is **not** an inference call. It returns a state container. Combine it with responses:

```python
conversation = openai_client.conversations.create()
openai_client.responses.create(
    conversation=conversation.id,   # server remembers prior turns
    input=user_input,
    stream=True,
)
```

### Where agents.create_version fits

`agents.create_version` defines the agent once (control plane). You then **invoke** that agent through the data plane — `responses.create` with an `agent_reference` — optionally inside a conversation:

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

### One-line mental model

```text
agents.create_version   = define the agent      (control plane, durable)
conversations.create    = remember the session  (data plane, state)
responses.create        = run a turn            (data plane, execution)
chat.completions.create = run a stateless turn  (data plane, no server state)
       .parse           = same, but typed/structured output
```

- **Differ:** control plane (define) vs data plane (run); stateless vs stateful.
- **Combine:** `create_version` → (reference by) `responses.create` → (state from) `conversations.create`.

---

# Part IX: A2A anatomy

**Agent-to-Agent (A2A)** is an open protocol that lets one agent discover and call another over HTTP. A Foundry agent is wrapped in an A2A **server** so other agents (or clients) can invoke it in a standard way. The server in this repo (`MicrosoftFoundry/A2A/A2A_Container_Apps/A2A_Server/`) shows every part.

## 33. The five building blocks

| Part | Type / class | Role |
|---|---|---|
| **Skill** | `AgentSkill` | A single capability the agent advertises: `id`, `name`, `description`, `tags`, `examples`. One agent can list several skills. It's a **description** of what the agent can do, not the implementation. |
| **Agent Card** | `AgentCard` | The agent's public "business card" at a well-known URL. Holds `name`, `description`, `url`, `version`, input/output modes, `capabilities` (e.g. streaming), and the list of `skills`. Other agents **read the card to discover** this agent. |
| **Executor** | `AgentExecutor` subclass | The **implementation**. Its `execute(context, event_queue)` runs the actual work — reads the user input from `RequestContext`, calls the underlying Foundry agent, and streams results back as events. Must also implement `cancel(...)`. This is where skills become real behaviour. |
| **Request Handler** | `DefaultRequestHandler` | The **wiring** between the protocol and your executor. Takes the `agent_executor` plus a `task_store` (e.g. `InMemoryTaskStore`) and manages the task lifecycle (receive request → run executor → track task state). |
| **Server** | `A2AStarletteApplication` + `uvicorn` | The **HTTP app**. Combines the `agent_card` and the `http_handler` (the request handler), exposes the card and endpoints, and serves them (here on port 8080). |

### How a request flows

```text
Caller reads the Agent Card (discovery)
  -> HTTP request hits the A2A server (A2AStarletteApplication)
  -> Request Handler (DefaultRequestHandler) creates/tracks a Task
  -> Executor.execute(context, event_queue)
        - context.get_user_input()        # the query
        - invoke underlying Foundry agent # responses.create stream
        - enqueue TaskArtifactUpdateEvent # stream chunks back
  -> Handler emits TaskStatusUpdateEvent(state=completed, final=True)
  -> Response streamed to the caller
```

### Exam-relevant facts

- **Agent Card = discovery/metadata; Executor = behaviour.** Don't confuse "what it says it can do" (skill/card) with "what it actually does" (executor).
- A **skill** is declarative (advertised on the card); the **executor** is where that skill is implemented.
- The **request handler needs a task store** because A2A models work as **tasks** with lifecycle states (e.g. `completed`) and streamed artifacts/status events.
- `capabilities=AgentCapabilities(streaming=True)` on the card tells callers the agent can stream — the executor then yields `TaskArtifactUpdateEvent`s.
- The underlying Foundry agent is invoked inside `execute` using the data-plane pattern from Part VIII (`responses.create` with an `agent_reference` + a conversation).

---

# Part X: Document extraction — Document Intelligence and Content Understanding

Two Azure services turn documents (and, for Content Understanding, other modalities) into structured data. Both follow the **same async poller pattern** and both offer **prebuilt** and **custom** options.

## 34. The two services and their prebuilt analyzers

| Service | SDK / client | What it does | Modalities |
|---|---|---|---|
| **Document Intelligence** | `azure-ai-documentintelligence` → `DocumentIntelligenceClient` | OCR plus **structured field extraction** from documents (key-value pairs, tables, selection marks). | Documents and images. |
| **Content Understanding** | `azure-ai-contentunderstanding` → `ContentUnderstandingClient` | Newer **multimodal** extraction and understanding; can also generate fields with a backing model. | Documents, images, audio, and video. |

### Prebuilt vs custom

- **Prebuilt** = ready to use, **no training required**. You just pass the analyzer/model id.
  - Common ids: `prebuilt-read` (raw text/OCR), `prebuilt-layout` (text + **tables + structure**), `prebuilt-invoice`, `prebuilt-receipt`, `prebuilt-idDocument`, `prebuilt-businessCard`, `prebuilt-tax.*`.
  - `prebuilt-read` → just the words. `prebuilt-layout` → words **plus** document structure. Domain analyzers (`invoice`, `receipt`, …) → **named fields** like total, vendor, date.
- **Custom** = you **train on your own labelled documents** and call it by a custom id.
  - Document Intelligence: `model_id="doc-intel-custom"`.
  - Content Understanding: a custom `analyzer_id`.

### The two call shapes

```python
# Document Intelligence — begin_analyze_document(model_id=, body=AnalyzeDocumentRequest(...))
poller = client.begin_analyze_document(
    model_id="prebuilt-invoice",
    body=AnalyzeDocumentRequest(bytes_source=document_bytes),  # or url_source=
)

# Content Understanding — begin_analyze(analyzer_id=, inputs=[AnalysisInput(...)])
poller = client.begin_analyze(
    analyzer_id="prebuilt-read",
    inputs=[AnalysisInput(url=file_url)],  # or data=bytes, name=, mime_type=
)
```

## 35. The poller and the result

Both `begin_analyze_document` and `begin_analyze` are **long-running operations (LROs)**. They don't return the answer directly:

```text
begin_analyze(...)         # kicks off the job, returns immediately
      -> poller            # a handle to the running operation
poller.result()            # BLOCKS until finished, returns the typed result
```

- The **poller** lets you wait (`.result()`), or check status, without re-sending the request. It is Azure's standard async pattern for work that takes time.
- The **result** is a typed object:
  - Document Intelligence → `AnalyzeResult` with `result.documents`, each having `doc_type`, `confidence`, and `fields` (each field has `type`, `content`/`value_string`, and `confidence`).
  - Content Understanding → `AnalysisResult` with the extracted content/fields.
- **Confidence scores** on fields let you route low-confidence extractions to human review.

### Exam-relevant facts

- **Prebuilt = no training; custom = trained on your documents.** `prebuilt-read` = OCR only; `prebuilt-layout` = adds tables/structure; domain analyzers = named business fields.
- Analysis is **asynchronous**: `begin_*` returns a **poller**, `poller.result()` returns the typed **result**.
- **Document Intelligence** is document/image focused; **Content Understanding** is **multimodal** (also audio/video) and is the newer service.
- Fields carry **confidence** — use it for human-in-the-loop review thresholds.

---

# Part XI: Azure AI Search

## 36. What it is and the purpose it serves

**Azure AI Search** is a **search-as-a-service**. You load your content into it once, and it serves fast queries over that content — keyword, filtered, vector, and semantic. It is the **retrieval engine** behind most RAG systems: the "R" that finds the right documents before a model answers (see §14).

```text
Your content (blobs, DBs, files)
   -> ingested + AI-enriched
   -> stored in a searchable INDEX
   -> apps/LLMs query it for relevant results
```

Purpose in one line: **make heterogeneous content searchable and retrievable**, so apps can find information and LLMs can be grounded on it.

## 37. The components

| Component | In plain words |
|---|---|
| **Data source** | The connection to where your content lives (e.g. Blob Storage, SQL, Cosmos DB). |
| **Indexer** | The **crawler/automation**. It pulls documents from the data source, runs them through the skillset, and pushes the results into the index — on a schedule or on demand. |
| **Skillset** | The **AI-enrichment pipeline** applied *during indexing*: OCR, key-phrase extraction, entity recognition (persons/locations/organizations), **sentiment**, image analysis, embeddings, and **custom skills**. Turns raw content into extra searchable fields. |
| **Index** | The **searchable store + schema**. Defines fields and their attributes, and holds the enriched documents you actually query. |

### Field attributes (on the index)

Each field is configured with what it's allowed to do:

- **searchable** — can be full-text searched.
- **retrievable** — can be returned in results.
- **filterable** — can be used in `$filter` (e.g. `sentiment eq 'positive'`).
- **sortable / facetable** — can order results / power facet navigation.

```text
Data source -> Indexer -> Skillset (enrich) -> Index (query this)
```

## 38. Query types and the semantic reranker

### First: keyword vs semantic, and what BM25 is

- **Keyword search (lexical)** matches the **actual words** in the query against the words in the index. If the words don't overlap, it won't match — "car" will not find a document that only says "automobile".
- **BM25** (Best Matching 25) is the **ranking algorithm** that scores those keyword matches. It's the classic, maths-based formula behind the default **`@search.score`**. Roughly, a document scores higher when:
  - the query term appears **more often** in it (term frequency), but with **diminishing returns**;
  - the term is **rare across the whole index** (a distinctive word counts more than a common one);
  - the document is **not unusually long** (length normalisation stops long docs winning just by size).
  - BM25 understands **nothing about meaning** — only word statistics. It's fast and the default for simple/full queries.
- **Semantic** means ranking by **meaning/intent**, not exact words. Azure AI Search runs a **language model** over the top keyword results to understand what the query and passages *mean*, so "cheap places to stay near the beach" can surface a hotel passage that never uses those exact words. It also powers captions and extractive answers.

> **One-liner:** BM25 = keyword relevance by word statistics (the default `@search.score`). Semantic = a language model re-ranks for meaning (adds `@search.reranker_score`).

### The query types

Set with `query_type` on the search call (or `"queryType"` in the REST body).

| Query type | What it does |
|---|---|
| **Simple** (default) | Basic keyword search with light operators. Ranked by **BM25**. Good default. |
| **Full** (Lucene) | Full **Lucene syntax**: field-scoped (`title:"Dubai Brochure.pdf"`), wildcards (`hote*`), fuzzy (`Dubia~`), boolean. Still keyword/BM25, just richer syntax. |
| **Semantic** | Takes the top BM25 results and **re-ranks them by meaning** with a language model; can return captions/answers. Requires a **semantic configuration**. |
| **Vector / hybrid** | Embeddings **similarity** search (meaning via vectors), optionally combined with keyword (hybrid) for best recall + precision. |

Filters (OData `$filter`) are **independent** of query type — they work on `filterable` fields with any mode:

```python
results = search_client.search(
    search_text="travel",
    query_type="semantic",
    semantic_configuration_name=semantic_configuration_name,
    filter="sentiment eq 'positive' and locations/any(o: o eq 'London')",
)
```

### The semantic reranker score

When `query_type="semantic"`, a second **deep-learning reranker** reorders the first-stage results by semantic relevance to the query:

- It returns **`@search.reranker_score`**, on a **fixed 0–4 scale** (higher = more relevant).
- This is **different** from the default **`@search.score`** (BM25 keyword relevance), which is **not** 0–4: BM25 is an **unbounded** positive number (0 and up) that is only meaningful *relative to other results in the same query* — you can't compare it across queries.
- Two-stage model: keyword/vector retrieval finds candidates → semantic reranker reorders the top of that list.

```python
for result in results:
    print("Reranker score:", result['@search.reranker_score'])  # 0–4, semantic
```

### Exam-relevant facts

- **Indexer = ingestion automation; Skillset = AI enrichment; Index = what you query.** Don't mix them up.
- A field must be **filterable** to use it in `$filter`, **retrievable** to return it, **searchable** to full-text search it.
- **Simple vs Full**: Full enables Lucene syntax (fields, wildcards `*`, fuzzy `~`, boolean).
- **BM25** is the default **keyword** ranking algorithm (word statistics: term frequency + rarity + length), producing **`@search.score`**. It ignores meaning. The score is **unbounded** (not 0–4) and only comparable within one query's results.
- **Semantic** ranks by **meaning** with a language model; it needs a semantic configuration and adds **`@search.reranker_score`** on a **fixed 0–4 scale**, separate from the unbounded BM25 **`@search.score`**.
- AI Search is the **retrieval** layer for RAG; groundedness/retrieval evaluators (§14) measure how well that retrieval feeds the model.

---

# Part XII: Red teaming

**Red teaming = you attack your own AI on purpose** to find safety problems **before** real users or real attackers do. Think of it like a fire drill: you start a (safe) fire to check the alarms actually go off. It is *testing*, not a live block.

## 39. AI Red Teaming Agent

Foundry's **AI Red Teaming Agent** does the attacking for you automatically. Under the hood it uses **PyRIT** (Python Risk Identification Tool — Microsoft's free open-source red-teaming tool).

- **When to run it:** before you deploy, and again after big changes. It's a safety check, like evaluations.
- **What it does:** it sends lots of "bad" prompts to your AI, then uses Content Safety to grade whether the answer that came back was actually harmful.
- **What you can point it at:** a deployed model, a function, or an agent.

### The filters it tests (and what each one catches)

A **filter** is the AI's safety gate: it is meant to spot and stop harmful content. Red teaming checks whether each of these common filters actually holds up under attack:

| Filter (risk category) | What it is meant to catch |
|---|---|
| **Hate & unfairness** | Hateful, insulting, discriminatory, or biased content about people or groups (race, gender, religion, etc.). |
| **Violence** | Content that describes, threatens, or encourages physical harm, weapons, or gore. |
| **Sexual** | Explicit or inappropriate sexual content. |
| **Self-harm** | Content about hurting oneself or suicide, or encouraging it. |

These are the same four content-safety categories used by guardrails and the safety evaluators. A separate filter, **Prompt Shields**, catches *jailbreak* / prompt-injection attempts — tricks that try to make the AI ignore its own rules.

### How hard it tries (attack difficulty)

It first asks the bad question plainly, then **disguises** it so the filter might not recognise the harmful words. Harder levels use sneakier disguises.

| Level | What it means |
|---|---|
| **Baseline** | The plain harmful question, no tricks. |
| **Easy → Moderate → Difficult** | The same question hidden with one or more of the techniques below. More/stronger disguises = harder level. |

### The disguise techniques (attack strategies)

These are the tricks the agent uses to try to smuggle a harmful request past the filter. The idea is always the same: **the meaning stays harmful, but the surface text looks innocent**, so a filter that only scans for bad words might miss it.

| Technique | What it does | Tiny example of "hello" |
|---|---|---|
| **Base64** | Encodes the text into a letters/numbers string; the model can decode it but the filter sees gibberish. | `aGVsbG8=` |
| **Morse code** | Replaces letters with dots and dashes. | `.... . .-.. .-.. ---` |
| **ROT13 / Caesar** | Shifts every letter a fixed number of steps in the alphabet. | `uryyb` (shift 13) |
| **Character flip / swap** | Reverses or scrambles the letters. | `olleh` |
| **Unicode / leetspeak** | Swaps letters for look-alike symbols or numbers. | `h3ll0` |
| **Jailbreak prompt** | Doesn't encode text — instead *talks the model out of its rules* ("ignore your instructions", "pretend you are an AI with no limits", role-play tricks). This is the **prompt-injection** family that **Prompt Shields** is meant to stop. |

> **Key idea:** Base64, Morse, ROT13, flipping, leetspeak = **hide the words**. Jailbreak = **argue the model into breaking its rules**. Red teaming throws all of these at your AI to see which ones get through.

### The one score that matters — Attack Success Rate (ASR)

- ASR = **out of all the attacks, how many got a harmful answer through.**
- **Lower = safer.** (0% means nothing got past the filters.)
- You get it as a **scorecard**: broken down by filter (harm category) and by difficulty, so you can see *which* filter leaked and *how clever* the attack had to be.

### Exam-relevant facts

- Red teaming **finds** weaknesses (testing); **filters/guardrails block** them at runtime. Different jobs — don't mix them up.
- The filters tested are **hate & unfairness, violence, sexual, self-harm**; **Prompt Shields** handles jailbreak / prompt injection.
- The AI Red Teaming Agent runs on **PyRIT**.
- The key metric is **Attack Success Rate (ASR)** — **lower is better**.
- Two families of disguise: **encode the words** (Base64, Morse, ROT13, flipping, leetspeak) and **jailbreak** (argue the model out of its rules — the prompt-injection family **Prompt Shields** targets).

---

# Part XIII: High-value summary

## 40. Facts to remember

1. Guardrail control = **risk + intervention point + action**.
2. Models normally protect **input and output**.
3. Agents can additionally protect **tool calls and tool responses**.
4. **Annotate** labels and continues; **annotate and block** labels and stops.
5. Agent policies can **override**, rather than merge with, model policies.
6. The default model policy is **Microsoft.DefaultV2**.
7. Hosted agents need special attention: omitting `rai_config` can mean no platform content-safety policy.
8. Guardrails intervene at runtime; evaluations measure behaviour.
9. Groundedness measures support from supplied context, not universal truth.
10. Hate and Unfairness is the main built-in fairness-style content evaluator; decision fairness needs custom testing.
11. Evaluate both the final agent outcome and its tool-use process.
12. Deployment names combine **processing scope** with **capacity/billing**.
13. Start with Global Standard unless residency, reserved throughput, or batch processing requires another type.
14. Responsible AI has **six principles**; **Transparency** and **Accountability** are overarching. Guardrails and evaluations are *implementations* of RAI, not RAI itself.
15. `AIProjectClient` = **control plane** (agents, connections, eval); `get_openai_client()` = **data plane** inference; `AzureOpenAI` = project-less direct inference.
16. `agents.create_version` **defines** an agent (durable); `responses.create` **runs** a turn; `conversations.create` **holds** state; `chat.completions.create` is stateless (`.parse` = typed output).
17. In A2A, the **Agent Card** (with its **Skills**) advertises/discovers the agent; the **Executor** implements behaviour; the **Request Handler** + task store manage the task; the **Server** serves it over HTTP.
18. Document analysis is **async**: `begin_*` returns a **poller**, `poller.result()` returns the typed result. **Prebuilt** needs no training; **custom** is trained on your documents.
19. `prebuilt-read` = OCR text only; `prebuilt-layout` = adds tables/structure; domain analyzers (`invoice`, `receipt`) = named fields. **Content Understanding** is multimodal (adds audio/video); **Document Intelligence** is document/image focused.
20. In Azure AI Search: **Indexer** = ingestion automation, **Skillset** = AI enrichment, **Index** = what you query. A field needs **filterable** for `$filter`, **retrievable** to return, **searchable** to full-text search.
21. Search query types: **simple** (default), **full** (Lucene: fields, `*`, `~`, boolean), **semantic** (reranks for meaning), **vector/hybrid**. Semantic adds **`@search.reranker_score`** (0–4), separate from BM25 **`@search.score`**.
22. **Red teaming** = proactive attack testing (built on **PyRIT**); it probes the **hate/unfairness, violence, sexual, self-harm** filters at rising difficulty and reports **Attack Success Rate (ASR)** — lower is safer.
23. **Version upgrade policy**: `OnceNewDefaultVersionAvailable` (auto, default), `OnceCurrentVersionExpired` (upgrade only at retirement), `NoAutoUpgrade` (pinned). Auto-upgrade can change agent behaviour (re-evaluate); fine-tunes are pinned to their base version.
24. **RAG** grounds on **text**; **multimodal RAG** grounds on **text + images/visual content** (multimodal embeddings + Document Intelligence/Content Understanding + a multimodal model).

## 41. Recommended study order

1. Guardrail concepts and intervention points.
2. Default, inherited, and overridden policies.
3. Annotate versus block using agent examples.
4. Agent development lifecycle and runtime tool loop.
5. Groundedness, relevance, retrieval, coherence, and fluency.
6. Agent task and tool-use evaluators.
7. Global, Data Zone, geography, Standard, Provisioned, and Batch deployments.
8. Responsible AI principles and how guardrails/evaluations implement them.
9. Foundry SDK clients: `AIProjectClient` vs `get_openai_client()` vs `AzureOpenAI`.
10. Inference APIs: responses, conversations, chat.completions/.parse, agents.create_version.
11. A2A anatomy: skill, agent card, executor, request handler, server.
12. Document Intelligence vs Content Understanding: prebuilt/custom, poller and result.
13. Azure AI Search: indexer, skillset, index, query types, and the semantic reranker score.
14. Red teaming: the AI Red Teaming Agent (PyRIT), the filters it tests, attack difficulty levels, and the ASR score.
15. Model version upgrade policy and its effect on agents and fine-tunes; RAG vs multimodal RAG.

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