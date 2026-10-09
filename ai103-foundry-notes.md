# Microsoft Foundry Study Guide: Guardrails, Agents, Evaluations, and Model Deployments

_Last updated: 9 October 2026_

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
9. **Version and publish**: save a known version and expose a stable integration.
10. **Monitor production**: watch latency, errors, token usage, safety signals, tool failures, and quality drift.
11. **Improve or roll back**: change model, instructions, tools, retrieval, or policy; then rerun regression tests.
12. **Retire**: remove access, revoke connections/identities, preserve required audit evidence, and migrate users.

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

| Evaluator | Short explanation |
|---|---|
| **Coherence** | Logical consistency and flow. |
| **Fluency** | Readability and natural-language quality. |
| **Similarity** | Semantic similarity to a reference. Similarity does not guarantee factual correctness. |
| **F1** | Token overlap using the harmonic mean of precision and recall. |
| **BLEU / GLEU** | N-gram overlap, often used for translation or reference-based generation. |
| **ROUGE** | Reference overlap with emphasis on recall, often used for summaries. |
| **METEOR** | Reference similarity with ordering and language variation considered. |

## 14. RAG and grounding evaluators

| Evaluator | Short explanation |
|---|---|
| **Groundedness** | Whether claims are supported by supplied/retrieved context. A true claim can still be ungrounded when the context does not support it. |
| **Groundedness Pro** | Preview pass/fail evaluator using Azure AI Content Safety; no separate judge-model deployment is required. |
| **Relevance** | Whether the response addresses the query. |
| **Retrieval** | How effectively the system retrieves relevant information. |
| **Document Retrieval** | Retrieval accuracy against ground-truth relevant documents. |
| **Response Completeness** | Preview measure of whether critical ground-truth information is missing. |

### Groundedness versus correctness

- **Groundedness:** Is the answer supported by this context?
- **Correctness:** Is the answer actually right?
- **Relevance:** Does the answer address the question?

A response can be relevant but ungrounded, grounded but incomplete, or grounded in an incorrect source.

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
| **Developer** | `DeveloperTier` | See current model documentation | Pay per token | Short-lived fine-tuned-model evaluation |

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

---

# Part V: High-value summary

## 23. Facts to remember

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

## 24. Recommended study order

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
