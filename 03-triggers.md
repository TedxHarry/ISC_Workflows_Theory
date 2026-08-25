# Module 03: Triggers & Filters

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
5. What does this event prove - and what does it not prove?
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

# Core Triggers

The six triggers in this section are **Core for this course**.

That is a learning classification, not a claim about which triggers every SailPoint customer uses most.

We will use the same four questions for each one:

1. **Business event - what happened?**
2. **Data boundary - what starting information is available?**
3. **Natural choice - what kind of requirement maps here?**
4. **Common assumption - what nearby fact should you not infer?**

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

## Filters narrow the right trigger

You have now seen enough Core triggers to make the filter model practical.

Use this sequence:

```text
Business requirement
        ↓
Correct event boundary
        ↓
Trigger
        ↓
Should every event qualify?
     ↙        ↘
   yes         no
               ↓
             Filter
```

### Mover example

Acme cares specifically about Priya moving into Finance.

The event boundary is:

**Identity Attributes Changed**

The qualification condition is:

> the `changes` array contains a department change whose new value is Finance.

A supported filter pattern is:

```text
$.changes[?(@.attribute == "department" && @.newValue == "Finance")]
```

That filter decides whether the event qualifies.

It does **not** rewrite the trigger data so that the Workflow receives only the matching department node.

That distinction came from Module 02 and matters here:

```text
filtering
= qualify the event

transforming
= change the shape/content of the data
```

A trigger filter is doing the first.

### A filter is not operator logic

Suppose Acme wants every department-change event to start the Workflow, and then wants the running Workflow to take different paths for Finance and Marketing.

That is no longer primarily a trigger-filter problem.

That is in-Workflow decision logic.

Keep the boundary:

```text
PRE-START
Filter:
Should this event start the Workflow?

POST-START
Operator:
What should the running Workflow do?
```

Module 04 begins with that second question.

---

## When a Workflow does not start

Filters create an important diagnostic distinction.

If a **valid** filter does not match an event, that event does not qualify to start the Workflow.

There may therefore be no Workflow execution for that event to inspect.

That can feel “silent” if you only look at Workflow execution history, but be precise about what happened:

> the filter excluded the event.

That is different from an **invalid filter expression**.

Invalid syntax or unsupported expression construction should be corrected during validation/configuration rather than described as a mysterious runtime non-event.

For Module 03, keep this diagnostic seed:

```text
Workflow did not start
        ↓
Did the event actually happen?
        ↓
Did I choose the correct trigger?
        ↓
Did the filter match the real event data?
```

Module 07 will turn that into a full debugging method.

> **Engineering Habit:** When a filtered Workflow does not start, inspect the event boundary and real payload before rewriting downstream logic. Downstream logic never ran.

---

# Specialized / Working Engineer: recognize the boundary

You do not need equal-depth mastery of the entire trigger catalog.

The triggers in this section matter, but your first-pass goal is recognition:

> **What event family does this represent, and where would I go verify the exact contract when I need it?**

## Identity Lifecycle State Change Processed

A later boundary than Identity Lifecycle State Changed.

It represents completion of ISC lifecycle-state processing/evaluation of configured lifecycle actions.

It does not independently prove downstream target-state completion.

## Identity Deleted

Represents actual deletion of the ISC identity.

Do not treat deletion as interchangeable with a leaver lifecycle-state transition.

For a process whose business event is actual ISC identity deletion, this can be the relevant trigger.

## Scheduled Search

A separate scheduled-search boundary where a scheduled search completes and results are available.

Recognize it as different from a plain Scheduled Trigger.

You do not need the detailed result contract here.

## Account event families

ISC also has account-oriented Workflow triggers such as account created, updated, and deleted events.

Recognize that these are account boundaries, not identity-lifecycle synonyms.

Verify the exact event contract when the business requirement is account-specific.

## Access Request Submitted and Access Request Decision

These are native Workflow trigger boundaries.

For Module 03, keep only the lifecycle picture:

```text
Access Request Submitted
        ↓
request/approval processing
        ↓
Access Request Decision
        ↓
possible later provisioning
```

**Access Request Submitted** on the native Workflow surface participates in the configured Adaptive Approval Workflow boundary.

**Access Request Decision** represents the final approved-or-denied decision boundary; when multiple approvals are required, the native Workflow documentation describes it after the final decision.

Do not turn this section into approval architecture.

Module 06 owns:

- Adaptive Approval;
- Approval Policy;
- reviewer mechanics;
- request payload details.

And keep one product-surface warning:

> Native Workflow triggers and similarly named Developer Event Triggers are related product surfaces, not interchangeable contracts.

For this course's Workflow design, use the native Workflow contract.

## Form and interactive starting mechanisms

ISC includes form and interactive Workflow starting mechanisms.

Recognize them as human/interactive boundaries.

Module 06 will teach the human-in-the-loop architecture properly.

## External Trigger

**External Trigger** is for a third-party system explicitly initiating a native Workflow.

The business-event origin is outside ISC and is intentionally sent into the Workflow.

That is enough here.

Do not turn Module 03 into:

- OAuth setup;
- API endpoint memorization;
- client-secret handling;
- replay/idempotency design.

Those have later homes.

External Trigger is also not the same thing as subscribing an external service to SailPoint Developer Event Triggers.

Related capability area, different product surface and contract.

## Certification, campaign, machine-identity, source, and platform event families

These trigger families broaden Workflow beyond Priya's identity lifecycle.

For now:

- recognize the family;
- identify the business event you need;
- verify the current trigger contract when the requirement actually calls for it.

Do not memorize the catalog.

---

# Advanced: signals and feature-dependent events

Some Workflow triggers represent security or platform signals that require more context before action.

Your first-pass skill is recognition, not remediation design.

## Native Change

Native Change trigger families represent out-of-band account changes detected by Native Change Detection during the relevant aggregation processing.

Keep the distinction precise:

```text
detected change
≠
proof the change was malicious
≠
proof the change was unauthorized
```

The event tells you what ISC detected.

The business meaning requires separate judgment.

Native Change can also involve correlated or uncorrelated accounts, so do not assume every event has a usable identity subject.

Remediation and auto-revert design belong in Modules 10 and 11.

## Outlier, CIEM, CAEP, DAS, and other specialized security-signal families

These exist on current Workflow surfaces but can depend on product capability, configuration, licensing, source setup, or regional availability.

Your first-pass rule is:

> **Recognize the signal family. Verify prerequisites and the current contract when the requirement actually needs it.**

Do not memorize volatile prerequisite tables.

And carry the same engineering principle:

> **signal ≠ verdict**

An alert or detection tells you that a product condition was observed.

It does not automatically tell you the business intent or the correct remediation.

---

## Workflow triggers and Developer Event Triggers

One final boundary protects the model established in Module 00.

Native Workflow triggers and Developer Event Trigger subscriptions overlap in some event families.

They are not one interchangeable trigger catalog with one guaranteed contract, and this course will not teach an undocumented “Workflow is just another subscriber to the same underlying event service” model.

The safe mental model is:

```text
native Workflow trigger surface
and
Developer Event Trigger subscription surface

= related extensibility mechanisms
  with some overlap
  but non-identical catalogs/contracts
```

When you are designing a native Workflow, use the native Workflow trigger documentation as the contract for that Workflow surface.

---

## Work It Out: Choose the event boundary

For each scenario, answer five questions:

1. What actually happened?
2. Which trigger is the natural boundary?
3. What starting data would you inspect?
4. Would you consider a filter?
5. What nearby event or assumption would be wrong?

### Scenario 1: Priya first appears in ISC

Acme wants a notification after ISC detects and creates Priya's identity through authoritative processing.

<details>
<summary>Check your reasoning</summary>

**Natural trigger:** Identity Created.

**Why:** The business requirement is tied to ISC identity creation.

**Inspect:** The actual identity reference and configured attribute data supplied by the trigger.

**Filter:** Only if Acme wants to narrow which Identity Created events qualify.

**Do not assume:** This proves Priya is already active, fully provisioned, or ready on downstream systems.

</details>

### Scenario 2: Priya moves into Finance

Priya's authoritative department changes from Sales to Finance. Acme only wants the Workflow for moves into Finance.

<details>
<summary>Check your reasoning</summary>

**Natural trigger:** Identity Attributes Changed.

**Why:** The business event is an authoritative identity-attribute transition.

**Inspect:** The `changes` array and actual old/new values.

**Filter:** Yes, a department-to-Finance filter is natural because not every attribute change should qualify.

**Do not assume:** The department change is always the first array item.

</details>

### Scenario 3: Priya enters Acme's leaver state

Acme wants its leaver orchestration to begin when Priya's configured lifecycle state changes to its terminated state.

<details>
<summary>Check your reasoning</summary>

**Natural trigger:** Identity Lifecycle State Changed.

**Why:** The business event is the lifecycle-state transition.

**Inspect:** Identity reference plus old/new lifecycle state values.

**Filter:** Often yes if the Workflow should only run for a particular target state or transition, using the tenant's actual technical state name.

**Wrong nearby boundary:** Identity Deleted. Actual ISC identity deletion is a different later event.

</details>

### Scenario 4: Acme cares about an aggregation outcome

Acme wants follow-up orchestration after an account aggregation reaches its completion/outcome boundary, but only for outcomes that meet an operational condition Acme has explicitly verified.

<details>
<summary>Check your reasoning</summary>

**Natural trigger:** Account Aggregation Completed.

**Why:** The process cares about that source account-aggregation/account-collection boundary.

**Inspect:** Source, status, errors, warnings, statistics, and timing that are relevant to Acme's requirement.

**Filter:** Potentially, but only using a condition and value contract Acme has actually verified. Do not invent an exhaustive status enum or assume warnings equal failure.

**Do not assume:** This event proves all later identity processing has completed.

</details>

### Scenario 5: provisioning processing reaches its completion boundary

Acme wants a follow-up notification after provisioning processing reaches the Provisioning Completed boundary.

<details>
<summary>Check your reasoning</summary>

**Natural trigger:** Provisioning Completed.

**Why:** The business event is the provisioning-stage boundary.

**Inspect:** Errors, warnings, account request/result information, and the current runtime contract.

**Filter:** Possibly, but do not hard-code a result enum from memory because current official examples are inconsistent.

**Do not assume:** The intended downstream target state has been independently proven.

</details>

### Scenario 6: the event originates outside ISC

A separate HR application owns a business event that Acme wants to send explicitly into a native Workflow.

<details>
<summary>Check your reasoning</summary>

**Specialized trigger to evaluate:** External Trigger.

**Why:** The initiating event originates outside ISC and is deliberately sent into the Workflow.

**Inspect:** The actual dynamic input contract for that integration.

**Do not overlearn here:** Authentication, endpoint, replay protection, and identifier-mapping mechanics belong later.

**Do not confuse it with:** Developer Event Trigger subscriptions, where an external service subscribes to SailPoint events.

</details>

---

## Checkpoint

You should now be able to hear a business requirement and reason in this order:

```text
What actually happened?
        ↓
Which trigger represents that event boundary?
        ↓
What starting data does that trigger provide?
        ↓
Should every event qualify?
        ↓
If not, what filter narrows it?
        ↓
What does this event prove - and what remains unproven?
```

You should also be able to explain:

- why event correctness comes before payload convenience;
- why a filter cannot repair the wrong trigger;
- why a trigger filter is a pre-start gate rather than in-Workflow branching;
- why Identity Created is not the hiring instant or downstream-readiness proof;
- why Identity Lifecycle State Changed is not Identity Deleted;
- why Scheduled Trigger breaks the “every trigger supplies a person-shaped JSON payload” assumption;
- why Account Aggregation Completed is not proof that all downstream identity processing finished;
- why warnings, errors, status, and statistics are separate evidence;
- why Provisioning Completed is not independent proof of final target state;
- why native Workflow triggers and Developer Event Triggers should not be treated as one interchangeable contract surface.

If you can do that, you are ready for the next question.

The correct events are now entering the Workflow.

Module 04 asks:

> **Now that the Workflow has started, what decisions should it make with the data it has?**

That is where Operators & Logic begins.

---

## Official References

- [Workflow Triggers - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-triggers.html)
- [Building Workflows - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-build.html)
- [Identity Created - SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/identity-created/)
- [Identity Attributes Changed - SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/identity-attribute-changed/)
- [Filtering Events - SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/filtering-events/)
- [Account Aggregation Completed - SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/account-aggregation-completed/)
- [Provisioning Completed - SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/provisioning-completed/)

---

[← Previous: Module 02 Data, Payloads, Variables & JSONPath](02-data-variables-and-expressions.md) | [Course home](README.md) | [Next: Module 04 Operators & Logic →](04-operators-and-logic.md)
