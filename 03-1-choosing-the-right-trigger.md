# Module 03.1: Choosing the Right Trigger
How to choose the event that should start a Workflow, understand the data boundary that event provides, and narrow the right events before execution begins.

Module 02 taught you how to inspect Workflow data.

You can now look at a payload and ask:

> **What shape is this, where is the value I need, and how do I reference it?**

That gives us the next engineering question:

> **Did I choose the right event in the first place?**

A perfectly written JSONPath does not rescue a Workflow that starts at the wrong business moment.

That is what this module is about.

---

## Trigger selection starts with the event boundary

A **trigger** establishes the starting boundary for a Workflow.

There is exactly one trigger per Workflow.

The important word here is **boundary**.

An **event boundary** is the specific product or business moment the Workflow is reacting to.

Nearby events can sound similar while representing different facts:

```text
identity created
≠
identity attribute changed
≠
lifecycle state changed
≠
identity deleted
```

And:

```text
access request submitted
≠
access request decided
≠
provisioning completed
```

Those distinctions are not naming trivia.

They determine when the Workflow can start, what data is available at that point, and what facts are still unproven.

### Event correctness comes before payload convenience

A tempting design shortcut is:

> “Which trigger gives me the most useful data?”

That is the second question, not the first.

Use this order instead:

```text
1. What business event actually matters?
2. Which Workflow trigger most directly represents that event?
3. What starting data does that trigger provide?
4. Does a filter need to narrow which events qualify?
5. What does this event prove, and what does it not prove?
```

If the correct trigger does not contain every value you eventually need, that is a later design problem.

Choosing the wrong event because its payload is convenient gives you a cleaner implementation of the wrong process.

> **Engineering Habit:** Choose the event boundary first. Inspect the data boundary second.

---

## Trigger versus filter

A trigger and a filter answer different questions.

```text
TRIGGER
Which event family may start this Workflow?

FILTER
Which events inside that family qualify?
```

Suppose Acme cares about identity-attribute changes.

That event family may be correct.

But Acme does not want a Workflow execution for every attribute change. It only cares when the department changes to Finance.

The trigger answers:

> “Is this an Identity Attributes Changed event?”

The filter answers:

> “Is this one of the Identity Attributes Changed events I actually care about?”

That gives you another important rule:

```text
wrong trigger + clever filter
≠
correct event boundary
```

A filter narrows the right event family.

It is not a repair mechanism for choosing the wrong trigger.

### Filters qualify events before execution

For supported event triggers, a trigger filter evaluates event data before the event qualifies to start the Workflow.

That is different from an operator inside a running Workflow.

```text
trigger filter
= should this event start the Workflow?

operator logic
= now that the Workflow started, what path should it take?
```

Module 04 will teach the second question.

This module stays with the first.

---

## Core Triggers

The six triggers in this section are **Core for this course**.

That is a learning classification, not a claim about which triggers every SailPoint customer uses most.

We will use the same four questions for each one:

1. **Business event: what happened?**
2. **Data boundary: what starting information is available?**
3. **Natural choice: what kind of requirement maps here?**
4. **Common assumption: what nearby fact should you not infer?**

The repetition is deliberate. I want you learning a selection method, not six disconnected definitions.

---

## Identity Created: Priya appears in ISC

### 1. Business event: what happened?

**Identity Created** represents the point where ISC detects and creates a new identity during the relevant authoritative-source aggregation and refresh processing.

That is the product boundary.

Priya being hired by Acme is the business story around it, but the trigger is not the literal instant somebody in HR changes her employment status.

Think:

```text
authoritative processing
        ↓
ISC detects a new identity
        ↓
Identity Created
```

### 2. Data boundary: what starting information is available?

The event provides an identity reference and identity-profile attribute data.

You already know from Module 02 how to inspect that structure.

The important design habit here is not to assume that every value your future steps need is present and usable.

Inspect the actual trigger input.

### 3. Natural choice: what kind of requirement maps here?

Identity Created is a natural starting boundary when the process really cares that ISC has now created the identity.

Examples might include:

- sending an appropriate identity-created notification;
- opening a follow-up process tied to that ISC identity-creation boundary;
- starting orchestration that should occur after the identity is detected in ISC.

The key phrase is:

> **after ISC creates the identity**

not:

> **the instant Acme hires the person**

### 4. Common assumption: what should you not infer?

Do not infer that Identity Created proves Priya is:

- already in the lifecycle state your business process wants;
- fully provisioned;
- ready on every downstream target;
- at the exact HR employment-start instant.

Identity creation proves the identity-creation boundary.

Nothing more should be smuggled into the word *created*.

> **Common Assumption:** “Identity Created means the joiner is completely ready.”
>
> **Correction:** It means ISC created the identity at that processing boundary. Readiness and downstream fulfillment are separate facts.

---

## Identity Attributes Changed: Priya moves

Months later, Priya moves from Sales to Finance.

Module 02 already used this event's `changes` array to teach arrays, indexes, and predicates.

Now we care about **why this trigger is the right boundary**.

### 1. Business event: what happened?

**Identity Attributes Changed** represents authoritative identity attributes changing during identity refresh.

For Priya, the department may change from:

```text
Sales
→
Finance
```

The event can contain more than one changed attribute.

### 2. Data boundary: what starting information is available?

The event includes:

- an identity reference;
- a `changes` array;
- change objects containing fields such as:
  - `attribute`
  - `oldValue`
  - `newValue`

You already know not to assume the business-relevant change is always `changes[0]`.

### 3. Natural choice: what kind of requirement maps here?

This is a natural starting point when the business requirement is genuinely about an identity-attribute transition.

For example:

> Acme wants a Workflow when an identity's department changes to Finance.

The event boundary is the attribute change itself.

### 4. Common assumption: what should you not infer?

Do not assume:

- every attribute change should start the Workflow;
- the department change is always the first array item;
- a lifecycle-state edge case is automatically represented exactly like every other attribute change.

A filter is often useful because the trigger family can be broader than the business requirement.

For Acme's Finance mover case, a supported trigger-filter pattern is:

```text
$.changes[?(@.attribute == "department" && @.newValue == "Finance")]
```

Read the reasoning before the syntax:

```text
Event family:
Identity Attributes Changed

Qualifying event:
one whose changes include department → Finance
```

Module 02 already taught why this trigger-filter context uses the event payload directly rather than the running Workflow's `$.trigger` root.

### Working Engineer note

SailPoint documents an edge case around lifecycle-state change from `null` to `active` that should not be treated as a normal Identity Attributes Changed joiner transition.

You do not need to memorize that exception here.

The lesson is:

> Nearby product events can have boundary-specific rules. When a requirement depends on an exact lifecycle transition, verify the trigger contract rather than assuming “an attribute changed” covers every case.

---

## Identity Lifecycle State Changed: Priya leaves

Acme's leaver process gives us one of the clearest examples of why event boundaries matter.

### 1. Business event: what happened?

**Identity Lifecycle State Changed** represents the identity's `cloudLifecycleState` changing.

For a leaver design, Acme might have a configured state transition such as:

```text
active
→
terminated
```

Those values are examples.

Lifecycle-state technical names are tenant-configurable and case-sensitive, so do not memorize Acme's sample values as a product-wide enum.

### 2. Data boundary: what starting information is available?

The current Workflow event boundary provides data including:

- the identity reference;
- `oldLifecycleState`;
- `newLifecycleState`.

That makes the before/after state transition directly relevant to the Workflow.

### 3. Natural choice: what kind of requirement maps here?

This is a natural choice when the process truly cares about the identity entering or leaving a configured lifecycle state.

For example:

> Acme wants its leaver orchestration to begin when Priya transitions into Acme's terminated lifecycle state.

The important boundary is the lifecycle transition.

### 4. Common assumption: what should you not infer?

Do not confuse:

```text
Identity Lifecycle State Changed
```

with:

```text
Identity Deleted
```

They are different events.

The lifecycle-state transition is about state changing on an existing ISC identity.

Identity Deleted is the later event where the ISC identity itself is actually deleted under ISC deletion criteria.

For employment/leaver orchestration, the lifecycle-state change is usually the more direct business boundary when termination is represented by that configured state transition.

Identity Deleted may still be useful for requirements where actual ISC identity deletion is the event you care about.

That is implementation guidance based on event meaning, not a product law saying Identity Deleted is “only for housekeeping.”

### Do not confuse Changed with Processed

There is also a separate specialized trigger:

**Identity Lifecycle State Change Processed**

That is a later lifecycle-processing boundary: ISC has evaluated and applied the configured lifecycle-state actions for that lifecycle change.

Keep the wording narrow.

It does **not** independently prove that every downstream target-system change completed successfully.

You will see that distinction repeatedly in this course:

> **A completion word only proves the boundary it actually describes.**

---

## Scheduled Trigger: the clock is the boundary

Not every Workflow starts because something happened to Priya.

### 1. Business event: what happened?

With **Scheduled Trigger**, the start condition is the configured schedule.

The clock is the boundary.

Examples include:

- daily;
- weekly;
- monthly;
- yearly;
- CRON-based scheduling.

### 2. Data boundary: what starting information is available?

This trigger is a useful counterexample to the idea that every trigger supplies JSON event data.

SailPoint documents Scheduled Trigger input as a CRON expression rather than JSON.

There is no inherent identity, account, access request, or other business-event subject supplied merely because the Workflow started on a schedule.

### 3. Natural choice: what kind of requirement maps here?

Scheduled Trigger is a natural choice when the business requirement is periodic rather than event-subject-driven.

For example:

- a scheduled report;
- a recurring data-quality process;
- a periodic evidence or maintenance Workflow.

If later processing needs identities, accounts, or other subjects, the Workflow design has to obtain the information it needs.

### 4. Common assumption: what should you not infer?

Do not assume:

> “Every Workflow begins with a JSON payload describing a person or event.”

Scheduled Trigger proves otherwise.

Also do not assume scheduled executions are automatically serialized. SailPoint documents that a later scheduled execution can begin before an earlier one finishes.

You do not need the concurrency consequences yet.

Module 08 and Module 11 will handle that engineering problem.

For now, simply avoid designing with an unstated assumption that “the previous scheduled run must be finished.”

---

## Account Aggregation Completed: an operational event boundary

Priya is useful, but Workflows are not limited to identity lifecycle stories.

This trigger moves us into ISC operations.

### 1. Business event: what happened?

**Account Aggregation Completed** represents an account aggregation/account-collection boundary for a source operation.

The event can represent different aggregation outcomes.

Do not read the word *Completed* as:

> “Every piece of identity processing caused by this aggregation is now finished.”

That is broader than the documented boundary.

### 2. Data boundary: what starting information is available?

Current Workflow data for this event includes evidence such as:

- source information;
- `status`;
- start/completion timing;
- `errors`;
- `warnings`;
- `stats`.

Those are separate pieces of evidence.

Do not collapse them into one imaginary boolean called:

```text
aggregationGood = true/false
```

SailPoint's own examples can show a successful status alongside warnings.

### 3. Natural choice: what kind of requirement maps here?

This trigger is a natural choice when the business process genuinely cares that the account aggregation operation reached this boundary.

Examples might include:

- operational notification;
- follow-up orchestration tied to completion of account collection;
- evidence collection about the aggregation outcome.

This broadens your trigger thinking beyond joiner/mover/leaver.

### 4. Common assumption: what should you not infer?

There are three common mistakes.

First:

> “Aggregation Completed means all later identity refresh or recalculation work is done.”

No. Keep the event scoped to its aggregation/account-collection boundary.

Second:

> “Any warning means the aggregation failed.”

No. `status`, `errors`, `warnings`, and `stats` are separate signals.

Third:

> “I can memorize the complete set of status values and write a universal anything-except-success filter.”

Do not do that here.

Current official SailPoint sources are not consistent enough to make an exhaustive status enum a good beginner lesson.

The engineering habit is stronger:

> Inspect the actual trigger data and current contract before building outcome filters.

### Filtering an aggregation event

A filter can be useful when Acme does not want every aggregation event to start the Workflow.

But this module deliberately does **not** teach a universal:

```text
status != "Success"
```

style rule.

Why?

Because the business requirement may care about a particular status, warning, error, or statistic, and the documented outcome/status vocabulary has current inconsistencies.

Build the condition from evidence you have actually verified.

That is better engineering than memorizing an enum that may not be the contract you are running against.

---

## Provisioning Completed: a later processing boundary

The final Core trigger teaches a distinction that will matter throughout the rest of the course.

### 1. Business event: what happened?

**Provisioning Completed** represents a provisioning action reaching the Provisioning Completed event boundary on a source.

It is not limited to one access-request scenario. Provisioning can arise from multiple ISC processes.

### 2. Data boundary: what starting information is available?

The event can provide provisioning context including:

- errors;
- warnings;
- account-request information;
- per-account result information.

That data is evidence about the provisioning process.

Inspect it.

Do not reduce the trigger name to:

```text
everything succeeded
```

### 3. Natural choice: what kind of requirement maps here?

This is a natural trigger when the Workflow genuinely needs to react at the provisioning-processing boundary.

For example:

> after provisioning processing reaches this event boundary, Acme wants to run follow-up orchestration or notification.

The exact follow-up design belongs later.

### 4. Common assumption: what should you not infer?

Do not infer:

> “Provisioning Completed means the intended target state has been independently proven.”

The event is a provisioning-processing boundary.

Independent confirmation that the target account or access is exactly as the business intended is a separate question.

Also avoid memorizing a fixed `provisioningResult` enum.

Current official SailPoint sources show inconsistent result-value examples.

The right engineering habit is:

> inspect the actual Provisioning Completed input and current contract before writing result-value filters.

This is an early form of a principle we will develop later:

> **execution/process completion and proven business outcome are not automatically the same fact.**

---

## Put the six Core triggers side by side

The point is not to memorize six definitions.

It is to see six different boundaries.

| Trigger | Boundary to think about |
|---|---|
| Identity Created | ISC created a new identity during authoritative processing |
| Identity Attributes Changed | authoritative identity attributes changed during refresh |
| Identity Lifecycle State Changed | the identity's lifecycle state changed |
| Scheduled Trigger | the configured schedule condition occurred |
| Account Aggregation Completed | the account aggregation/account-collection operation reached its completion/outcome boundary |
| Provisioning Completed | provisioning processing reached the Provisioning Completed boundary |

Notice what is absent from that table:

- “best payload”
- “most convenient fields”
- “sounds closest to my requirement”

Start with the event.

Then inspect the data.

---

---

[← Previous: Module 02.2: Variables & JSONPath](02-2-variables-and-jsonpath.md) | [Course home](README.md) | [Next: Module 03.2: Filters & Specialized Triggers →](03-2-filters-and-specialized-triggers.md)
