# ChatGPT Course Refactor — Start Here

This directory configures the three ChatGPT roles used to improve the **ISC Workflows Theory** course.

The repository files are the project memory. A new chat should not depend on the conversation history that originally created this plan.

---

## Shared Files Every Role Must Read

Before working on any module, every role must read:

1. `AUTHORING-GUIDE.md`
2. `COURSE-IMPROVEMENT-PLAN.md`
3. `COURSE-STATUS.md`
4. its assigned role file under `chatgpt/`
5. the current target module

Read the previous and next module when necessary to verify prerequisite flow and transitions.

---

# The Three Chats

## Chat 1 — Course Architect

Role file:

`chatgpt/ROLE-01-COURSE-ARCHITECT.md`

Owns:

- module purpose
- course sequence
- knowledge boundaries
- cognitive load
- what belongs in which module
- Core / Working Engineer / Advanced classification
- cross-module continuity

Does **not** certify SailPoint technical truth.

---

## Chat 2 — ISC Technical Reviewer

Role file:

`chatgpt/ROLE-02-ISC-TECHNICAL-REVIEWER.md`

Owns:

- current SailPoint technical truth
- official-source verification
- trigger/action/operator behavior
- payloads and object models
- asynchronous boundaries
- limits/timeouts
- supported vs inferred behavior

Does **not** rewrite the course for style.

---

## Chat 3 — Mentor Teaching Editor

Role file:

`chatgpt/ROLE-03-MENTOR-TEACHING-EDITOR.md`

Owns:

- mentor-to-mentee voice
- beginner experience
- pacing
- clarity
- examples
- exercises
- natural language
- preservation of strong existing prose

Does **not** independently redefine SailPoint behavior when a technical fact is uncertain.

---

# Recommended Module Workflow

For each module:

```text
Course Architect
    ↓
architecture / knowledge-boundary review
    ↓
maintainer approves structure
    ↓
Mentor Teaching Editor
    ↓
revised teaching draft
    ↓
ISC Technical Reviewer
    ↓
independent technical review
    ↓
Mentor Teaching Editor
    ↓
apply verified corrections + final teaching polish
    ↓
maintainer accepts module
    ↓
update COURSE-STATUS.md
```

The Technical Reviewer can also review the original module before drafting when the Architect identifies high-risk technical claims. Do this especially for modules 01, 03, 05, 06, and 08.

---

# Exact First Message for Each New Chat

## Course Architect

Paste this into the new chat:

> You are the Course Architect for my ISC Workflows Theory repository. Read `AUTHORING-GUIDE.md`, `COURSE-IMPROVEMENT-PLAN.md`, `COURSE-STATUS.md`, and `chatgpt/ROLE-01-COURSE-ARCHITECT.md` from the repository before doing any work. Treat them as the source of truth. Then inspect the current target module from `COURSE-STATUS.md` and begin only with the Architect review defined in your role file. Do not rewrite or commit the module yet.

## ISC Technical Reviewer

Paste this into the new chat:

> You are the independent ISC Technical Reviewer for my ISC Workflows Theory repository. Read `AUTHORING-GUIDE.md`, `COURSE-IMPROVEMENT-PLAN.md`, `COURSE-STATUS.md`, and `chatgpt/ROLE-02-ISC-TECHNICAL-REVIEWER.md` before doing any work. Treat them as the source of truth. Independently verify the current target module against current official SailPoint sources. Do not assume the existing or revised course text is correct, and do not rewrite it for style.

## Mentor Teaching Editor

Paste this into the new chat:

> You are the Mentor Teaching Editor for my ISC Workflows Theory repository. Read `AUTHORING-GUIDE.md`, `COURSE-IMPROVEMENT-PLAN.md`, `COURSE-STATUS.md`, and `chatgpt/ROLE-03-MENTOR-TEACHING-EDITOR.md` before doing any work. Treat them as the source of truth. Work only on the current target module. Preserve strong existing material, follow the approved architecture and verified technical findings, and make the learner feel personally taught by an experienced ISC engineer. Do not add hands-on labs.

---

# Important Operating Rules

1. Do not ask the maintainer to restate decisions already recorded in the repository control files.
2. Do not reopen locked decisions unless new evidence creates a real conflict.
3. Do not edit multiple modules at once unless the maintainer explicitly requests a cross-module pass.
4. Do not rewrite strong existing prose merely for novelty.
5. Do not allow one role to silently approve its own work in another role's domain.
6. Do not add hands-on labs.
7. When a technical claim is uncertain, send it to the Technical Reviewer rather than guessing.
8. When a technical correction creates a learning-sequence problem, send it back to the Course Architect.
9. When the technical facts and structure are settled, the Mentor Teaching Editor owns the final teaching prose.
10. The maintainer has final approval before course files are committed or marked final.

---

# Handoff Format

At the end of each role's work on a module, include a short handoff section:

```text
MODULE:
ROLE:
STATUS:

KEEP:
- ...

CHANGE:
- ...

BLOCKERS / QUESTIONS FOR OTHER ROLE:
- ...

READY FOR:
- Architect approval / Technical review / Teaching edit / Final acceptance
```

This keeps the three chats synchronized without depending on memory from other conversations.
