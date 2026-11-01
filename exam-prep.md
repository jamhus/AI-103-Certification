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
4. **Constraint:** identity, region, residency, latency, throughput, cost, safety or GA/preview status?
5. **Level:** service, resource, deployment, model ID, API version, SDK client/version, method, role or Responsible AI principle?

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
| Bias recognition toward a small set of expected terms at runtime | Phrase List |
| Improve recognition for domain vocabulary | Custom Speech |
| Evaluate a speaker's pronunciation | Pronunciation Assessment |

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

# Part VII: Power Fx expressions (Copilot Studio agents)

## 23. Power Fx essentials

Copilot Studio agents use **Power Fx** for conditions and text handling. Variables carry a **scope prefix**: `Local.` (topic-local), `Global.`, `System.` — keep it, do not reference a bare variable name.

### Blank vs Empty (the big trap)

```text
IsBlank(value)   → single text/value: is it blank ("" or null)?
IsEmpty(table)   → table/collection: does it have zero rows?
```

- User input is **text** → validate with **`IsBlank`**, never `IsEmpty`.
- `IsEmpty` on a text value is **wrong** — it only tests tables/collections.

| Need | Expression |
|---|---|
| Continue only if the user entered a response (text exists) | `Not(IsBlank(Local.Varx))` |
| True when the value is blank/empty | `IsBlank(Local.Varx)` |
| Table/collection has no rows | `IsEmpty(SomeCollection)` |

### Text case

```text
Upper(text) → UPPERCASE
Lower(text) → lowercase
```

- Power Fx uses **`Upper`** / **`Lower`**. There is **no `ToUpper` / `ToLower`** (classic distractor).
- Keep the prefix: `Upper(Local.Varx)`, not `Upper(Varx)`.

**Traps:**

- `IsEmpty` for a text value → wrong; use `IsBlank`.
- `ToUpper` / `ToLower` → not Power Fx functions.
- Dropping the `Local.` / `Global.` scope prefix.

---

# Part VIII: Exam traps

## 24. Common traps

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


# Part VIII-A: Personal Weak-Point Review

These are recurring patterns from practice-test mistakes. Review this section before the final readiness review.

## 24A. Agent tool decision rules

```text
Agent may decide whether to use a tool → tool_choice="auto"
Agent must use at least one tool       → tool_choice="required"
Agent must not use tools               → tool_choice="none"
```

**Exam clues for `required`:** must always search, retrieve, use knowledge or provide citations.

## 24B. File Search vs Azure AI Search

```text
Files uploaded in the current conversation → File Search
Indexed enterprise content repository       → Azure AI Search
```

**Trap:** Do not choose Azure AI Search merely because a document must be searched. First decide whether it is a conversational upload or an indexed collection.

## 24C. Agent, tool and connection

```text
Agent → invokes a tool
Tool  → uses a connection
Connection → holds the endpoint and authentication configuration
```

```text
API key already exists
Connection is already configured
Authentication header is missing
→ Link the tool or API integration to the connection
```

## 24D. OpenAPI authentication

```text
API key in a request header → apiKey security scheme
OAuth authorisation flow    → OAuth2 security scheme
Bearer access token         → HTTP bearer security scheme
```

Look for `securitySchemes` when credentials must be applied automatically. Avoid hard-coded secrets, prompt variables and manual credential injection.

## 24E. RBAC distinctions

| Requirement | Likely role |
|---|---|
| Invoke or consume an AI capability | Cognitive Services User |
| Create, configure or deploy resources without managing RBAC | Cognitive Services Contributor |
| Manage resources and role assignments | Owner |

**Exam clue:** Create and configure resources, but do not manage access control → **Cognitive Services Contributor**.

## 24F. Cost, quality and execution telemetry

```text
Why are costs increasing?       → Inspect token usage
Was the generated result good?  → Evaluation
What happened during execution? → Observability and traces
```

```text
enable_content_recording=true
→ prompts, responses and tool content can be included in telemetry
```

**Risk:** Content recording can expose sensitive content to the telemetry pipeline.

## 24G. Scanned PDFs and RAG

```text
Scanned PDF + tables + page references
→ OCR + page-aware chunking
```

Page-aware chunking helps preserve page boundaries, citations and structured content.

## 24H. Mixed-language translation

```text
Multiple languages in one segment
→ split into single-language segments
→ translate each segment
→ recombine the result
```

## 24I. Rate limiting and retries

```text
HTTP 429 / throttling / burst traffic
→ exponential backoff with jitter
```

Immediate retries can amplify throttling. Jitter prevents many clients from retrying at the same moment.

## 24J. Image-generation fidelity

```text
Preserve the reference image's appearance, colours, shape or design
→ use high input_fidelity
```

```text
Higher fidelity → more faithful to the input
Lower fidelity  → more creative freedom
```

## 24K. Conversation continuity

```text
Remember messages, tool calls and responses in the current session
→ conversation history
```

Do not confuse current-session continuity with a persistent knowledge store or external memory system.

For cross-conversation personalisation, review **24S: Foundry Memory (preview)** below.

## 24L. Approval variables and exact values

When a workflow stores an approval response, compare the variable with the exact value returned by the approval step.

```text
approval == "approved"
```

**Trap:** Do not assume a Boolean value or invent a synonym such as `"yes"` when the stored response is an explicit status string.

## 24M. API/version literacy

An API version belongs to an **individual service contract**, not to Azure AI or Foundry as a whole. Check the exact service, operation and documented version.

| Contract | Version to recognise | Status |
|---|---|---|
| Content Safety Prompt Shields REST API | `2024-09-01` | GA |
| Document Intelligence v4 REST API | `2024-11-30` | GA |
| Speech-to-text REST API | `2025-10-15` | Current GA |

**Version snapshot:** Verified against Microsoft Learn on 2026-11-01. Recheck the service reference when a question specifies another version or when preparing a deployment.

```text
Model ID/version → Which model or model revision performs the task?
API version      → Which service request/response contract is used?
SDK version      → Which client-library release is installed?
Deployment name  → Which deployed model instance is invoked?
```

- A date-looking model revision is not automatically an API version.
- An SDK release number does not replace the REST `api-version`.
- A newer-looking date is not evidence that a version exists, is supported by that service or is GA.
- A `-preview` suffix flags a preview contract; also check feature-specific status rather than relying on naming alone.

**Sources:** [Prompt Shields REST quickstart](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-jailbreak), [Document Intelligence version support](https://learn.microsoft.com/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0#version-support-and-retirement), [Speech REST migration guide](https://learn.microsoft.com/azure/ai-services/speech-service/migrate-2025-10-15).

## 24N. REST contract recognition

Recognise **exact property names and their location**, not just the feature description.

| Service / operation | Contract element | Meaning |
|---|---|---|
| Prompt Shields: `text:shieldPrompt` | `userPrompt` | User text to analyse for prompt attacks |
| Prompt Shields: `text:shieldPrompt` | `documents` | Array of document text to analyse for injected instructions; not document URLs |
| Speech batch transcription | Root `contentUrls` | Array of individual audio-file URLs |
| Speech batch transcription | Root `contentContainerUrl` | URL of the container holding the audio files |
| Speech batch transcription | `properties.diarizationEnabled` | Enable speaker separation, not speaker identity recognition |
| Speech batch transcription | `properties.timeToLiveHours` | Retention after the job completes, not its execution timeout |
| Document Intelligence analysis | Model ID `prebuilt-layout` | Extract text, tables and document structure |
| Content Safety: `text:analyze` | `haltOnBlocklistHit` | Decide whether a blocklist hit stops further harmful-content analysis |

- Batch audio input: specify either `contentUrls` or `contentContainerUrl`.
- Batch `diarizationEnabled` and `timeToLiveHours` belong inside `properties`, not at the root.
- In the current batch contract, `timeToLiveHours` is required: 6 hours to 31 days; 48 hours is the documented recommendation when consuming results directly.
- `haltOnBlocklistHit=true`: a blocklist hit skips further harmful-content analysis.
- `haltOnBlocklistHit=false`: harmful-content analysis continues even if a blocklist matches.

**Traps:** Prompt Shields checks injected instructions, not general harmful-content categories. `haltOnBlocklistHit` controls analysis short-circuiting; it does not itself implement the application's blocking policy. Do not copy batch transcription properties into fast-transcription requests: those are different operation contracts.

**Sources:** [Prompt Shields request](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-jailbreak#quick-example), [Batch transcription configuration](https://learn.microsoft.com/azure/ai-services/speech-service/batch-transcription-create#request-configuration-options), [Document Intelligence layout model](https://learn.microsoft.com/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0), [Content Safety text request](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-text#analyze-text-content).

## 24O. Language sentiment aggregation

Document sentiment is determined from the **sentence labels**:

| Sentence labels present | Document label |
|---|---|
| Positive, with any remaining sentences neutral | `positive` |
| Negative, with any remaining sentences neutral | `negative` |
| Both positive and negative, with or without neutral sentences | `mixed` |
| Neutral only | `neutral` |

```text
positive + neutral  → positive
negative + neutral  → negative
positive + negative → mixed
neutral only        → neutral
```

**Trap:** Neutral sentences do not turn an otherwise positive or negative document into `mixed`. Do not use majority voting: the presence of both positive and negative sentence labels produces `mixed`.

**Source:** [Sentiment analysis document-label rules](https://learn.microsoft.com/azure/ai-services/language-service/sentiment-opinion-mining/how-to/call-api#sentiment-analysis).

## 24P. Speech recognition optimisation

| Requirement | Choose | Why |
|---|---|---|
| Small set of expected names, product names or terms at runtime | Phrase List | Biases recognition without training a model |
| Persistent domain-specific recognition accuracy | Custom Speech | Adapts a model using domain training data |
| Score pronunciation, fluency or completeness | Pronunciation Assessment | Evaluates how speech is pronounced |

```text
Expected vocabulary for this recognition session → Phrase List
Reusable domain-adapted recognition model         → Custom Speech
Evaluate the speaker's pronunciation              → Pronunciation Assessment
```

**Traps:** Pronunciation Assessment is not a vocabulary-correction feature. Phrase lists bias recognition; they do not guarantee a term will be recognised. Check the recognition route: phrase lists support real-time recognition and supported fast-transcription APIs, but not batch transcription.

**Sources:** [Phrase lists](https://learn.microsoft.com/azure/ai-services/speech-service/improve-accuracy-phrase-list), [Custom Speech](https://learn.microsoft.com/azure/ai-services/speech-service/custom-speech-overview), [Pronunciation Assessment](https://learn.microsoft.com/azure/ai-services/speech-service/how-to-pronunciation-assessment).

## 24Q. Custom Speech model lifecycle

An expired custom or base model is no longer available for transcription. The result depends on **how the model is invoked**:

| Route | Expired-model behaviour | Action |
|---|---|---|
| Recognition through a custom endpoint | Falls back to the most recent base model for the same locale | Update the endpoint to a non-expired model |
| Batch transcription explicitly referencing an expired model | Fails with a 4xx error | Reference a non-expired model, or omit `model` to use the latest base model |

```text
Custom endpoint + expired model → base-model fallback; domain accuracy can drop
Batch + explicit expired model → 4xx failure; no automatic fallback
```

**Trap:** A successful response from a custom endpoint does not prove the custom model is still being used. Monitor expiration and validate accuracy after replacing the model; do not confuse model expiration with API-version retirement.

**Source:** [Custom Speech expiration behaviour](https://learn.microsoft.com/azure/ai-services/speech-service/how-to-custom-speech-model-and-endpoint-lifecycle#what-to-do-when-a-model-expires).

## 24R. Azure AI Search lexical analysis

```text
Input text → character filters → tokenizer → token filters → indexed/query tokens
```

- **Character filters:** Transform text before tokenisation, such as removing markup.
- **Tokenizer:** Splits the resulting text into tokens.
- **Token filters:** Transform or remove tokens after tokenisation, such as lowercasing.
- **`CustomAnalyzer`:** Combines exactly one tokenizer with optional character and token filters. REST type: `#Microsoft.Azure.Search.CustomAnalyzer`.
- **`keyword_v2`:** Preserves the input as a whole-value token, subject to its maximum token length.

| Content | Analysis goal |
|---|---|
| Natural-language descriptions | Split into useful words; apply appropriate linguistic analysis |
| Product codes and identifiers | Preserve the complete value rather than splitting on punctuation |

```text
Product code AB-123/CD must remain one searchable term
→ CustomAnalyzer with keyword_v2
→ optionally lowercase if case-insensitive matching is required
```

**Traps:** `keyword_v2` is a tokenizer, not a language analyzer. Character/token filters can still alter the value. Its default maximum token length is 256 characters (configurable up to 300); longer inputs are split. Apply compatible analysis at indexing and query time. For exact conditions on filterable identifier fields, consider a filter rather than full-text search.

**Sources:** [Custom analyzer pipeline and tokenizer reference](https://learn.microsoft.com/azure/search/index-add-custom-analyzers), [Whole-value tokenisation example](https://learn.microsoft.com/azure/search/tutorial-create-custom-analyzer#build-a-custom-analyzer).

## 24S. Foundry Memory (preview)

```text
Conversation state → Messages, tool calls and responses in a conversation
Persistent memory → Selected information retained and retrieved across conversations
Memory store      → Holds memory items partitioned by scope
```

| Element | Purpose |
|---|---|
| `MemorySearchPreviewTool` | Attach memory access to a prompt agent |
| `scope` | Partition memory items into isolated collections within a store |
| `{{$userId}}` | Resolve the memory search tool's scope to the end user |
| `update_delay` | Debounce automatic memory writes until the configured inactivity period, in seconds |

- For per-user memory through the agent tool, set `scope` to `{{$userId}}`.
- In backend/proxy scenarios, supply `x-memory-user-id` on each response call from the authenticated end-user identity.
- Without that header, scope resolution falls back to the caller's Microsoft Entra tenant/object identity. A shared backend identity is not automatically a distinct identity for each end user.
- A static scope shares that collection among calls using the same scope; it does not provide per-user isolation.
- Low-level memory API calls require an explicit scope; they do not automatically extract the end-user identity.
- Automatic updates are scheduled after responses and debounced by `update_delay`; do not assume every turn is written immediately.

**Traps:** Memory is not simply the complete conversation transcript or an enterprise document index. Foundry Memory and the Memory Store API are **preview**; recheck the current SDK/schema and deployment terms.

**Source:** [Create and use Foundry memory: scope, tool and update behaviour](https://learn.microsoft.com/azure/foundry/agents/how-to/memory-usage).

## 24T. Preview versus GA

Treat availability status as a **deployment and risk constraint**, not a cosmetic label.

```text
Visible in the portal → Available to try; not proof of GA
Newer API date        → Not proof of GA or service compatibility
Production/SLA need   → Check feature status, support and applicable terms
Explicit GA-only need → Exclude preview features/contracts
```

- Check both the service API version and the particular feature's status: a feature can be preview within a broader GA service.
- For production or SLA scenarios, explicitly evaluate preview terms, support commitments, regional availability and change risk.
- Do not assume a parent service's SLA automatically covers a preview feature.
- Preview is not automatically forbidden for every workload; it must satisfy the question's explicit requirements and the organisation's accepted risk.

**Source:** [Foundry Memory preview notice and applicable terms](https://learn.microsoft.com/azure/foundry/agents/how-to/memory-usage).

## Personal weakness check

Before booking, confirm that you can explain without notes:

- Why `tool_choice="required"` differs from `auto`.
- When File Search is preferable to Azure AI Search.
- How an agent, tool and connection relate to one another.
- How OpenAPI `securitySchemes` apply credentials.
- Why Contributor fits resource management without RBAC management.
- Why token usage explains cost while evaluation measures quality.
- What content recording can place in telemetry.
- Why OCR and page-aware chunking suit scanned structured PDFs.
- Why mixed-language segments should be separated before translation.
- Why HTTP 429 calls for exponential backoff with jitter.
- What high `input_fidelity` controls.
- When conversation history is enough and persistent storage is unnecessary.
- Why workflow conditions must use the exact stored status value.
- Why model IDs, API versions, SDK versions and deployment names are different.
- Which service contracts use `2024-09-01`, `2024-11-30` and `2025-10-15`.
- Where Prompt Shields and batch transcription request properties belong.
- What `prebuilt-layout` and `haltOnBlocklistHit` mean.
- How positive, negative and neutral sentence labels determine document sentiment.
- When to use Phrase List, Custom Speech or Pronunciation Assessment.
- Why expired Custom Speech models cause endpoint fallback but explicit batch references fail.
- How character filters, tokenizers and token filters differ.
- Why `keyword_v2` suits whole-value product identifiers.
- How Foundry memory differs from conversation state and isolates end users by scope.
- What `update_delay` controls and why Foundry Memory's preview status matters.
- Why portal availability and a newer API date do not establish GA or SLA coverage.


# Part IX: Final readiness review

## 25. Rapid review

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

## 26. Booking checklist

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
- Recognise exact REST fields and service-specific API versions.
- Apply sentiment aggregation, Speech optimisation and expired-model decision rules.
- Choose lexical analysis for natural language versus whole-value identifiers.
- Explain persistent memory, per-user scope and preview deployment constraints.
- Explain why the strongest distractor is wrong.

### Final test

For every missed practice question, state:

1. The requirement you overlooked.
2. The decision rule that gives the correct answer.
3. Why your original choice was tempting.
4. Why the closest alternative is wrong.
