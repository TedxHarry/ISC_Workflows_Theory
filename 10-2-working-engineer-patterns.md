# Module 10.2: Working Engineer Patterns
## Part II: Working Engineer Patterns

## 14. Working Engineer: Manage Access orchestration

Sometimes Workflow deliberately initiates an access change.

That does not change the ownership boundary you learned earlier.

### Pattern anatomy

```text
PURPOSE
Submit a supported access change as part of a larger orchestration.

EVENT
The business event that justifies the access operation.

CONTEXT
Identity and access object references required by the action.

DECISION
Is this change actually authorized and appropriate here?

WORK
Manage Access.

BOUNDARY
The access request was submitted/processed
according to the action's result boundary.

RISK
Treating action success as proof that target access is live.
```

### Green Does Not Mean Granted

This is the central lesson.

Manage Access can successfully submit work while later approval or provisioning still remains.

So:

```text
Manage Access green
        ≠
access live on target
```

Inspect the action's result outputs.

Understand what was accepted and what failed.

Then ask which later process owns the next fact.

Do not stretch the action's success boundary because the business wants a stronger answer.

---

## 15. Working Engineer: Manage Accounts orchestration

A Workflow may deliberately perform a supported account operation.

### Pattern anatomy

```text
PURPOSE
Coordinate an account-state operation
inside a justified orchestration.

EVENT
Business/security/lifecycle event that justifies the action.

CONTEXT
Exact account references and source context.

DECISION
Which accounts should be acted on?
Does the target/source support the required operation?

WORK
Manage Accounts.

BOUNDARY
Inspect successful, failed, and error results.

RISK
Partial results and unsupported target capabilities.
```

Do not assume:

```text
account exists in ISC
        ↓
every account operation is supported
```

Discovery and capability are different questions.

For the real target, verify that the source and connector configuration support the operation you intend to perform.

### Partial-result thinking

A multi-account action can produce a mixed result.

That means the engineering question is not merely:

> Is the step green?

Ask:

```text
Which accounts succeeded?
Which failed?
What error detail exists?
What state matters next?
```

That is Working Engineer reasoning.

---

## 16. Working Engineer: Access Request Decision reaction

Sometimes you do not own the approval process.

You only need to react to its result.

### Pattern anatomy

```text
PURPOSE
Orchestrate work after the governed request
reaches its decision boundary.

EVENT
Access Request Decision

CONTEXT
Request, requester/recipient, requested-item status
and decision-related context.

DECISION
Was the governed outcome approved or denied?
What surrounding action is appropriate?

WORK
Notify / record / initiate bounded downstream work.

BOUNDARY
The Workflow reacted to the final decision event.

RISK
Confusing approval with provisioning or target completion.
```

Conceptually:

```text
Access Request Decision
        |
        +---- approved → surrounding orchestration
        |
        +---- denied   → different surrounding orchestration
```

An approved decision does not itself prove the target access exists.

The next ownership boundary still matters.

---

## 17. Working Engineer: Adaptive Approval

Priya requests sensitive Finance access through ISC's native governed request process.

The access item is configured to use an appropriate Workflow for approval.

### Pattern anatomy

```text
PURPOSE
Perform supported Workflow-based approval logic
inside native access-request governance.

EVENT
Access Request Submitted

CONTEXT
requestedItem
requestedFor
requestedBy
accessRequestId
plus deliberately retrieved enrichment if required.

DECISION
Approval Policy resolves the governed decision.

WORK
Approval Policy
plus bounded surrounding notification/enrichment.

BOUNDARY
The Workflow reached an approved or denied
governed business outcome.

RISK
Treating Workflow success as "access granted."
```

### The shape

```text
Access Request Submitted
        ↓
read request context
        ↓
optional enrichment
        ↓
Approval Policy
        |
        +---- APPROVED
        |
        +---- REJECTED
```

A rejected request can still represent a perfectly successful Workflow execution.

That is not a contradiction.

```text
business decision = rejected
Workflow handled it correctly
        ↓
execution can be successful
```

This gives us a sharper version of the course principle:

> **Green does not mean approved.**

And even:

```text
approved
        ≠
provisioned
        ≠
verified live on target
```

Those are separate boundaries.

### Keep governance ownership intact

Workflow participates in the governed process.

It does not replace native access-request governance.

That architectural distinction from Module 09 remains binding.

---

## 18. Working Engineer: Controlled collection pattern

Some Workflows legitimately process a bounded collection.

### Pattern anatomy

```text
PURPOSE
Apply the same bounded orchestration
to multiple returned subjects.

EVENT
Whatever event or schedule justifies the collection.

CONTEXT
A documented returned collection.

DECISION
Which members of the collection qualify?

WORK
Loop and perform the bounded action.

BOUNDARY
The collection processing reached its action/result boundaries.

RISK
Volume, partial failure, ordering, and repeated side effects.
```

### The shape

```text
retrieve bounded collection
        ↓
qualify collection/items
        ↓
loop
        ↓
perform work per item
```

The important word remains **bounded**.

Do not use this pattern as permission to turn Workflow into a bulk-processing engine.

### Stop before Module 11

At this point you should recognize several questions:

- What if item 6 fails after items 1–5 succeeded?
- What if the Workflow runs again?
- Does order matter?
- What if two executions touch the same item?

Those are excellent questions.

Do not solve all of them here.

They are exactly where Module 11 begins.

---

## 19. Working Engineer: Certification creation

Sometimes the required orchestration is not merely:

> Tell somebody something looks risky.

The business may require an explicit governed review.

Acme decides that Priya's move into Finance should create an Identity Certification for a governance group.

### Pattern anatomy

```text
PURPOSE
Create a governed review in response
to a meaningful event.

EVENT
For this scenario:
Identity Attributes Changed
with the relevant Finance transition.

CONTEXT
The affected ISC identity id
plus certification configuration.

DECISION
Does this event meet Acme's policy
for creating a certification?

WORK
Create Certification Campaign.

BOUNDARY
Campaign creation completed according
to the action contract.

RISK
Assuming creation means activation,
review, completion, or remediation.
```

### Event precision still matters

The mover seed may contain:

```json
{
  "identity": {
    "type": "IDENTITY",
    "id": "2c91808568c529c60168cca6f90c1313",
    "name": "priya.patel"
  },
  "changes": [
    {
      "attribute": "department",
      "oldValue": "Sales",
      "newValue": "Finance"
    }
  ]
}
```

The event proves an identity attribute changed.

The Workflow still needs to confirm that this is the business transition Acme cares about.

Do not create a campaign for every unrelated attribute change.

### A representative configuration shape

Conceptually:

```text
Reviewer
→ Acme's intended reviewer/group

Certification Type
→ Identity Certification

Identity
→ Priya's ISC identity id

Start Campaign when Created
→ follow the intended and validated design

Undecided items
→ follow Acme certification policy
```

The exact tenant configuration belongs to the implementation.

The pattern lesson is the boundary.

### Creation is not the whole lifecycle

```text
Create Certification Campaign green
        ≠
review completed
```

It also does not automatically prove:

- campaign activation;
- reviewer sign-off;
- campaign completion;
- remediation;
- target-state correction.

That is **Green Does Not Mean Done** applied to governance.

### Activation boundary

Current action documentation exposes a **Start Campaign when Created** option that can activate after creation.

A deliberately staged design can instead keep creation and activation as separate boundaries.

Do not teach one universal sequence for every campaign design.

Teach the configured boundary that Acme actually chose and validate it.

### Production risk

Creating a certification changes governance state and creates reviewer work.

So before production ask:

> What happens if the same business situation causes this creation logic to run again?

Do not assume the action is idempotent unless its current contract explicitly guarantees that behavior.

Recognize the duplicate-campaign risk.

Module 11 will handle the deeper replay/correlation design.

---

---

[← Previous: Module 10.1: Pattern Method & Core Patterns](10-1-pattern-method-and-core-patterns.md) | [Course home](README.md) | [Next: Module 10.3: Advanced Patterns & Pattern Transfer →](10-3-advanced-patterns-and-pattern-transfer.md)
