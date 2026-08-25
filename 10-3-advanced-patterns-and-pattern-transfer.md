# Module 10.3: Advanced Patterns & Pattern Transfer
## Part III: Advanced Recognition

Advanced does **not** mean irrelevant.

These are real patterns.

It means the number of independent boundaries and production risks has increased.

Your goal is to recognize the architecture, the facts each event proves, and the engineering question that must be answered before production.

---

## 20. Advanced: Certification lifecycle orchestration

A certification can span multiple independent event boundaries.

Do not stretch one Workflow execution across the whole lifecycle just because the business calls it one review.

Conceptually:

```text
Create Certification Campaign
        ↓
Campaign Generated
        ↓
Campaign Activated
        ↓
review activity
        ↓
Certification Signed Off
        ↓
Campaign Ended
        ↓
remediation / target evidence where required
```

Those are not synonyms.

### Pattern anatomy

```text
PURPOSE
Coordinate work around different stages
of a certification lifecycle.

EVENT
Different campaign/certification events
for different lifecycle facts.

CONTEXT
Campaign/certification identifiers
and stage-specific data.

DECISION
What work belongs at this lifecycle boundary?

WORK
Activate / notify / observe / route
according to the particular pattern.

BOUNDARY
Each event proves only its own documented stage.

RISK
Correlation, replay, and collapsing several stages
into one false "complete" state.
```

### Generated is not activated

A staged design can look like:

```text
Create Certification Campaign
        ↓
Campaign Generated
        ↓
campaign ready at its generated/staged boundary
        ↓
Activate Certification Campaign
        ↓
Campaign Activated
```

If a later Workflow acts on the campaign, it must operate on the intended campaign identity.

That introduces a **correlation question**.

Module 10 should make you recognize that question.

Module 11 owns the deeper design for making cross-execution correlation durable and safe.

### Signed off is not campaign ended

A campaign can contain multiple certifications.

So:

```text
Certification Signed Off
        ≠
Campaign Ended
```

One reviewer completing one certification does not prove the entire campaign has ended.

### Campaign ended is not necessarily target proof

Even after governance reaches its completion boundary, remediation can still be a separate concern.

So retain the chain:

```text
governance completed
        ≠
every target change independently verified
```

### Production risks

This pattern should make three alarms go off in your head:

```text
REPLAY
Could the same creation/activation work happen again?

CORRELATION
How does a later execution know which campaign it belongs to?

BOUNDARY
Which event proves which lifecycle fact?
```

You do not need the complete durable-state design yet.

You do need to recognize that a campaign name or a green box is not enough to answer those questions safely.

---

## 21. Advanced: Native Change response

Suppose Priya's Active Directory account is directly added to:

```text
Finance Privileged Operators
```

outside ISC.

Acme wants Security notified and may, under explicit policy, revoke that out-of-band addition.

This is not a normal identity-attribute mover.

It is a target-account change detected outside ISC.

### Pattern anatomy

```text
PURPOSE
React to an out-of-band target-account change.

EVENT
Native Change Account Updated

CONTEXT
Source, account, change types,
entitlement changes, correlation information.

DECISION
Did the relevant protected entitlement change?
What response does policy authorize?

WORK
Notify / ticket / potentially remediate
under an explicit approved policy.

BOUNDARY
The Workflow reacted to a detected native change.

RISK
Treating the signal as proof of malicious intent,
or creating repeated/destructive responses.
```

### Configuration is part of the pattern

Native Change Detection has to be configured for the source and relevant monitored changes.

So the Workflow definition alone is not the whole design.

Conceptually:

```text
Native Change Detection configured
        ↓
target changes outside ISC
        ↓
aggregation detects change
        ↓
Native Change Account Updated
        ↓
Workflow evaluates it
```

If the source is not configured to detect the change you care about, the Workflow cannot react to an event it never receives.

### Signal is not verdict

This is the strongest lesson in the pattern.

```text
Native Change
→ proves an out-of-band change was detected

Native Change
≠
proof of malicious intent
```

The change could reflect:

- unauthorized activity;
- an emergency admin action;
- break-glass procedure;
- manual operational work;
- another external process.

Your notification should state what the event proves.

Do not make the Workflow invent intent.

### A representative shape

```text
Native Change Account Updated
        ↓
is this the protected source?
        ↓
does the change include entitlement addition?
        ↓
inspect added entitlements
        ↓
protected entitlement?
        |
        +---- no  → end
        |
        +---- yes
                ↓
        notify Security / source owner
                ↓
        optional policy-approved remediation
```

### Remediation is a separate decision

SailPoint supports Native Change remediation patterns.

That does not mean every native change should be automatically reversed.

Before destructive remediation, Acme needs deliberate answers to questions such as:

- Is the policy unambiguous?
- Is this entitlement always prohibited outside the governed path?
- Does the source support the intended revoke operation?
- Is the entitlement reference actionable?
- What is the exception path?

### Production risk

An external actor can change the target again later.

That can create another real native-change event.

Recognize the risk:

```text
external re-change
→ another response
→ possible repeated alert/remediation
```

Do not design the full suppression or reconciliation mechanism here.

Carry that problem to Module 11.

---

## 22. Advanced: Outlier response

Identity Outliers gives us a useful example of another major principle:

> **Signal is not verdict.**

An identity may be identified as unusually different from its peers.

That is a risk signal.

It is not automatic proof that:

- Priya is malicious;
- one particular entitlement is unauthorized;
- every account should be disabled.

### Pattern anatomy

```text
PURPOSE
Respond to an identity-risk signal
according to an approved policy.

EVENT
Outlier Detected

CONTEXT
Outlier score/type and identity reference,
plus deliberately retrieved current context.

DECISION
Which policy band applies?
What response is authorized?

WORK
Notify / create governed review /
perform explicitly authorized containment.

BOUNDARY
The Workflow executed the selected response.

RISK
Treating a statistical/risk signal as a security verdict
or allowing destructive automation without policy.
```

### Read the event representation you actually receive

The Workflow event documents a decimal score representation from:

```text
0.0 → 1.0
```

with higher values representing a stronger outlier signal.

The product UI can present richer information and a different display scale.

Do not copy a UI value directly into Workflow logic without checking the event representation.

If the event provides:

```text
0.82
```

a comparison expecting:

```text
>= 70
```

is not reading the event representation correctly.

### Current template examples are examples

SailPoint currently provides Outlier Workflow templates demonstrating bands conceptually like:

```text
lower band
→ manager notification

higher review band
→ certification + notification

highest band
→ account containment + notification
```

Current templates use specific numeric ranges.

Those ranges demonstrate product-supported patterns.

They are **not Acme's universal security policy**.

Acme still needs to decide:

- which populations the policy covers;
- which score bands authorize which responses;
- what exceptions exist;
- who owns recovery;
- what evidence is required.

### Priya's review path

Suppose Acme explicitly adopts a review policy that routes Priya's `0.82` event to governed certification.

The shape becomes:

```text
Outlier Detected
        ↓
inspect score / outlierType / identity
        ↓
retrieve current identity/manager context
        ↓
Acme policy selects review band
        ↓
Create Certification Campaign
        ↓
notify manager
```

Now reuse the certification boundary you already learned.

```text
campaign created
        ≠
review complete
        ≠
remediation complete
        ≠
target verified
```

### Destructive containment

A higher-risk policy might disable accounts.

That is a legitimate supported pattern in the right design.

It is also high blast radius.

Before an account is treated as automatically containable, the pattern has to respect:

- source capability;
- intended account scope;
- partial results;
- business authorization;
- downstream evidence.

Do not reason:

```text
Get Accounts found it
        ↓
therefore Disable is supported
```

Finding an account is not the same as proving the source supports that provisioning operation.

### Production risk

The same identity can become relevant again over time.

An operator can also rerun work after ambiguous failure.

So recognize:

```text
repeat signal
→ possible repeat certification / notification / containment
```

Do not assume exactly-once behavior.

The deeper reconciliation and repeat-safety design belongs in Module 11.

---

## 23. Advanced: External Trigger integration contract

Sometimes the initiating business event belongs outside ISC.

Suppose Acme's HR platform knows about a high-priority separation before any native ISC event represents the moment Acme wants to orchestrate around.

An External Trigger can become that inbound Workflow boundary.

### Pattern anatomy

```text
PURPOSE
Accept a deliberate external event contract
and start bounded ISC orchestration.

EVENT
External Trigger

CONTEXT
Caller-supplied dynamic JSON.

DECISION
Is the payload structurally valid?
Are business values valid?
Can external identifiers be resolved safely?

WORK
Perform the authorized orchestration.

BOUNDARY
The Workflow accepted and processed
the inbound contract according to its design.

RISK
Identifier confusion, replay, weak validation,
and trusting caller-supplied data too far.
```

### Define a contract

Do not accept:

```json
{
  "stuff": "whatever"
}
```

and hope the Workflow can work it out.

A deliberate contract might look like:

```json
{
  "eventId": "hr-2026-08-19-00421",
  "eventType": "SEPARATION_FILED",
  "workerId": "W-18422",
  "effectiveAt": "2026-08-19T15:00:00Z",
  "reasonCode": "VOLUNTARY"
}
```

Those are values supplied by the caller.

They are not magically ISC identifiers.

### Dynamic data requires deliberate access

External Trigger input is dynamic.

That means the Workflow may need manual JSONPath references such as:

```text
$.trigger.eventId
$.trigger.workerId
```

rather than assuming every incoming field appears as a normal fixed variable-selection option.

That makes the upstream contract part of the design.

### Validation has layers

A strong inbound pattern distinguishes:

```text
SHAPE
Does the field exist?
Is it a string/timestamp/etc.?

BUSINESS VALUE
Is SEPARATION_FILED an allowed eventType?

IDENTITY RESOLUTION
Does W-18422 map to exactly the intended ISC identity?

AUTHORIZATION
Is this caller/event allowed to request this orchestration?

REPLAY
Has this business event already been handled?
```

A type check handles only the first layer.

It does not prove the business meaning of the value.

### Identifier mapping

This deserves special attention.

```text
HR worker id
        ≠
ISC identity id

ticket id
        ≠
account id

vendor object id
        ≠
SailPoint object id
```

Two systems using the field name `id` does not make the identifiers interchangeable.

Resolve external identifiers deliberately.

Reject or investigate missing and ambiguous matches.

### Production risk

A caller may retry.

An operator may replay a failed process.

The upstream system may send the same business event again.

Recognize that as a replay-safety requirement.

A stable upstream `eventId` can be useful as part of the contract.

But Module 10 stops here:

> **The pattern needs a deliberate answer for repeat delivery.**

Module 11 will handle the durable state and duplicate-side-effect reasoning.

---

## Part IV: Combining Patterns

## 24. Core / Working Engineer Bridge: Real Workflows combine simple shapes

Real production Workflows rarely fit one isolated label.

Priya's leaver process may require both:

```text
notify manager
        +
create Facilities ticket
```

Those are two familiar patterns sharing one lifecycle event.

### Combined shape

```text
Identity Lifecycle State Changed
        ↓
qualify leaver transition
        ↓
retrieve required identity context
        |
        +----------------------+
        |                      |
        v                      v
notify manager          create Facilities ticket
```

That does not automatically mean every branch should share the same failure policy.

Ask:

- Does notification failure mean ticket creation should stop?
- Does ticket failure mean the manager should not be notified?
- Which result matters to which business owner?
- Does one branch depend on data produced by the other?
- Which outcome belongs outside Workflow?

Those questions determine whether two patterns should be:

- sequential;
- independent branches;
- separate Workflows;
- or part of different capability-owned processes.

### Combine by shared reasoning, not canvas convenience

Do not combine patterns merely because:

> They start from the same event, so I can put them all on one canvas.

And do not split them merely because:

> Smaller is always better.

Ask whether they share:

- purpose;
- context;
- lifecycle;
- failure ownership;
- operational ownership.

This is where pattern adaptation becomes architecture.

---

## 25. Working Engineer: Notification plus ticket

Take a common example:

```text
meaningful event
        ↓
notify owner
        +
open ticket
```

The two pieces share an event.

They may not share a success boundary.

```text
notification delivered
        ≠
ticket created

ticket created
        ≠
ticket resolved
```

If the ticketing system is unavailable, you must decide what that means for the process.

Possible questions:

- Should notification still happen?
- Should the Workflow follow an error branch?
- Which team owns recovery?
- Would rerunning later create duplicate work?
- Is ticket creation the business-critical path or only supplemental evidence?

Do not jump to the retry algorithm yet.

First make the business boundaries explicit.

That is the preparation Module 11 needs.

---

## Part V: Pattern Transfer

## 26. Work It Out: A pattern you have not seen exactly

Acme has a privileged application.

When provisioning reaches its completion event, Acme wants:

- no message for normal successful outcomes;
- the application owner notified when the result requires human attention;
- a ticket created when manual follow-up is required;
- the Workflow to avoid claiming that the target is corrected merely because the ticket was created.

Do **not** start by choosing boxes.

Write the anatomy.

### PURPOSE

What business orchestration is required?

### EVENT

What starts the pattern?

### CONTEXT

What information must you obtain from the event or through deliberate lookup?

### DECISION

What result requires human follow-up?

### WORK

What should the Workflow do?

### BOUNDARY

What does a successful Workflow execution prove?

### RISK

What is the most important production assumption?

Think through your answer before reading on.

---

### A strong answer

```text
PURPOSE
Route provisioning outcomes that require human follow-up.

EVENT
Provisioning Completed.

CONTEXT
Enough provisioning/source/subject information
to classify the result and resolve the responsible owner.

DECISION
Does this event require manual follow-up?

WORK
Notify the application owner.
Create a ticket when Acme's policy requires one.

BOUNDARY
The Workflow reacted to the provisioning event
and completed its notification/ticket actions
according to their contracts.

It does not prove the underlying target state
was independently corrected.

RISK
External ticketing dependency and repeat side effects
if the same business situation is processed again.
```

### Which existing patterns did you reuse?

At least three:

```text
Provisioning-result reaction
        +
operational alert
        +
outbound ticket integration
```

That is pattern transfer.

You did not copy a Workflow called:

> Privileged Application Provisioning Failure v3

You recognized several reusable shapes and combined them around one requirement.

---

## 27. One more transfer exercise: Scheduled data-quality review

Acme wants a daily report when identities are missing a manager.

An engineer proposes:

```text
Scheduled Search
→ loop every identity in preview
→ repair each identity
```

Use the pattern model.

What is wrong with the proposal?

A strong answer should identify at least three things:

1. **Scheduled Search boundary**
   - its inline preview should not be assumed to be the complete result population.
2. **Ownership**
   - Workflow can coordinate data-quality remediation but should not automatically become the owner of every identity-data correction.
3. **Operating model**
   - a large recurring repair population may be a batch-processing architecture problem rather than a simple Workflow pattern.

A safer pattern might instead be:

```text
Scheduled Search
        ↓
report-ready event
        ↓
inspect count / preview / report reference
        ↓
notify data owner or hand off processing
```

or, for a deliberately small bounded case:

```text
Scheduled Trigger
        ↓
bounded supported lookup
        ↓
inspect returned identities
        ↓
notify / ticket
```

The correct design depends on the real requirement.

That is exactly why pattern anatomy matters more than recipe copying.

---

## Part VI: Final Pattern Checkpoint

## 28. Checkpoint: Do you recognize the shape?

By now you should be able to take an unfamiliar Workflow requirement and describe:

```text
PURPOSE
Why does this orchestration exist?

EVENT
What fact starts it?

CONTEXT
What data is present,
and what must be retrieved?

DECISION
What must the Workflow determine?

WORK
What side effect or orchestration occurs?

BOUNDARY
What does success actually prove?

RISK
What production assumption deserves scrutiny?
```

You should also be able to distinguish maturity.

### Core recognition

You can adapt:

- joiner communication;
- mover notification;
- leaver notification/ticketing;
- aggregation-failure alerts;
- provisioning-result reactions;
- data-quality alerts;
- simple outbound integrations;
- bounded scheduled processes;
- basic human-input orchestration.

### Working Engineer recognition

You can reason about:

- Manage Access;
- Manage Accounts;
- Access Request Decision reactions;
- Adaptive Approval;
- bounded loops;
- certification creation;
- combined multi-action orchestration.

### Advanced recognition

You can identify the boundaries and risks in:

- certification lifecycle event chains;
- Native Change response;
- Outlier response;
- External Trigger contracts;
- destructive security-remediation patterns.

You do **not** yet need to claim that every repeat/failure/concurrency problem has been solved.

Instead, you should know when the pattern has crossed into questions such as:

```text
What if it runs twice?

What if the action succeeds
but the response is lost?

What if five loop items succeed
and the sixth fails?

What if two executions touch
the same object?

What state survives between executions?

What if the external system disagrees
with what the Workflow thinks happened?

What if remediation partially succeeds?
```

Those questions are not evidence that your pattern is bad.

They are evidence that you have reached the next engineering layer.

---

## 29. From patterns to failure engineering

Module 09 taught:

```text
Choose the right capability.
```

Module 10 taught:

```text
Recognize and adapt the right Workflow shape.
```

Now we deliberately attack that shape.

```text
Module 10

I recognize the pattern.

        ↓

Module 11

Now I try to break it.
```

In Module 11, we will press on:

- repetition;
- duplicate side effects;
- partial failure;
- ordering;
- concurrency;
- overlap;
- retry behavior;
- ambiguous external outcomes;
- durable state;
- reconciliation.

Do not leave this module thinking:

> I know the leaver pattern.

Leave thinking:

> I know how to decompose a Workflow pattern into its purpose, event, context, decision, work, success boundary, and production risk. I can adapt that shape without blindly copying somebody else's implementation.

That is the skill that survives when the next requirement has a business name you have never seen before.

---

## Official References

- [Workflow Triggers - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-triggers.html)
- [Workflow Actions - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-actions.html)
- [Workflow Operators - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-operators.html)
- [Identity Attributes Changed - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/identity-attribute-changed/)
- [Account Aggregation Completed - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/account-aggregation-completed/)
- [Setting Up Lifecycle States - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/provisioning/lifecycle.html)
- [Adaptive Approvals - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/adaptive_approvals/index.html)
- [Managing Native Change Detection - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/sources/native_change_detection.html)
- [Native Change Account Updated - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/native-change-account-updated/)
- [Outlier Detected - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/outlier-detected/)
- [Identity Outliers - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/ai/access_insights/outliers.html)
- [Workflow Templates - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-templates.html)
- [Managing Workflows - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-manage.html)

---

[← Previous: Module 10.2: Working Engineer Patterns](10-2-working-engineer-patterns.md) | [Course home](README.md) | [Next: Module 11.1: Repetition, Partial Failure & Concurrency →](11-1-repetition-partial-failure-and-concurrency.md)
