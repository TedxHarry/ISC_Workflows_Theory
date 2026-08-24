# ISC Workflows Theory — Project Status

## Purpose

This file is the shared state for all ChatGPT course-refactor sessions.

Every new course-related ChatGPT session should read this file together with:

- `AUTHORING-GUIDE.md`
- `COURSE-IMPROVEMENT-PLAN.md`
- the role file assigned to that chat
- the current target module

Update this file only after a module reaches an agreed milestone.

---

# Working Branch

**All course-refactor reads and writes must use:** `course-theory-refactor`

The `main` branch is the protected/current course baseline. Do not modify student-facing course files on `main` during the refactor unless the maintainer explicitly decides to merge or apply completed work.

If a role uses a GitHub connector, it must explicitly read and write the `course-theory-refactor` branch rather than relying on the connector's default branch.

---

# Current Project State

**Phase:** Repository-wide structural cleanup complete; course-wide audits pending

**Current target:** None — Modules 00–12 are FINAL ACCEPTED

**Course modules modified so far:** Module 00 — Orientation (`FINAL ACCEPTED`); Module 01 — The Workflow Model (`FINAL ACCEPTED`); Module 02 — Data, Payloads, Variables & JSONPath (`FINAL ACCEPTED`); Module 03 — Triggers & Filters (`FINAL ACCEPTED`); Module 04 — Operators & Logic (`FINAL ACCEPTED`); Module 05 — Actions & Error Handling (`FINAL ACCEPTED`); Module 06 — Forms, Approvals & Interactive Workflows (`FINAL ACCEPTED`); Module 07 — Testing, Debugging & Execution (`FINAL ACCEPTED`); Module 08 — Operations, Limits & Governance (`FINAL ACCEPTED`); Module 09 — When to Use Workflows and When Not (`FINAL ACCEPTED`); Module 10 — Real-World Workflow Patterns (`FINAL ACCEPTED`); Module 11 — Challenges, Failure Modes & Edge Cases (`FINAL ACCEPTED`); Module 12 — Readiness & Paper Design (`FINAL ACCEPTED`)

**Repository-control files created:**

- `AUTHORING-GUIDE.md`
- `COURSE-IMPROVEMENT-PLAN.md`
- `COURSE-STATUS.md`
- role instructions under `chatgpt/`

Modules 00 through 12 are final accepted. The module-by-module refactor sequence and coordinated filename/navigation repair are complete. Course-wide technical, learner-continuity, teaching-voice, and reference consistency audits remain pending.

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
- [x] Refactor work occurs on `course-theory-refactor`, not directly on `main`.

---

# Planned Final Module Sequence

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

These findings came from the preliminary repository review. They are **review targets**, not permission to edit blindly. The Technical Reviewer must verify them against current official SailPoint sources before acceptance.

## Module 01 — Workflow JSON model

The existing JSON skeleton appeared to place `trigger` inside `definition`. Formal technical review found conflicting current official representations: the API/SDK model places `trigger` at the top level, while product-help material shows a JSON-file representation with `trigger` nested under `definition`.

**Status:** Resolved in the final accepted Module 01 by removing the exact universal hierarchy and teaching only the stable structured-Workflow-definition concept.

## Modules 00 / 09 — Transform wording

Existing language suggests transforms "do not make decisions." This is likely too absolute because supported transform operations can contain conditional/fallback logic. The intended architectural distinction is that transforms calculate/shape values and do not act as general workflow orchestration engines.

**Status:** Resolved in the final accepted Modules 00 and 09. Module 09 explicitly preserves supported conditional value logic while teaching the architectural boundary between attribute-value calculation/manipulation and event/process orchestration.

## Module 04 / future Module 05 — Get Identity execution wording

Existing language says an unnecessary Get Identity "spends an execution." Verify the relevant execution-count definition. Preliminary review suggests the safer point is that an unnecessary lookup adds a service call, latency, data, and another failure surface rather than necessarily counting as a separate workflow execution.

**Status:** Resolved in the final accepted Module 05 by removing the incorrect execution-count claim and teaching the safer action/service-call, latency, returned-data, and failure-surface boundary.

## Module 05 / future Module 06 — Human-in-the-loop mechanisms

Adaptive Approval, Approval Policy, Generic Approval Policy, Form action, Interactive Workflow, Approve/Deny Access Request, and identifier semantics require current-source verification during module review.

**Status:** Resolved in the final accepted Module 06 through current-source technical review, mechanism-specific non-response handling, current Interactive Process terminology, Adaptive Approvals boundaries, and verified direct Approve/Deny identifier semantics.

## Module 08 — Operations additions

Verify and add where current documentation supports them:

- workflow ownership and creator-departure consequences
- workflow-specific token/credential behavior
- definition/input/payload size limits
- scheduled execution overlap behavior
- current execution thresholds and retention

**Status:** Resolved in the final accepted Module 08 through current-source verification of ownership and Workflow PAT behavior, size limits, scheduled overlap, execution thresholds, retention boundaries, promotion/configuration-management behavior, and secure-credential scope.

---

# Module Workflow

Each module must progress through these states:

```text
NOT STARTED
→ ARCHITECT REVIEWED
→ STRUCTURE APPROVED
→ DRAFT REVISED
→ TECHNICALLY REVIEWED
→ TEACHING REVIEWED
→ FINAL ACCEPTED
```

The module should not be marked `FINAL ACCEPTED` merely because the prose was rewritten.

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

# Repository-Wide Work Still Pending

The module-by-module refactor sequence and structural navigation cleanup are complete. The remaining work is the course-wide audit and final integrity phase.

- [x] Renumber/rename module files 02–06
- [x] Update README navigation
- [x] Update previous/next links
- [x] Update Docsify/sidebar navigation where required
- [x] Repair cross-module number references
- [x] Decide whether old public deep links need redirect/stub files — preserved with moved-module stubs
- [ ] Add/update Official References sections and reconcile site-injected reference lists
- [ ] Run final technical consistency audit
- [ ] Run final beginner learning-continuity audit
- [ ] Run final teaching-voice audit

`index.html` module routing, ordering, display titles, and module-key mappings have been structurally updated. The student-facing `moduleHighlights` text and `officialReferences` contents were intentionally not substantively revised during structural cleanup and remain explicit specialist-audit targets.

---

# Handoff Rule

A role chat should not silently perform another role's approval.

- The **Course Architect** owns structure, sequencing, scope, and learner prerequisites.
- The **ISC Technical Reviewer** owns technical truth and current SailPoint verification.
- The **Mentor Teaching Editor** owns beginner experience, teaching voice, pacing, and prose refinement.

The maintainer remains the final decision-maker.
