# Microsoft Foundry Study Guide: Guardrails, Agents, Evaluations, Model Deployments, and Fine-Tuning

_Last updated: 12 October 2026_

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

# Part VI: High-value summary

## 29. Facts to remember

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

## 30. Recommended study order

1. Guardrail concepts and intervention points.
2. Default, inherited, and overridden policies.
3. Annotate versus block using agent examples.
4. Agent development lifecycle and runtime tool loop.
5. Groundedness, relevance, retrieval, coherence, and fluency.
6. Agent task and tool-use evaluators.
7. Global, Data Zone, geography, Standard, Provisioned, and Batch deployments.

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
