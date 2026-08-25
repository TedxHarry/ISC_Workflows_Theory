# ISC Workflows Theory: Authoring Guide

## Purpose

This file is the writing, teaching, and technical standard for the entire **ISC Workflows Theory** course.

The course is designed to take a learner from beginner understanding to engineer-level workflow design thinking. It is a theory course. Hands-on labs are intentionally maintained separately and must not be added here.

The desired learner experience is personal: the reader should feel that an experienced SailPoint ISC engineer is teaching them one-to-one, explaining not only what a feature does, but how to think about it, what assumptions commonly fail, and how an engineer decides what to do next.

---

## 1. Teaching Voice

Write as an experienced ISC engineer teaching one learner personally.

The tone should be:

- clear
- calm
- technically confident
- approachable
- mentor-to-mentee
- conversational without becoming casual or chatty
- respectful of an intelligent beginner

The course should not read like:

- official product documentation
- a certification cram guide
- marketing copy
- a generated summary of SailPoint documentation
- a lecture delivered at the learner

Prefer language that guides attention and reasoning, for example:

- "Look at what the payload actually gave you."
- "Before adding another step, ask whether you already have the value you need."
- "If this were my workflow, this is the first thing I would verify."
- "The useful question is not only whether the step succeeded, but what that success actually proves."

Use these naturally, not as templates.

Do not use em dashes in course or project prose. Choose commas, colons, semicolons, parentheses, or ordinary hyphens according to the sentence instead.

---

## 2. Teach Reasoning, Not Memorization

The course should teach the learner how to reach an answer independently.

Whenever practical, explain:

1. what a beginner may reasonably assume,
2. why that assumption seems sensible,
3. what ISC actually guarantees or provides,
4. how an engineer reasons from the real behavior.

Example pattern:

> A successful Manage Access step can look like proof that the access is live. It is not. The useful question is: what boundary did this action actually complete? Request submission, approval, provisioning, and confirmed target state are different facts.

Do not ask the learner to memorize facts that are better looked up.

Explicitly distinguish between:

- concepts worth remembering,
- current implementation details worth verifying when needed.

Examples:

- Do not memorize every action timeout. Remember that timeouts are action-specific and verify the current value for the action you are using.
- Do not memorize every trigger field. Learn to inspect the real trigger payload.
- Do not memorize every JSONPath expression. Understand objects, arrays, paths, predicates, and the JSONPath environment you are using.

---

## 3. Progressive Mentoring

The teaching style should mature as the learner progresses.

### Early modules: 00–03

Provide more scaffolding.

- introduce one idea at a time
- explain unfamiliar terminology before relying on it
- tell the learner what they do not need to understand yet
- make the mental model more important than product catalog coverage

Useful language:

- "For now, notice only..."
- "You do not need the full syntax yet."
- "We will come back to that once the data model is familiar."

### Middle modules: 04–08

Move from explanation toward guided reasoning.

- ask the learner what they would inspect before giving the answer
- show engineering decision-making
- make success, error, data, and execution boundaries explicit

### Late modules: 09–12

Treat the learner increasingly like a junior engineer.

- present competing designs
- ask what assumption is hidden
- ask which boundary has actually been proven
- ask whether Workflow is the right ISC capability at all
- let the learner reason before revealing the explanation

The mentor should gradually step back as the learner becomes more capable.

---

## 4. Course-Wide Engineering Principles

These principles should recur naturally across modules and remain technically consistent.

### Inspect the actual payload

Do not guess where data should be. Read the actual trigger or action input/output.

### Event boundary matters

Choose the trigger that represents the business event you actually care about, not merely an event that happens nearby in time.

### Green does not mean done

A successful Workflow action proves only that action's documented success contract.

Keep these boundaries distinct when relevant:

```text
Workflow action succeeded
        ≠
Access request approved
        ≠
Provisioning completed
        ≠
Target state independently confirmed
```

### Validate data before depending on it

Presence, null, empty, and usable values are not automatically equivalent.

### Design for repetition

For side-effecting processes, ask:

> What happens if this runs twice or two executions overlap?

### Prefer the purpose-built ISC capability

Do not force requirements into Workflows when transforms, roles, access profiles, lifecycle states, provisioning, request governance, or another supported capability owns the problem more naturally.

### Distinguish signal from verdict

Events such as Native Change or Outlier Detection provide evidence or risk signals. Do not automatically infer intent, authorization, maliciousness, or business correctness from the event alone.

---

## 5. Technical Accuracy Standard

Every material SailPoint claim must be technically defensible.

When editing or reviewing a module:

- verify changing behavior against current official SailPoint Documentation and SailPoint Developer documentation
- use exact current trigger, action, operator, and feature names
- verify payload shapes before teaching a JSONPath against them
- verify workflow object-model placement and property names
- verify action success semantics
- verify whether behavior is synchronous or asynchronous
- verify execution-stage boundaries
- verify current limits and timeouts when numbers are stated
- identify deprecated actions or features
- distinguish documented behavior from inference, tenant observation, workaround, or community report
- do not invent APIs, fields, output properties, actions, filters, or guarantees

If official SailPoint sources conflict, state the conflict or teach the safer invariant rather than silently choosing one source.

Community observations may be used when official material does not settle a behavior, but they must be presented as observations, not documented guarantees.

---

## 6. Learning Design Standard

Every module must have one clear learner outcome.

Before editing a module, answer:

> What should the learner be able to reason about or explain after this module that they could not before it?

A module should not introduce later-course complexity merely because it is related to the topic.

Use a **knowledge boundary** for every module:

- what the learner already knows,
- what this module teaches,
- what should remain a preview for later.

Avoid using concepts before they are taught. If a later concept must be mentioned, frame it explicitly as a preview.

---

## 7. Difficulty Labels

Use difficulty labels where they reduce cognitive load.

Recommended levels:

- **Core**: expected first-pass understanding
- **Working Engineer**: important after the core model is comfortable
- **Advanced**: recognize the design problem and return when needed

Do not use labels as decoration. Use them when a learner could otherwise mistake reference material for required beginner memorization.

---

## 8. Recurring Teaching Devices

Use these selectively. They should support the lesson rather than create a rigid template.

### Common Assumption

Use for a reasonable beginner belief that needs correction.

### Engineering Habit

Use for a behavior worth carrying into day-to-day engineering work.

### Work It Out

Use for active reasoning before revealing the explanation.

Questions should progress from simple understanding in early modules to design judgment in later modules.

### Checkpoint

Every module should end with a concise statement of what the learner should now be able to do.

Example:

> **Checkpoint:** You should now be able to hear "someone moved departments" and explain why Identity Attributes Changed is a more natural starting point than Identity Created.

---

## 9. Priya and Acme Continuity

Keep the existing Acme/Priya narrative.

Use it to connect concepts across the learner journey:

```text
Priya joins
  → identity event
  → notification / access context

Priya moves
  → attribute transition
  → manager / department / governance context

Priya leaves
  → lifecycle transition
  → offboarding / target-state context

Something fails
  → execution debugging

A process repeats
  → idempotency / concurrency

An auditor asks for evidence
  → distinguish workflow status from business outcome
```

Do not force Priya into examples where another scenario would be clearer.

---

## 10. Real-Engineer Commentary

Occasional practical observations improve the mentor feel.

Examples:

- "If I inherit a workflow I did not build, execution history is usually where I start before changing the canvas."
- "When a comparison unexpectedly stops matching, inspect the rendered values before rewriting the logic."
- "If the trigger already contains the value, another lookup adds latency and another place for the process to fail."

Use sparingly. Two or three genuine observations are stronger than commentary in every section.

---

## 11. Language and Style Guardrails

Prefer cohesive prose and concrete examples.

Avoid repeated reliance on stock phrases such as:

- "Here is the..."
- "The important thing..."
- "The biggest trap..."
- "Let us slow down..."
- "This is the most important..."
- "The honest..."
- "Remember..."

These phrases are not banned. Repetition is the problem.

Reserve strong emphasis for genuinely foundational lessons.

Do not call every fact critical, surprising, a trap, or something to burn into memory.

Avoid unnecessary rhetorical drama.

Avoid artificial friendliness or praise.

Do not use contractions if the established course voice does not use them consistently.

---

## 12. Preserve Strong Existing Material

Do not rewrite prose merely to make it different.

Preserve existing language when it is:

- technically accurate,
- pedagogically effective,
- natural,
- consistent with the course voice.

Change content only when there is a clear technical, structural, learning, consistency, or language reason.

The goal is to improve the existing course, not erase its identity.

---

## 13. Official References

Use official references without turning the lesson into documentation.

Prefer a concise **Official References** section at the bottom of a module for general supporting material.

Place a source closer to a statement when:

- the behavior is unusually specific,
- the behavior is likely to change,
- documentation conflicts,
- the distinction is important to the design.

Official sources should support the teaching, not interrupt it.

---

## 14. Theory Scope

This repository is the **theory and engineering-design course**.

Do not add hands-on lab exercises, tenant setup instructions, click-by-click build labs, or lab verification steps. Those belong to the separate practical course.

Theory exercises may ask the learner to reason about payloads, designs, execution histories, failure cases, and architecture on paper.

## Reading-unit structure

The course keeps **13 conceptual modules, numbered 00 through 12**. Longer modules may be divided into numbered reading units such as `10.1`, `10.2`, and `10.3` when there is a genuine learner stopping point.

- Keep the conceptual module landing page and repository path stable.
- Split at an existing conceptual boundary rather than an arbitrary word count.
- Preserve the full teaching and technical substance unless a separate content revision is approved.
- Keep first-pass navigation linear across reading units.
- Use the module landing page for cross-module references such as “Module 10.”
- Do not split a short module merely to make the file structure symmetrical.
