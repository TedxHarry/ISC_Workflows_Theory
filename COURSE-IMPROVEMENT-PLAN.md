# ISC Workflows Theory — Course Improvement Plan

## Goal

Refactor the existing theory course into a deliberately sequenced beginner-to-engineer learning path while preserving the strong existing material, Acme/Priya narrative, production-minded engineering lessons, and personal mentor voice.

This plan does **not** include hands-on labs. Labs are a separate course.

---

# 1. Final Course Architecture

## Part I — Foundations

### 00 — Orientation
**Learner outcome:** Understand what ISC Workflows are, where they fit among other ISC capabilities, and how the course will teach workflow engineering.

### 01 — The Workflow Model
**Learner outcome:** Understand trigger → data → steps → decisions → outcomes, and why later steps can use data produced earlier.

### 02 — Data, Payloads, Variables & JSONPath
**Learner outcome:** Read workflow JSON confidently enough to identify objects, arrays, paths, missing data, and values produced by earlier steps.

---

## Part II — Building Blocks

### 03 — Triggers & Filters
**Learner outcome:** Hear a business event and identify the most appropriate workflow trigger and filter boundary.

### 04 — Operators & Logic
**Learner outcome:** Turn business conditions into branches, validations, variable operations, and appropriately scoped loops.

### 05 — Actions & Error Handling
**Learner outcome:** Choose appropriate actions, understand what their success actually guarantees, and design deliberate error paths.

### 06 — Forms, Approvals & Interactive Workflows
**Learner outcome:** Choose correctly among intake forms, form actions, delegated interactive workflows, and governed approval mechanisms.

---

## Part III — Operating Workflows

### 07 — Testing, Debugging & Execution
**Learner outcome:** Diagnose workflow behavior systematically from trigger input through the first unexpected step and downstream business boundary.

### 08 — Operations, Limits & Governance
**Learner outcome:** Treat workflows as production assets with ownership, limits, promotion, secrets, monitoring, maintenance, and lifecycle concerns.

---

## Part IV — Engineering Judgment

### 09 — When to Use Workflows and When Not
**Learner outcome:** Decide whether a requirement belongs in Workflow or another ISC capability and defend that decision.

### 10 — Real-World Workflow Patterns
**Learner outcome:** Recognize and adapt common production workflow shapes without blindly copying them.

### 11 — Challenges, Failure Modes & Edge Cases
**Learner outcome:** Anticipate replay, concurrency, partial failure, external dependency, scale, and signal-vs-verdict problems before production.

### 12 — Readiness & Paper Design
**Learner outcome:** Design and defend a complete workflow architecture before opening the visual builder.

---

# 2. Existing-to-New Module Mapping

Current repository mapping:

```text
Current 00 Orientation                         → New 00 Orientation
Current 01 Workflow Model                     → New 01 Workflow Model
Current 06 Data, Variables & Expressions      → New 02 Data, Payloads, Variables & JSONPath
Current 02 Triggers                           → New 03 Triggers & Filters
Current 03 Operators & Logic                  → New 04 Operators & Logic
Current 04 Actions                            → New 05 Actions & Error Handling
Current 05 Forms & Interactive Workflows      → New 06 Forms, Approvals & Interactive Workflows
Current 07 Testing, Debugging & Execution     → New 07
Current 08 Operations, Limits & Governance    → New 08
Current 09 When to Use Workflows              → New 09
Current 10 Use Case Patterns                  → New 10 Real-World Workflow Patterns
Current 11 Challenges & Edge Cases            → New 11 Challenges, Failure Modes & Edge Cases
Current 12 Readiness & Paper Design           → New 12
```

Do not leave filenames and module numbers mismatched after the refactor. When renaming occurs, update:

- README course links
- Docsify/sidebar/navigation configuration
- previous/next links
- all references such as "Module 06" inside prose
- relative Markdown links
- any module number embedded in examples or summaries

Preserve old public deep links with redirect/stub files if the maintainer decides existing external links are important.

---

# 3. Locked Course Decisions

These decisions are intentional and should not be reopened casually by future editing chats.

1. **Theory only.** No hands-on labs in this repository.
2. **Priya/Acme stays.** It is the main continuity device.
3. **Data/JSONPath moves before Triggers.** The learner should understand payload structure before being asked to reason deeply about trigger payloads and filters.
4. **Green Does Not Mean Done stays as a signature engineering principle.**
5. **Workflow is not automatically the right solution.** Tool-selection judgment is a core learning outcome.
6. **Technical accuracy outranks stylistic polish.**
7. **Strong existing prose should be preserved when it already works.**
8. **Core / Working Engineer / Advanced labels may be used to control cognitive load.**
9. **The mentor voice becomes less hand-holding as the learner progresses.**
10. **Official SailPoint documentation is the primary source for changing technical behavior.**

---

# 4. Course-Wide Seven-Question Engineering Framework

Introduce this briefly in Module 00 and fully develop it in Module 12.

1. **What actually starts this process?**
2. **What data arrives, and what is missing?**
3. **What decisions must be made?**
4. **What actions belong here?**
5. **What can fail, and how will failure be handled?**
6. **What happens if this runs twice or concurrently?**
7. **What evidence proves the intended business outcome?**

This framework should become the learner's internal workflow-design checklist.

---

# 5. Module-by-Module Improvement Requirements

## Module 00 — Orientation

### Preserve
- Acme/Priya introduction
- workflow mental model
- surrounding ISC tools
- theory-course framing

### Add
- course journey: understand → build → operate → engineer
- brief preview of the seven engineering questions
- explanation that Advanced sections are reference material, not first-pass memorization

### Correct/refine
- avoid saying transforms cannot make decisions at all
- teach the boundary more precisely: transforms calculate/shape values and may contain conditional/fallback logic, but do not orchestrate workflow actions and external process steps

### Knowledge boundary
The learner may know basic ISC identities/accounts/sources and basic JSON/REST concepts. Do not rely on workflow-specific JSONPath, trigger catalogs, approval architecture, or production debugging yet.

---

## Module 01 — The Workflow Model

### Preserve
- whole-workflow example before naming parts
- trigger/action/operator mental model
- forward-only data dependency
- builder vs underlying JSON concept

### Correct
- verify and correct the current Workflow JSON object model; the trigger placement must match the current workflow API/model

### Reduce/move
- detailed JSONPath explanation should become a preview only; Module 02 teaches it fully

### Add
- end Checkpoint stating what the learner should now recognize in any simple workflow

### Knowledge boundary
The learner understands the purpose of Workflows and nearby ISC tools. Do not rely on advanced filters, arrays, approval boundaries, idempotency, or production operations.

---

## Module 02 — Data, Payloads, Variables & JSONPath

### Source
Refactor current Module 06 rather than merely renumbering it.

### Required teaching order
1. plain JSON values
2. objects
3. nested objects
4. arrays
5. arrays of objects
6. workflow data growing step by step
7. simple JSONPath
8. array indexing and why positional assumptions are fragile
9. predicates/selections
10. missing vs null vs empty
11. Variable Selector
12. trigger-filter JSONPath vs workflow-step JSONPath

### Preserve
- actual payload examples
- array-order warning
- missing/null data discussion
- Jayway vs SailPoint JSON Slice distinction

### Add
- explicit conceptual diagram showing trigger data plus outputs from earlier steps
- strong Engineering Habit: inspect actual data rather than infer where a field should live

### Knowledge boundary
No assumption yet that the learner understands the full trigger catalog, loops, action success contracts, or approval architecture.

---

## Module 03 — Triggers & Filters

### Structural change
Split the catalog into **Core** and **Specialized/Advanced** triggers.

### Core triggers for first-pass mastery
- Identity Created
- Identity Attributes Changed
- Identity Lifecycle State Changed
- Scheduled Trigger
- Account Aggregation Completed
- Provisioning Completed

For each core trigger teach:

1. what business event it represents,
2. what data boundary it provides,
3. when it is a natural choice,
4. the common assumption that causes mistakes.

### Specialized/Advanced recognition
Keep existing coverage of items such as:

- Access Request Submitted
- Access Request Decision
- Form Submitted
- External Trigger
- Interactive Trigger
- Native Change triggers
- certification/campaign events
- Outlier Detected
- other specialized trigger families

The learner should recognize the event boundary without being expected to memorize the catalog.

### Preserve
- lifecycle state vs Identity Deleted distinction
- trigger-specific payload differences
- access request boundary reasoning
- Native Change boundary reasoning

### Knowledge boundary
The learner understands JSON payloads and paths. Do not assume formal knowledge of action error handling or full approval behavior until Modules 05–06.

---

## Module 04 — Operators & Logic

### Required progression
1. single comparison
2. branch
3. combine conditions
4. verify/guard data
5. shape data with variables
6. loops

### Add
- visible **Engineering Step-Up: Loops** section explaining that loops introduce ordering, scale, scope, concurrency, and partial-failure concerns

### Preserve
- Compare Strings/Numbers/Boolean/Timestamps
- Define Comparison
- Define/Update Variable
- Verify Data Type
- serial vs parallel loop distinctions
- execution-limit connection

### Review carefully
- exact operator capabilities and comparison semantics
- statements about case sensitivity or normalization must be documented or cautiously worded

---

## Module 05 — Actions & Error Handling

### Preserve
- notify/fetch/change/integrate/pause action-family mental model
- Get Identity
- Manage Access
- Manage Accounts
- HTTP Request
- Wait
- Green Does Not Mean Done
- async boundary reasoning

### Add major section
**When an Action Fails / Native Error Handling**

Teach:

- normal success path
- action error path
- what error information is available
- when fallback is reasonable
- when the correct design is to end in Failure
- technical failure vs valid business outcome

### Correct/refine
- do not say unnecessary Get Identity calls "spend another workflow execution" unless current documentation explicitly supports that metric; instead describe added service call, latency, data, and failure surface

### Preserve signature principle

```text
Workflow action succeeded
        ≠
Access request approved
        ≠
Provisioning completed
        ≠
Target state independently confirmed
```

### Review carefully
- Manage Access output semantics
- approval waiting behavior
- action-specific timeout values
- deprecated action replacements

---

## Module 06 — Forms, Approvals & Interactive Workflows

### Add decision map first

```text
Need information from a person?
  → Form family

Does submission start the workflow?
  → Form Submitted Trigger

Does a running workflow pause for a selected person?
  → Form Action

Does a user launch and interact with a delegated process?
  → Interactive Workflow

Need a governed yes/no decision?
  → Approval tooling
```

### Preserve
- Form Submitted vs Form Action distinction
- Interactive Process distinction
- Interactive Message vs Interactive Form
- Approval Policy vs Generic Approval Policy
- governed approval vs form-based imitation

### Review carefully
- current Adaptive Approval requirements
- reviewer categories
- Approve/Deny Access Request identifiers and UI/documentation naming issues

---

## Module 07 — Testing, Debugging & Execution

### Reorganize around five diagnostic questions

1. **Did the workflow start?**
2. **What data actually arrived?**
3. **Where did the first unexpected value appear?**
4. **What did that action actually guarantee?**
5. **Which system or process owned the next boundary?**

### Preserve
- simulated testing warning
- execution history
- rendered input/output inspection
- trigger filter failures
- JSONPath diagnosis
- Manage Access partial-result diagnosis
- Native Change diagnostics
- access-request boundary debugging

### Add/refine
- make the diagnostic procedure memorable and reusable rather than a list of unrelated troubleshooting tips

---

## Module 08 — Operations, Limits & Governance

### Preserve
- individual vs tenant execution limits
- loop-count distinction
- promotion/versioning
- tenant-specific references
- execution-history retention
- Parameter Storage
- naming/modularity/documentation/monitoring

### Add

#### Workflow ownership
Teach operational impact of ownership changes, creator departure, workflow-specific credentials/tokens where currently documented, and ownership reassignment.

#### Definition/input/payload size limits
Include current documented values, but teach the principle rather than forcing memorization.

#### Scheduled execution overlap
Explain that a new scheduled execution may begin before a prior one finishes when the schedule allows it, and connect this to idempotency and concurrency.

#### Production lifecycle

```text
Design
→ review
→ version/export
→ promote
→ enable
→ monitor
→ maintain
→ transfer ownership
→ retire
```

### Review carefully
Every numeric limit, retention period, and ownership-token statement must be verified against current official documentation.

---

## Module 09 — When to Use Workflows and When Not

### Add decision framework near the top

```text
Calculate/shape a value?
  → Transform

Determine standard automatic access?
  → Roles / Access Profiles / Lifecycle

Fulfill target account change?
  → Provisioning

Govern an access request?
  → Native request governance / Adaptive Approval

React to an event with orchestration?
  → Workflow

Need custom/high-volume/heavy processing?
  → External service/integration

No supported configurable feature fits?
  → Consider Rule
```

### Preserve
- anti-patterns
- birthright-by-workflow warning
- no-filter firehose
- bulk processor
- poller
- hard-coded secrets
- workflow-specific limits

### Correct/refine
Use precise transform wording; do not imply transforms cannot contain conditional logic.

---

## Module 10 — Real-World Workflow Patterns

### Structural change
Classify patterns by expected learner maturity.

#### Core
Examples:
- joiner notification
- mover notification
- leaver notification/ticketing
- aggregation-failure alert
- provisioning notification
- data-quality alert
- simple scheduled process
- simple HTTP integration
- basic manager form/intake

#### Working Engineer
Examples:
- Manage Access orchestration
- Manage Accounts
- Access Request Decision
- Adaptive Approval
- Interactive Workflows
- controlled loops
- ServiceNow/ticket integrations
- certification creation

#### Advanced
Examples:
- Native Change remediation
- Outlier response
- campaign lifecycle orchestration
- multi-workflow event chains
- durable correlation
- replay protection
- target verification strategies

### Preserve
Do not remove advanced content merely to simplify the course. The labels control cognitive load.

---

## Module 11 — Challenges, Failure Modes & Edge Cases

### Teaching-style change
Increase scenario-first reasoning.

Use:

```text
Scenario
→ learner question
→ reasoning
→ explanation
```

### Preserve
- loops and performance
- execution/rate limits
- race conditions
- partial failures
- retries
- idempotency
- duplicate side effects
- repeated alerts
- Native Change signal-vs-verdict
- Outlier signal-vs-verdict
- source capability gates

### Add
- scheduled-overlap scenario if not fully handled in Module 08

### Core recurring question

> If this happens twice, does the system still end in the correct state?

---

## Module 12 — Readiness & Paper Design

### Preserve
- paper-design concept
- worked scenarios
- readiness checklist

### Strengthen
Use the final seven-question engineering framework:

1. What actually starts this process?
2. What data arrives, and what is missing?
3. What decisions must be made?
4. What actions belong here?
5. What can fail, and how will failure be handled?
6. What happens if this runs twice or concurrently?
7. What evidence proves the intended business outcome?

### Tone
The mentor should increasingly step back. Do not immediately provide the answer. Ask the learner to identify the event, hidden assumption, success boundary, or replay problem first.

---

# 6. Required Review Sequence for Every Module

Do not jump directly from old content to final rewrite.

For every module use this sequence:

```text
1. Existing-module assessment
2. Proposed revised structure
3. Revised module draft
4. Independent ISC technical review
5. Independent beginner/teaching review
6. Apply only verified corrections and useful teaching improvements
7. Final acceptance
8. Update COURSE-STATUS.md
9. Move to the next module
```

---

# 7. Module Acceptance Criteria

A module is not final until all are true.

## Technical
- no known incorrect SailPoint claims
- current names and contracts verified where material
- no invented payload fields or guarantees
- supported vs inferred behavior clearly distinguished

## Learning
- learner prerequisites are respected
- concepts are not used before being taught without explicit preview framing
- cognitive load is appropriate to the module position
- examples reinforce the actual learning outcome

## Voice
- mentor-to-mentee feeling is present
- language sounds natural and human
- no unnecessary rewrite of good existing prose
- repeated rhetorical templates have been reduced

## Engineering outcome
- learner can perform the module's stated reasoning outcome
- Work It Out questions test understanding, not mere recall
- Checkpoint clearly states what the learner should now be able to do

---

# 8. Repository-Wide Final Audits

After all modules are individually accepted, run three full-course audits.

## Audit A — Technical Consistency
Check for contradictions across modules in:

- trigger names and payloads
- workflow object model
- JSONPath environments
- action success semantics
- approval and provisioning boundaries
- timeouts
- execution limits
- retention
- deprecated/current actions
- certification and Native Change behavior

## Audit B — Learning Continuity
Read 00 → 12 as a beginner and identify:

- concepts used before taught
- unnecessary repeated teaching
- abrupt difficulty spikes
- advanced material lacking labels
- weak transitions
- prerequisites that are assumed rather than taught

## Audit C — Teaching Voice
Read 00 → 12 as one long mentor/student conversation and identify:

- documentation-like sections
- sudden personality changes
- repeated stock phrases
- excessive dramatic emphasis
- unnatural AI-like patterns
- missed opportunities to expose engineering reasoning

Only after all three audits should the theory course be considered complete.
