# AI-103 Master Study Guide

> **Purpose:** A simple, complete review guide to skim after finishing the learning material and before booking the AI-103 exam.
>
> Focus on decision rules, service boundaries, SDK names and scenario clues. Use deeper notes only when a topic below feels unclear.

---

## 1. Start every exam question here

Before looking at the answers, identify:

1. **Input:** text, image, audio, document, search query, prompt or multimodal content?
2. **Output:** classification, extraction, generation, retrieval, translation or action?
3. **Operation:** create, configure, deploy, invoke, analyse, monitor or evaluate?
4. **Constraint:** identity, region, residency, latency, throughput, cost or safety?
5. **Level:** service, resource, deployment, SDK client, method, role or Responsible AI principle?

**Golden rule:** Choose the simplest supported service that satisfies every explicit requirement.

---

# Part I: Choose the right service

## 2. Azure AI Language

Use Azure AI Language when the input is text and the goal is to analyse its linguistic meaning.

| Need | Capability |
|---|---|
| Identify the language | Language detection |
| Detect positive, neutral or negative sentiment | Sentiment analysis |
| Detect sentiment about individual aspects | Opinion mining |
| Extract important phrases | Key phrase extraction |
| Identify people, places, organisations and dates | Named Entity Recognition |
| Connect an entity to an external identity | Entity linking |
| Detect or redact personal information | PII detection |
| Produce a shorter version of text | Summarisation |
| Define domain-specific entities | Custom NER |
| Assign custom categories to text | Custom text classification |
| Answer questions from curated content | Question answering |

```text
Analyse one piece of text → Azure AI Language
Retrieve content from a collection → Azure AI Search
Generate new text → Generative model
```

**SDK:** `TextAnalyticsClient`

## 3. Azure AI Speech

| Need | Capability / object |
|---|---|
| Speech to text | Speech recognition |
| Text to speech | Speech synthesis |
| Spoken-language translation | Speech translation |
| Control pronunciation and speaking style | SSML |
| Improve recognition for domain vocabulary | Custom Speech |

```text
SpeechConfig          → Configuration
SpeechRecognizer      → Speech to text
SpeechSynthesizer     → Text to speech
TranslationRecognizer → Speech translation
```

**Trap:** A recogniser consumes audio and returns text. A synthesiser consumes text and returns audio.

## 4. Vision, OCR and documents

### Azure AI Vision

Use for general image analysis:

- OCR from a general image
- Image and dense captions
- Tags
- Object detection
- Smart crops

### Document Intelligence

Use when document structure matters:

- Printed or handwritten document text
- Layout, tables, paragraphs and selection marks
- Prebuilt invoice, receipt and ID models
- Custom extraction
- Document classification

### Content Understanding

Use for schema-driven extraction and analysis across supported content types, especially when the requirement goes beyond a conventional document model.

```text
General image understanding → Azure AI Vision
Document text, layout and business fields → Document Intelligence
Broader multimodal schema extraction → Content Understanding
```

**OCR trap:** Do not select the service from the word OCR alone. Identify the content type and required output.

## 5. Azure AI Search

Use Azure AI Search to retrieve and rank relevant content from a collection.

```text
Index           → Searchable fields and content
Indexer         → Moves source data into an index
Data source     → Connection to source content
Skillset        → Enrichment pipeline
Vector search   → Similarity using embeddings
Semantic ranker → Semantic reranking
Hybrid search   → Text plus vector search
Filter          → Exact condition on filterable fields
```

### RAG flow

```text
Question → query/embedding → retrieve chunks → add context → generate answer
```

**Trap:** Azure AI Search retrieves content. A generative model produces the final answer.

## 6. Generative AI models

Use a direct model call for prompt-to-response generation without reusable agent behaviour or tool orchestration.

Common requirements:

- Text generation and summarisation
- Prompt-based classification
- Structured output
- Multimodal understanding
- Embeddings

```text
Model name      → Underlying model
Deployment name → Application-facing deployed instance
```

Applications normally invoke the **deployment name**.

## 7. Foundry agents

Use an agent when the solution needs reusable behaviour around a model:

- Instructions
- Tools
- Knowledge
- Conversation state
- Identity
- Orchestration
- Guardrails
- Tracing

```text
Agent definition/version → Durable configuration
Conversation/session     → Continuity across turns
Response/run             → One execution
Trace                    → Execution telemetry
```

```text
Application function → Function tool
REST API contract    → OpenAPI tool
Search knowledge     → Search/knowledge tool
MCP-exposed tools    → MCP tool/server
```

**Trap:** Do not choose an agent if a direct model call fully satisfies the requirement.

---

# Part II: Identity, access and resources

## 8. Authentication

### API key

- Secret-based credential
- Must be protected and rotated

### Microsoft Entra ID

- Identity-based authentication
- Supports Azure RBAC

### Managed identity

Use for supported Azure workloads when the application should authenticate without stored secrets.

```text
System-assigned → Tied to one resource
User-assigned   → Separate reusable identity
```

```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```

`DefaultAzureCredential` is a credential chain. The effective identity depends on the environment.

## 9. Authentication versus authorisation

```text
Authentication → Who is the caller?
Authorisation  → What may the caller do?
```

RBAC checklist:

1. Who performs the operation?
2. What operation is required?
3. Where should access be scoped?
4. Is it control plane or data plane?
5. What is the least-privileged suitable role and scope?

## 10. Control plane versus data plane

### Control plane

- Create or configure resources
- Manage deployments
- Configure networking
- Manage project settings

### Data plane

- Invoke a model
- Analyse text or an image
- Search an index
- Process a document

**Trap:** A management role does not necessarily grant every data-plane action.

## 11. Foundry resource map

```text
Azure subscription
└── Resource group
    └── Microsoft Foundry resource
        ├── Foundry project
        │   ├── Agents
        │   ├── Connections
        │   ├── Datasets
        │   ├── Evaluations
        │   └── Knowledge and indexes
        └── Model deployments
```

Do not confuse resource, project, connection, endpoint, model, deployment, agent version, conversation and response.

---

# Part III: Deployments and model operations

## 12. Deployment selection

```text
Global Standard → Shared global capacity where supported
Data Zone       → Processing within a supported data zone
Regional option → Region/geography-specific requirement
Provisioned     → Reserved, predictable throughput
Batch           → Large asynchronous processing
```

Decision order:

1. Processing and residency boundary
2. Model availability
3. Real-time or asynchronous workload
4. Throughput predictability
5. Cost and utilisation
6. Model-version policy

```text
EU processing boundary      → Data Zone
Large offline workload      → Batch
Stable high-volume workload → Provisioned
```

## 13. Model versions

Distinguish between:

- Automatic upgrades
- Upgrade when the current version is retired
- Pinned version
- Validation before adopting a newer version

**Rule:** Reproducibility favours tighter version control.

## 14. Fine-tuning

```text
Correct examples       → SFT
Preferred vs rejected  → DPO
Reliable grader/reward → RFT
```

- **SFT:** Learn from labelled input-output examples.
- **DPO:** Learn from preferred and rejected responses.
- **RFT:** Learn from a grader or reward signal.

**Trap:** Fine-tuning changes behaviour. RAG supplies knowledge at runtime. Prompt engineering changes instructions.

---

# Part IV: Safety, evaluation and operations

## 15. Responsible AI

| Scenario | Principle |
|---|---|
| Unjustified outcome differences | Fairness |
| Safe and dependable behaviour | Reliability and safety |
| Protection of data and systems | Privacy and security |
| Design for varied abilities | Inclusiveness |
| Explain behaviour and limitations | Transparency |
| Human ownership and oversight | Accountability |

```text
Explain the system → Transparency
Own and govern decisions → Accountability
```

## 16. Content safety and guardrails

Capabilities can include:

- Harm-category detection
- Severity information
- Prompt Shields
- Protected-material detection
- Custom blocklists
- Custom categories where supported

```text
User input → input guardrail → model/agent → tools → output guardrail → user
```

```text
Annotate           → Detect and return metadata
Annotate and block → Detect and stop the flow
```

Guardrails do not replace RBAC, validation, tool allowlists, business rules, approvals, transaction limits or audit logging.

## 17. Prompt attacks

```text
Direct attack   → Malicious instruction in the user prompt
Indirect attack → Malicious instruction in retrieved/tool content
```

Use layered mitigation: Prompt Shields, trusted sources, least privilege, strict schemas, validation and human approval for high-impact actions.

## 18. Evaluation

### Quality

- Relevance
- Coherence
- Fluency
- Similarity
- Task success

### Grounded generation

- Groundedness
- Retrieval relevance
- Response completeness

### Agent evaluation

- Task completion
- Tool-call correctness
- Tool-call success
- Path/trajectory quality

```text
Offline evaluation → Prepared datasets and repeatable experiments
Production signals → Live samples, traces, latency, failures and drift
```

## 19. Observability

```text
Trace → Complete request path
Span  → One operation in the trace
```

Observe latency, errors, dependencies, token use, tool failures and model calls.

```text
Observability → What happened?
Evaluation    → Was the result good?
```

---

# Part V: Information extraction

## 20. Document Intelligence

```text
Read     → Text extraction
Layout   → Structure, tables and positions
Prebuilt → Known document type
Custom   → Organisation-specific fields
```

Document analysis commonly uses a long-running operation and poller.

## 21. Content Understanding

An analyzer defines what should be identified or extracted.

Common field shapes:

- String
- Number
- Date
- Boolean
- Array
- Object

```text
Classification → What kind of content is this?
Extraction     → Which values are present?
```

Use arrays for repeating items, nested objects for grouped fields and clear field descriptions.

---

# Part VI: SDK recognition

## 22. Core list

```text
AIProjectClient            → Foundry project operations
DefaultAzureCredential     → Microsoft Entra credential chain
TextAnalyticsClient        → Azure AI Language
DocumentIntelligenceClient → Document Intelligence
SpeechConfig               → Speech configuration
SpeechRecognizer           → Speech to text
SpeechSynthesizer          → Text to speech
TranslationRecognizer      → Speech translation
```

For code questions:

1. Check the imported package.
2. Identify the client.
3. Identify input and output.
4. Check authentication.
5. Decide control plane or data plane.
6. Check whether a poller is required.
7. Eliminate methods from another client.

---

# Part VII: Exam traps

## 23. Common traps

- Choosing the most advanced product instead of the simplest suitable service.
- Missing one constraint such as geography, identity, latency or throughput.
- Mixing Language with Search.
- Mixing Vision with Document Intelligence.
- Mixing Document Intelligence with Content Understanding.
- Mixing a direct model call with an agent.
- Mixing observability with evaluation.
- Mixing authentication with authorisation.
- Mixing control plane with data plane.
- Reading the answer choices before forming an expected solution.
- Memorising definitions without practising scenarios.

---

# Part VIII: Final readiness review

## 24. Rapid review

```text
Text meaning                         → Azure AI Language
Collection retrieval and ranking    → Azure AI Search
General image understanding         → Azure AI Vision
Document structure and fields       → Document Intelligence
Multimodal schema extraction        → Content Understanding
Speech recognition                  → SpeechRecognizer
Speech generation                   → SpeechSynthesizer
Project-level Foundry operations    → AIProjectClient
Identity without stored secrets     → Managed identity
Who is the caller?                  → Authentication
What may the caller do?             → Authorisation/RBAC
Manage Azure resources              → Control plane
Invoke an AI capability             → Data plane
What happened during execution?     → Observability
Was the result good?                → Evaluation
Unequal outcomes                    → Fairness
Safe operation and failure handling → Reliability and safety
Personal data protection            → Privacy and security
Accessible for varied users         → Inclusiveness
Explain behaviour and limitations   → Transparency
Human ownership and oversight       → Accountability
Data-zone processing constraint     → Data Zone
Predictable reserved capacity       → Provisioned
Large asynchronous processing       → Batch
Correct examples for tuning         → SFT
Preferred and rejected answers      → DPO
Reliable reward or grader           → RFT
```

## 25. Booking checklist

Consider booking when you can, without opening detailed notes:

- Select Language, Search, Vision, Speech, Document Intelligence or Content Understanding from a scenario.
- Explain direct model call versus agent.
- Recognise the main SDK clients.
- Explain authentication versus authorisation.
- Explain control plane versus data plane.
- Choose deployments from geography and throughput clues.
- Identify all Responsible AI principles from scenarios.
- Explain observability versus evaluation.
- Explain SFT versus DPO versus RFT.
- Explain why the strongest distractor is wrong.

### Final test

For every missed practice question, state:

1. The requirement you overlooked.
2. The decision rule that gives the correct answer.
3. Why your original choice was tempting.
4. Why the closest alternative is wrong.
