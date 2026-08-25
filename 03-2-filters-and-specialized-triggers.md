# Module 03.2: Filters & Specialized Triggers
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

## Specialized / Working Engineer: recognize the boundary

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

## Advanced: signals and feature-dependent events

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
What does this event prove, and what remains unproven?
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

[← Previous: Module 03.1: Choosing the Right Trigger](03-1-choosing-the-right-trigger.md) | [Course home](README.md) | [Next: Module 04: Operators & Logic →](04-operators-and-logic.md)
