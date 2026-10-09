# Azure AI Foundry Study Notes (AI-103/AI-102 aligned)
_Last updated: 2026-10-09_
 
These notes summarize:
- Guardrails (models vs agents), defaults, and actions (annotate vs block)
- Agent development lifecycle
- Agent & model evaluations (fairness/hate-unfairness, groundedness, and other common metrics)
- Model deployment types (Global / Standard / Data Zone / Provisioned / Batch / Developer)
 
---
 
## 1) Guardrails in Microsoft Foundry (Models vs Agents)
 
### 1.1 What guardrails are
A **guardrail** is a named collection of **controls**. Controls define:
- a **risk** to detect,
- **intervention point(s)** to scan,
- and the **action** to take when detected.
Source: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview
 
Guardrails use classification models (Azure AI Content Safety) to detect harmful content.
Source: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview
 
### 1.2 Intervention points (where scanning happens)
Four intervention points are supported:
- **User input** (prompt sent to model/agent)
- **Tool call** (agents only; preview) — what the agent is about to send to a tool
- **Tool response** (agents only; preview) — what a tool returns to the agent before it’s saved/used
- **Output** — final response sent to the user
Source: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview
Source: https://learn.microsoft.com/azure/foundry/guardrails/intervention-points
 
**Applicability:**
- Models: **User input**, **Output**
- Agents: **User input**, **Tool call**, **Tool response**, **Output**
Source: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview#intervention-point-applicability
 
> Note: Tool call/tool response controls require moderation support from the tool; only certain tools currently support it.
Source: https://learn.microsoft.com/azure/foundry/guardrails/intervention-points#supported-tools
 
### 1.3 Actions: Annotate vs Annotate and block
When a control detects a risk, it can take one of two actions:
 
| Action | Models | Agents (Preview) |
|---|---:|---:|
| Annotate | ✅ | ❌ |
| Annotate and block | ✅ | ✅ |
 
Source: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview#action-applicability
 
**What they mean:**
- **Annotate (models only):** the content isn’t blocked, but the response includes annotations your app can inspect/log.
- **Annotate and block (models + agents):** the system stops the flow at that intervention point.
- Example: on **user input**, the prompt is blocked and never reaches the model/agent.
- Example: on **tool call**, the tool call won’t execute and the agent stops until new user input.
- Example: on **tool response**, the agent stops and the malicious tool output isn’t saved/used.
Source: https://learn.microsoft.com/azure/foundry/guardrails/intervention-points
 
### 1.4 Defaults: model vs agent
**Default for model deployments:** models are assigned **Microsoft.DefaultV2** guardrail by default.
Source: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview#default-guardrails
 
**Default for agents (rules):**
1. If you assign a custom guardrail to an agent, it uses that guardrail.
2. If no custom guardrail is assigned, the agent inherits the underlying model deployment’s guardrail.
3. An agent only uses **Microsoft.DefaultV2** if the model deployment uses it or you explicitly assign it.
Source: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview#default-guardrails
 
### 1.5 Inheritance/override behavior (critical exam concept)
**Agent guardrails override model guardrails.** Risks in an agent are detected based on the agent’s assigned guardrail, not the underlying model’s guardrail.
Source: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview#guardrail-inheritance-and-override
 
**Consequence:** If an agent has a custom guardrail that doesn’t include tool call/tool response controls, then those steps may not be scanned—even if the underlying model deployment guardrail was stricter.
Source example behavior: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview#example-guardrail-override-behavior
 
---
 
## 2) Agent Development Lifecycle (Foundry)
 
Foundry’s suggested lifecycle checklist:
1. Choose agent type (prompt-based, voice-based prompt agent, or hosted agent)
2. Create agent and test (playground or code)
3. Add tools and data
4. Save changes as versions
5. Debug with tracing
6. Evaluate quality and safety
7. Optimize hosted agents (preview)
8. Publish and integrate
9. Monitor and iterate in production
Source: https://learn.microsoft.com/azure/foundry/agents/concepts/development-lifecycle#lifecycle-at-a-glance
 
Agent types overview (high level):
- **Prompt-based:** configured in portal (model + instructions + tools)
- **Voice-based prompt agents:** prompt-based agent optimized for real-time spoken interactions
- **Hosted:** containerized agents built in code; Foundry deploys/manages runtime
Source: https://learn.microsoft.com/azure/foundry/agents/concepts/development-lifecycle#agent-types-in-microsoft-foundry
 
---
 
## 3) Evaluations (Quality, Groundedness, Fairness, Safety, Agent Behavior)
 
### 3.1 What “evaluators” are
Evaluators measure the **quality, safety, and reliability** of AI responses across the lifecycle.
Source: https://learn.microsoft.com/azure/foundry/concepts/observability#core-observability-capabilities
 
A full reference list is here:
Source: https://learn.microsoft.com/azure/foundry/concepts/built-in-evaluators
 
---
 
### 3.2 Key evaluation metrics (short explanations)
 
#### Groundedness (RAG quality)
- **What it measures:** how well the response is supported (“grounded”) in the provided/retrieved context.
- **Output:** score 1–5 (model-based judgment).
Source: https://learn.microsoft.com/azure/foundry/concepts/built-in-evaluators#rag-evaluators
 
#### Groundedness Pro (preview)
- **What it measures:** whether the response is grounded in retrieved context.
- **Output:** binary pass/fail (uses Azure AI Content Safety; doesn’t require a model deployment).
Source: https://learn.microsoft.com/azure/foundry/concepts/built-in-evaluators#rag-evaluators
 
#### Relevance (RAG quality)
- **What it measures:** how relevant the response is to the query.
Source: https://learn.microsoft.com/azure/foundry/concepts/built-in-evaluators#rag-evaluators
 
#### Retrieval / Document Retrieval (RAG quality)
- **Retrieval:** measures how effectively the system retrieves relevant information.
- **Document Retrieval:** measures accuracy in retrieval results given ground truth.
Source: https://learn.microsoft.com/azure/foundry/concepts/built-in-evaluators#rag-evaluators
 
#### Coherence / Fluency (general quality)
- **Coherence:** logical consistency and flow.
- **Fluency:** language quality/readability.
Source: https://learn.microsoft.com/azure/foundry/concepts/built-in-evaluators#general-purpose-evaluators
 
---
 
### 3.3 “Fairness” in Foundry evaluations (commonly tested)
In Foundry’s built-in evaluators, “fairness” is typically represented under:
 
#### Hate and Unfairness (safety / fairness-style evaluation)
- **What it measures:** identifies biased, discriminatory, or hateful content.
Source: https://learn.microsoft.com/azure/foundry/concepts/built-in-evaluators#risk-and-safety-evaluators
 
(You’ll also see this labeled as `hate_unfairness` in evaluator lists/SDKs.)
 
---
 
### 3.4 Agent evaluators (how well the agent behaves, uses tools, and completes tasks)
 
Foundry agent evaluators act like unit tests for agent workflows (system-level and process-level).
Source: https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators
 
**System evaluation (end-to-end outcome):**
- **Task Completion (preview):** did it complete the user’s requested task end-to-end with a usable deliverable?
- **Customer Satisfaction (preview):** overall satisfaction across dimensions like helpfulness/completeness/clarity/tone/resolution/adaptability
- **Task Adherence (preview):** did it follow rules/constraints/instructions?
- **Task Navigation Efficiency:** did it take the expected/optimal steps? (requires ground truth)
- **Intent Resolution (preview):** did it correctly identify and address user intent?
Source: https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators#system-evaluation
Source: https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators (table)
 
**Process evaluation (tool-use correctness):**
- **Tool Call Accuracy:** right tools + right parameters + efficiency
- **Tool Selection:** chose necessary tools without unnecessary ones
- **Tool Input Accuracy:** strict parameter correctness checks (type/format/required/unexpected/value appropriateness, etc.)
- **Tool Output Utilization:** used tool results correctly in reasoning/final response
- **Tool Call Success:** tool calls succeeded (no errors/timeouts)
Source: https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators#process-evaluation
 
---
 
## 4) Model Deployment Types (Global vs Standard vs Data Zone, etc.)
 
When you deploy a model in Foundry, the **deployment type** determines:
- where data is processed,
- how you pay (pay-per-token vs reserved capacity),
- and performance characteristics (throughput/latency variance).
Source: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types
 
### 4.1 Big picture categories
Foundry describes these major categories:
- **Standard** (pay-per-token)
- **Provisioned** (reserved capacity, “PTUs”)
- **Batch** (discounted asynchronous, large jobs)
- **Developer** (fine-tuned model evaluation only; temporary/no SLA)
Source: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types
 
### 4.2 Data residency / processing location options
**Data at rest** remains in the Azure geography of the resource, but **inferencing data processing** differs:
 
- **Global**: may be processed in any Azure region
- **Data Zone**: processed only within a Microsoft-defined data zone (US, EU, APAC)
- **Azure geography (regional)**: processed within the customer-specified Azure geography (may move within that geography for operational purposes)
Source: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types#deployment-types-for-microsoft-foundry-models
 
### 4.3 Deployment type comparison (cheat sheet)
From the Foundry table:
 
| Deployment type | SKU code | Data processing | Billing | Best for |
|---|---|---|---|---|
| Global Standard | `GlobalStandard` | Any Azure region | Pay-per-token | General workloads, highest quota |
| Global Provisioned | `GlobalProvisionedManaged` | Any Azure region | Reserved PTU | Predictable high-throughput |
| Global Batch | `GlobalBatch` | Any Azure region | 50% discount, async | Large async jobs |
| Data Zone Standard | `DataZoneStandard` | Within data zone | Pay-per-token | Data zone compliance (EU/US/APAC) |
| Data Zone Provisioned | `DataZoneProvisionedManaged` | Within data zone | Reserved PTU | Data zone + predictable throughput |
| Data Zone Batch | `DataZoneBatch` | Within data zone | Discounted async | Large async jobs + data zone |
| Standard | `Standard` | Within Azure geography | Pay-per-token | Geography compliance, low/medium volume |
| Regional Provisioned | `ProvisionedManaged` | Within Azure geography | Reserved PTU | Geography compliance + throughput |
| Developer | `DeveloperTier` | Any Azure region | Pay-per-token | Fine-tuned evaluation only (24h lifetime, no SLA / residency guarantee) |
 
Source: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types#deployment-type-comparison
 
### 4.4 Practical selection guidance
- Start with **Global Standard** for most workloads; it’s often the first place new models/features appear and has broad availability.
Source: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types#start-with-global-standard
- Use **Provisioned** for more predictable throughput and lower latency variance at scale.
Source: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types
- Use **Data Zone** when you need processing restricted to US/EU/APAC zones.
Source: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types#data-zone-deployments
- Use **Batch** for large async jobs that are delay-tolerant (lower cost).
Source: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types#global-batch
 
---
 
## 5) Suggested “Study Links” (Official Docs)
- Guardrails overview: https://learn.microsoft.com/azure/foundry/guardrails/guardrails-overview
- Intervention points: https://learn.microsoft.com/azure/foundry/guardrails/intervention-points
- Agent development lifecycle: https://learn.microsoft.com/azure/foundry/agents/concepts/development-lifecycle
- Built-in evaluators reference: https://learn.microsoft.com/azure/foundry/concepts/built-in-evaluators
- Agent evaluators: https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators
- Deployment types: https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deployment-types