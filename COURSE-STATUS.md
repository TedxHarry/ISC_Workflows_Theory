# ISC Workflows Theory: Project Status

## Purpose

This file is the shared state for all ChatGPT course-refactor sessions.

Every new course-related ChatGPT session should read this file together with:

- `AUTHORING-GUIDE.md`
- `COURSE-IMPROVEMENT-PLAN.md`
- the role file assigned to that chat
- the current target module, if any

Update this file when the project reaches an agreed milestone or a new course-maintenance phase begins.

---

# Repository State

**Current integrated course branch:** `main`

The completed `course-theory-refactor` branch was reviewed, approved, and merged into `main` through PR #10. It is retained as historical refactor state and is no longer the active course-working branch.

New course work should start from the current `main` baseline unless the maintainer explicitly creates or designates another working branch.

---

# Current Project State

**Phase:** COMPLETE - final course integration approved and merged to `main`

**Current target:** None - Modules 00–12 are FINAL ACCEPTED

**Course modules:** Module 00 - Orientation (`FINAL ACCEPTED`); Module 01 - The Workflow Model (`FINAL ACCEPTED`); Module 02 - Data, Payloads, Variables & JSONPath (`FINAL ACCEPTED`); Module 03 - Triggers & Filters (`FINAL ACCEPTED`); Module 04 - Operators & Logic (`FINAL ACCEPTED`); Module 05 - Actions & Error Handling (`FINAL ACCEPTED`); Module 06 - Forms, Approvals & Interactive Workflows (`FINAL ACCEPTED`); Module 07 - Testing, Debugging & Execution (`FINAL ACCEPTED`); Module 08 - Operations, Limits & Governance (`FINAL ACCEPTED`); Module 09 - When to Use Workflows and When Not (`FINAL ACCEPTED`); Module 10 - Real-World Workflow Patterns (`FINAL ACCEPTED`); Module 11 - Challenges, Failure Modes & Edge Cases (`FINAL ACCEPTED`); Module 12 - Readiness & Paper Design (`FINAL ACCEPTED`)

**Repository-control files:**

- `AUTHORING-GUIDE.md`
- `COURSE-IMPROVEMENT-PLAN.md`
- `COURSE-STATUS.md`
- role instructions under `chatgpt/`

Modules 00 through 12 are final accepted. The module-by-module refactor sequence, coordinated filename/navigation repair, full-course technical audit, learner-continuity audit, teaching-voice audit, Official References/site-consistency audit, final Course Lead repository-wide integrity review, and maintainer-authorized merge are complete.

No refactor-stage course-content, audit, integration, or merge work remains pending.

---

# Locked Decisions

Do not reopen these unless the maintainer explicitly changes them.

- [x] Theory course only; hands-on labs remain separate.
- [x] Keep the Priya/Acme continuity narrative.
- [x] Move Data/JSONPath before Triggers in the final structure.
- [x] Preserve "Green Does Not Mean Done" as a recurring engineering principle.
- [x] Teach Workflow as one ISC capability among several, not the default answer to every automation problem.
- [x] Use Core / Working Engineer / Advanced labels where they reduce cognitive load.
- [x] Use a personal mentor-to-mentee teaching voice.
- [x] Teaching voice should mature from guided beginner instruction toward junior-engineer reasoning.
- [x] Preserve strong existing prose; do not rewrite for novelty.
- [x] Technical accuracy takes priority over style.
- [x] Current official SailPoint sources are primary for changing technical behavior.
- [x] Final module sequence is defined in `COURSE-IMPROVEMENT-PLAN.md`.
- [x] Refactor work was completed on `course-theory-refactor` and merged into `main` only after maintainer approval.

---

# Final Module Sequence

```text
00 Orientation
01 The Workflow Model
02 Data, Payloads, Variables & JSONPath
03 Triggers & Filters
04 Operators & Logic
05 Actions & Error Handling
06 Forms, Approvals & Interactive Workflows
07 Testing, Debugging & Execution
08 Operations, Limits & Governance
09 When to Use Workflows and When Not
10 Real-World Workflow Patterns
11 Challenges, Failure Modes & Edge Cases
12 Readiness & Paper Design
```

---

# Initial Technical Findings Requiring Resolution

These findings came from the preliminary repository review. They are preserved here as project history; each was formally resolved before final acceptance.

## Module 01: Workflow JSON model

The existing JSON skeleton appeared to place `trigger` inside `definition`. Formal technical review found conflicting current official representations: the API/SDK model places `trigger` at the top level, while product-help material shows a JSON-file representation with `trigger` nested under `definition`.

**Status:** Resolved in the final accepted Module 01 by removing the exact universal hierarchy and teaching only the stable structured-Workflow-definition concept.

## Modules 00 / 09: Transform wording

Existing language suggested transforms "do not make decisions." This was too absolute because supported transform operations can contain conditional/fallback logic. The intended architectural distinction is that transforms calculate/shape values and do not act as general workflow orchestration engines.

**Status:** Resolved in the final accepted Modules 00 and 09. Module 09 explicitly preserves supported conditional value logic while teaching the architectural boundary between attribute-value calculation/manipulation and event/process orchestration.

## Module 04 / future Module 05: Get Identity execution wording

Existing language said an unnecessary Get Identity "spends an execution." Technical review established the safer point: an unnecessary lookup adds a service call, latency, data, and another failure surface rather than necessarily counting as a separate workflow execution.

**Status:** Resolved in the final accepted Module 05 by removing the incorrect execution-count claim and teaching the safer action/service-call, latency, returned-data, and failure-surface boundary.

## Module 05 / future Module 06: Human-in-the-loop mechanisms

Adaptive Approval, Approval Policy, Generic Approval Policy, Form action, Interactive Workflow, Approve/Deny Access Request, and identifier semantics required current-source verification during module review.

**Status:** Resolved in the final accepted Module 06 through current-source technical review, mechanism-specific non-response handling, current Interactive Process terminology, Adaptive Approvals boundaries, and verified direct Approve/Deny identifier semantics.

## Module 08: Operations additions

The review verified and incorporated, where supported by current documentation:

- workflow ownership and creator-departure consequences
- workflow-specific token/credential behavior
- definition/input/payload size limits
- scheduled execution overlap behavior
- current execution thresholds and retention

**Status:** Resolved in the final accepted Module 08 through current-source verification of ownership and Workflow PAT behavior, size limits, scheduled overlap, execution thresholds, retention boundaries, promotion/configuration-management behavior, and secure-credential scope.

---

# Module Workflow

Each module progressed through these states:

```text
NOT STARTED
→ ARCHITECT REVIEWED
→ STRUCTURE APPROVED
→ DRAFT REVISED
→ TECHNICALLY REVIEWED
→ TEACHING REVIEWED
→ FINAL ACCEPTED
```

A module was not marked `FINAL ACCEPTED` merely because its prose had been rewritten.

---

# Module Status Table

| Module | State | Notes |
|---|---|---|
| 00 Orientation | FINAL ACCEPTED | Maintainer approved; integration complete |
| 01 Workflow Model | FINAL ACCEPTED | Maintainer approved; integration complete |
| 02 Data / JSONPath | FINAL ACCEPTED | Maintainer approved; integration complete; canonical filename finalized |
| 03 Triggers & Filters | FINAL ACCEPTED | Maintainer approved; integration complete; canonical filename finalized |
| 04 Operators & Logic | FINAL ACCEPTED | Maintainer approved; integration complete; canonical filename finalized |
| 05 Actions & Error Handling | FINAL ACCEPTED | Maintainer approved; integration complete; canonical filename finalized |
| 06 Forms / Approvals / Interactive | FINAL ACCEPTED | Maintainer approved; integration complete; canonical filename finalized |
| 07 Testing / Debugging | FINAL ACCEPTED | Maintainer approved; integration complete |
| 08 Operations / Limits / Governance | FINAL ACCEPTED | Maintainer approved; integration complete |
| 09 When to Use Workflows | FINAL ACCEPTED | Maintainer approved; integration complete |
| 10 Real-World Patterns | FINAL ACCEPTED | Maintainer approved; integration complete |
| 11 Failure Modes / Edge Cases | FINAL ACCEPTED | Maintainer approved; integration complete |
| 12 Readiness / Paper Design | FINAL ACCEPTED | Maintainer approved; integration complete |

---

# Repository-Wide Completion Status

The module-by-module refactor sequence, structural navigation cleanup, course-wide audits, site/reference repair, final Course Lead integrity review, and merge to `main` are complete. No additional refactor-stage course-content repair is pending.

- [x] Renumber/rename module files 02–06
- [x] Update README navigation
- [x] Update previous/next links
- [x] Update Docsify/sidebar navigation where required
- [x] Repair cross-module number references
- [x] Preserve old public deep links with moved-module compatibility stubs
- [x] Add/update Official References sections and reconcile site-injected reference lists
- [x] Run final technical consistency audit
- [x] Run final beginner learning-continuity audit
- [x] Run final teaching-voice audit
- [x] Run final Official References / site-consistency audit
- [x] Run final Course Lead repository-wide integrity review
- [x] Record final integration approval
- [x] Merge `course-theory-refactor` into `main` through maintainer-authorized PR #10
- [x] Synchronize post-merge project status on `main`

`index.html` module routing, ordering, display titles, module-key mappings, student-facing highlights, and generated-reference behavior are reconciled with the final accepted course. Modules 02–12 use their authored Official References as the canonical displayed reference sections; Modules 00–01 retain generated references.

**Final project status:** COMPLETE. The accepted ISC Workflows Theory course is integrated on `main`. No refactor-stage action remains pending.

---

# Handoff Rule

A future course-maintenance chat should not silently perform another specialist role's approval.

- The **Course Architect** owns structure, sequencing, scope, and learner prerequisites.
- The **ISC Technical Reviewer** owns technical truth and current SailPoint verification.
- The **Mentor Teaching Editor** owns beginner experience, teaching voice, pacing, and prose refinement.

The maintainer remains the final decision-maker.
