# Module 10: Real-World Workflow Patterns

Module 09 taught you to stop before building and ask:

> **Should Workflow participate in this requirement at all?**

You learned to identify the primary capability owner first and then decide whether Workflow has an orchestration role.

Now assume that architecture decision has been made.

Workflow belongs in the solution.

The next question is:

> **What Workflow shape should we start from?**

```text
Module 09

Should Workflow participate?
What should it own?

        ↓

Module 10

Workflow belongs here.
What reusable shape fits?

        ↓

Module 11

What happens when that good-looking shape
meets repetition, partial failure,
concurrency, scale, and uncertain external state?
```

This module is a pattern library.

But a pattern is **not a recipe**.

You are not here to memorize:

> Finance mover Workflow = these seven boxes in this exact order.

You are here to recognize the shape underneath the business story, adapt that shape to another requirement, and know which assumption deserves the most scrutiny before production.

That requires a model.

---

## 1. Core: The anatomy of a Workflow pattern

Every pattern in this module can be examined through the same seven questions:

```text
PURPOSE
What business orchestration does this pattern serve?

        ↓

EVENT
What starts it?

        ↓

CONTEXT
What useful data is already available?
What must be retrieved?

        ↓

DECISION
What must the Workflow determine?

        ↓

WORK
What action or orchestration occurs?

        ↓

BOUNDARY
What does successful completion actually prove?

        ↓

RISK
What assumption is most likely to fail in production?
```

Condensed:

```text
PURPOSE
→ EVENT
→ CONTEXT
→ DECISION
→ WORK
→ BOUNDARY
→ RISK
```

That is the spine of Module 10.

### A very small example

Acme wants the Finance access owner notified when an aggregation fails.

The pattern is:

```text
PURPOSE
Alert the responsible team about a failed aggregation.

EVENT
Account Aggregation Completed

CONTEXT
Source and aggregation outcome from the event.

DECISION
Does the verified aggregation outcome match
the condition Acme intends to alert on?

WORK
Notify the responsible owner or operations channel.

BOUNDARY
The Workflow performed its notification step.

RISK
A noisy or badly filtered pattern teaches people
to ignore the alert.
```

That is more reusable than memorizing one notification canvas.

Tomorrow the business may replace email with Slack.

The source name may change.

The recipient may come from a different lookup.

Those details change.

The pattern shape survives.

---

## 2. Core: How to adapt a pattern

When you borrow a pattern, do not copy everything.

Separate three kinds of information.

### The stable shape

This is what makes the pattern recognizable.

For example:

```text
relevant operational event
        ↓
qualify the signal
        ↓
identify the responsible owner
        ↓
notify
```

That shape can work for several operational alerts.

### Environment-specific choices

These belong to Acme, your tenant, or your organization.

Examples:

- source names;
- departments;
- access objects;
- recipients;
- governance groups;
- ticket queues;
- external endpoints;
- business thresholds;
- schedules;
- escalation owners.

Copying those from somebody else's Workflow is not pattern reuse.

It is configuration copying.

### Production-dependent decisions

These cannot be answered safely by the diagram alone.

Examples:

- Can the event repeat?
- Does a later system own the real business outcome?
- Does the source support the operation you want?
- Can two runs interact?
- What happens after a partial result?
- Does the external system need independent verification?

Those are where engineering begins.

So adaptation looks like:

```text
PRESERVE THE SHAPE
        ↓
CHANGE THE BUSINESS DETAILS
        ↓
RECHECK THE DATA BOUNDARY
        ↓
RECHECK THE SUCCESS BOUNDARY
        ↓
RECHECK THE PRODUCTION RISK
```

Never stop at:

> This looks like a mover Workflow I saw before.

Ask:

> Which parts of that mover pattern are actually invariant here?

---

## 3. Three maturity levels

Not every pattern in this module has the same difficulty.

That matters.

### Core

You should be able to recognize and adapt these on a first pass.

They teach clean event, context, decision, work, and boundary reasoning.

### Working Engineer

These add meaningful side effects, governance boundaries, collections, or multi-stage product behavior.

You should be able to reason through them, but they deserve more deliberate verification.

### Advanced

These involve security response, event chains, external contracts, destructive actions, correlation questions, or multiple independent business boundaries.

Your goal here is **recognition and boundary judgment**.

You are not expected to solve every replay, idempotency, race, retry, or reconciliation problem yet.

When an Advanced pattern raises one of those issues, Module 10 should let you say:

> This is a production risk that needs an answer.

Module 11 will teach you how to attack that answer.

---

# Part I: Core Patterns

## 4. Core: Joiner communication

Priya joins Acme.

The IAM team wants to notify her manager and the onboarding team.

### Pattern anatomy

```text
PURPOSE
Coordinate communication around a newly created identity.

EVENT
Identity Created

CONTEXT
Identity data available in the trigger.
Retrieve current identity data if required values
are absent or unusable.

DECISION
Does this identity qualify for this communication?
Who should receive it?

WORK
Send the appropriate notification
or create a human follow-up item.

BOUNDARY
The Workflow performed its communication action.

RISK
Data may not be ready in the form the action expects.
```

### The reusable shape

```text
Identity Created
        ↓
validate required context
        ↓
retrieve missing/current context if needed
        ↓
resolve recipient
        ↓
notify
```

The important word is **validate**.

An Identity Created event gives you an identity boundary.

It does not guarantee that every optional or configured value you would like to use is populated and usable.

Suppose the email needs:

```text
displayName
manager
department
startDate
```

Do not treat the existence of the event as proof that all four values are ready for your message.

Inspect what actually arrived.

Retrieve current identity information when the pattern genuinely requires it.

### What this pattern does not own

A joiner communication Workflow should not quietly become Acme's standard-access engine.

Keep the Module 09 ownership model:

```text
Role
→ can determine standard access through its assignment model

Access Profile
→ represents bundled access

Lifecycle State
→ can drive lifecycle-state-related access
   and configured account-state behavior

Workflow
→ coordinates surrounding communication,
   integration, exceptions, or human work
```

If Acme's requirement is:

> Every qualifying employee gets the standard employee access package.

that is not made a Workflow requirement merely because the employee also needs a welcome message.

### Production risk: data readiness

The pattern may be logically correct and still produce a bad message because a required value was null, stale, or unavailable at the event boundary.

That is why the stable pattern is:

```text
event
→ validate context
→ act
```

not:

```text
event
→ assume context
→ act
```

---

## 5. Core: Mover notification

Priya moves from Sales to Finance.

The Finance team wants to know.

### Pattern anatomy

```text
PURPOSE
React to a meaningful identity-attribute transition.

EVENT
Identity Attributes Changed

CONTEXT
Identity reference plus changes[] describing
the attributes that actually changed.

DECISION
Did the relevant attribute change
in the direction the business cares about?

WORK
Notify or open bounded downstream work.

BOUNDARY
The orchestration reacted to the detected change.

RISK
Reading the wrong change or assuming context
that the event did not provide.
```

### The reusable shape

```text
Identity Attributes Changed
        ↓
inspect changes[]
        ↓
find the relevant attribute change
        ↓
confirm old/new values as required
        ↓
retrieve additional current context if needed
        ↓
route
        ↓
notify / ticket
```

For Priya:

```text
department
Sales → Finance
```

The Workflow must deliberately identify that transition.

Do not assume:

```text
changes[0]
```

is always department.

More than one attribute can change.

The position of the useful change is not the business rule.

The **attribute and its values** are the business rule.

### Manager data: retrieve it deliberately

A department-change event does not automatically mean manager information is present.

`changes[]` describes attributes that actually changed.

So if Acme wants to notify Priya's **current manager**, a safer conceptual pattern is:

```text
Identity Attributes Changed
        ↓
identity.id
        ↓
Get Identity
        ↓
current manager reference
        ↓
retrieve manager identity if more manager data is needed
        ↓
notify
```

If the manager attribute itself changed, that manager change may appear in `changes[]`.

That is a different event condition.

Do not turn it into a universal assumption for every mover.

### Production risk: event precision

A sloppy mover pattern can:

- alert on unrelated changes;
- miss the relevant transition;
- use stale assumptions about current identity data;
- route to the wrong person.

The event gives you a signal.

Your pattern still has to interpret the right part of that signal.

---

## 6. Core: Leaver communication and ticketing

Now Priya leaves Acme.

Facilities needs a ticket.

Security needs a notification.

### Pattern anatomy

```text
PURPOSE
Coordinate human or external work around
a lifecycle transition.

EVENT
Identity Lifecycle State Changed

CONTEXT
Lifecycle transition plus any current identity
data needed for the downstream work.

DECISION
Is this the lifecycle transition this process owns?

WORK
Notify / create ticket / start bounded follow-up.

BOUNDARY
The Workflow performed the surrounding orchestration.

RISK
The Workflow can accidentally duplicate native lifecycle
responsibilities or create repeated downstream work.
```

### The reusable shape

```text
lifecycle transition
        ↓
qualify the state change
        ↓
gather required context
        ↓
notify
        +
create downstream work
```

This is an important architecture boundary.

Lifecycle State configuration can own lifecycle-driven access changes and configured account-state behavior.

So do not casually build:

```text
leaver event
→ manually reconstruct every native leaver control in Workflow
```

when those controls already belong to lifecycle configuration.

A leaver Workflow is strongest when it coordinates around those controls.

For example:

```text
Lifecycle State
→ owns configured lifecycle access/account behavior

Workflow
→ notifies Facilities
→ opens hardware-return ticket
→ informs Security
→ coordinates an exception
```

That preserves the Module 09 ownership model.

### Production risk: downstream side effects

Creating a ticket changes another system.

If the same business situation is processed again, another ticket may be created.

You should recognize that as a replay/duplicate-side-effect risk.

Do not solve the entire idempotency architecture here.

Carry the question forward:

> **If this pattern runs again, what would happen?**

Module 11 will force that question much harder.

---

## 7. Core: Aggregation-failure alert

One of the most useful Workflows in a tenant can be very small.

An aggregation reaches a failure or termination condition Acme cares about.

Tell the right person.

### Pattern anatomy

```text
PURPOSE
Turn an aggregation failure or termination condition
into an actionable signal.

EVENT
Account Aggregation Completed

CONTEXT
Aggregation outcome and source information.

DECISION
Does the verified aggregation outcome match
the failure / termination condition
Acme actually intends to alert on?

WORK
Route an alert to the responsible owner/team.

BOUNDARY
The Workflow emitted the operational notification.

RISK
Poor filtering creates noise and destroys trust in the alert.
```

The important implementation habit is not memorizing one status value.

The exact status predicate is an implementation fact to verify against the current native Workflow contract and actual trigger data.

> **Do not hard-code a status value from memory.**

### The reusable shape

```text
Account Aggregation Completed
        ↓
inspect the verified aggregation outcome
        ↓
does it match the failure / termination condition
Acme actually intends to alert on?
        |
        +---- no  → end quietly
        |
        +---- yes
                ↓
          identify source
                ↓
          route to owner
                ↓
             notify
```

The filter is not decorative.

Without a precise condition:

```text
aggregation outcomes Acme does not care about
        ↓
another message
```

Soon the channel becomes noise.

When the real operational condition arrives, nobody notices.

### Signal before remediation

An actionable aggregation outcome can result from different operational conditions, such as:

- connectivity;
- credentials;
- source behavior;
- collection problems;
- other operational conditions.

The event gives you an aggregation outcome.

Your verified predicate determines whether that outcome matches the failure or termination condition Acme intends to alert on.

It does not automatically tell your Workflow that one universal corrective action is safe.

A strong Core pattern often stops at:

```text
detect
→ identify
→ notify responsible operator
```

Automated remediation requires a stronger decision boundary.

---

## 8. Core: Provisioning-result reaction

Suppose Acme wants an operations team notified when a provisioning process reaches its later Workflow event boundary.

### Pattern anatomy

```text
PURPOSE
React after provisioning reaches its documented event boundary.

EVENT
Provisioning Completed

CONTEXT
Provisioning event data relevant to the process.

DECISION
Does this result require follow-up?

WORK
Notify / route / create bounded downstream work.

BOUNDARY
The Workflow reacted to the provisioning event.

RISK
Treating the event as independent proof of final target state.
```

### The reusable shape

```text
Provisioning Completed
        ↓
inspect relevant result/context
        ↓
requires follow-up?
        |
        +---- no  → end
        |
        +---- yes → notify / ticket
```

This pattern reinforces one of the course's most important principles:

> **Green Does Not Mean Done.**

A later provisioning event is a meaningful boundary.

It is still not automatically the same thing as independent target-state verification.

If Acme's business requirement is:

> Prove the access is live exactly as intended on the target.

then your architecture must identify what evidence proves that fact.

Do not silently upgrade one Workflow event into stronger evidence than its boundary provides.

---

## 9. Core: Data-quality alert

Every tenant accumulates imperfect data.

Perhaps some identities are missing a manager.

Perhaps a required department value is absent.

Workflow can help coordinate remediation.

### Pattern anatomy

```text
PURPOSE
Find or receive a data-quality signal
and route remediation work.

EVENT
Scheduled Search report-ready event
OR
Scheduled Trigger for a deliberately bounded lookup.

CONTEXT
Search/report information or a bounded returned collection.

DECISION
Which conditions require human or external follow-up?

WORK
Notify / ticket / hand off remediation.

BOUNDARY
The Workflow coordinated the remediation request.

RISK
Treating report preview as the full population
or turning Workflow into an unbounded batch processor.
```

There are two different shapes here.

### Shape A: Scheduled Search as a report-ready event

Conceptually:

```text
Scheduled Search
        ↓
report is available
        ↓
inspect count / preview / report reference
        ↓
route / notify / hand off processing
```

The inline result is a **preview**.

Do not teach:

```text
Scheduled Search
→ preview contains every matching identity
→ loop over whole population
```

as a general contract.

If the full report needs substantial processing, that may belong in a different execution environment.

### Shape B: Scheduled Trigger plus bounded lookup

Another pattern is:

```text
Scheduled Trigger
        ↓
perform a documented bounded lookup
        ↓
inspect returned subjects
        ↓
process the bounded collection
```

The key word again is **bounded**.

Verify the current action's return and operating limits when designing the real Workflow.

### What this pattern owns

Workflow can coordinate:

```text
bad data detected
→ identify responsible owner
→ notify / ticket
```

It should not automatically become the owner of calculated identity-attribute logic that belongs to Transform or the authoritative data model.

### Production risk: accidental batch architecture

The moment the requirement becomes:

> Process every identity in a very large population every night.

you are no longer merely adapting a data-quality alert.

You are asking an architecture question about the execution environment.

Module 09 taught you to recognize that signal.

---

## 10. Core: Simple outbound integration

Acme receives a meaningful ISC event and needs to create a case in another system.

### Pattern anatomy

```text
PURPOSE
Send bounded event-driven work to an external system.

EVENT
The ISC event that actually represents the business moment.

CONTEXT
Fields required by the external request.

DECISION
Should this event create/update the external object?

WORK
HTTP Request or supported integration action.

BOUNDARY
The outbound action completed according to its contract.

RISK
External availability, credentials, response assumptions,
and ambiguous downstream state.
```

### The reusable shape

```text
event
        ↓
validate required context
        ↓
shape outbound request
        ↓
call external system
        ↓
inspect response needed by later steps
        ↓
continue / error branch
```

The external system is a dependency.

It has its own:

- availability;
- latency;
- authentication;
- API contract;
- object lifecycle.

Do not hide those facts behind a single action box.

### Green Does Not Mean Done

Suppose the HTTP action returns successfully after creating a ticket.

That may prove the HTTP interaction satisfied the action's success contract.

It does not automatically prove:

- the ticket reached the intended queue;
- the correct human worked it;
- the underlying access problem was fixed.

Keep Workflow success separate from business-outcome proof.

### Security

Do not bury credentials directly in the Workflow definition.

Use supported secure parameter handling where the action and supported parameter mechanism allow it.

And never send sensitive identity information to a chat channel simply because notification is convenient.

---

## 11. Core: Simple scheduled operational pattern

Scheduled work has a different data shape from event-driven identity work.

### Pattern anatomy

```text
PURPOSE
Perform bounded operational work on a schedule.

EVENT
Scheduled Trigger

CONTEXT
The schedule itself does not magically provide
the business subject you need.

DECISION
What subject or condition should be examined now?

WORK
Retrieve bounded context, decide, act.

BOUNDARY
This scheduled execution performed its bounded job.

RISK
Unbounded population work or overlap assumptions.
```

### The reusable shape

```text
Scheduled Trigger
        ↓
retrieve the subject/context
        ↓
evaluate
        ↓
act
```

Compare that with an identity event:

```text
Identity event
        ↓
subject already exists in event context
```

Scheduled work frequently has to **find its subject**.

That is the important adaptation lesson.

Do not copy an identity-trigger pattern and assume a Scheduled Trigger will somehow contain the same identity data.

### Production risk

A scheduled pattern can look harmless while gradually expanding into:

```text
every night
→ retrieve everyone
→ loop everything
→ call several systems
```

At that point the operating model deserves a new architecture review.

---

## 12. Core: Human-input pattern

Some orchestration starts because a person needs to provide information.

You already learned the supported human-interaction mechanisms in Module 06.

Do not reteach them here.

Study the pattern shape.

### Pattern anatomy

```text
PURPOSE
Collect human-provided context before continuing
a bounded orchestration.

EVENT
Supported interactive/human-start boundary
from the Module 06 design.

CONTEXT
Initial process data plus human-provided values.

DECISION
Are the required values valid,
and what path should they select?

WORK
Route / notify / call / submit the intended action.

BOUNDARY
The Workflow used the collected input
to complete its orchestration responsibility.

RISK
Confusing human input with governed authorization
or trusting unvalidated data.
```

### The reusable shape

```text
process begins
        ↓
collect required human input
        ↓
validate
        ↓
make bounded decision
        ↓
perform work
```

A form can collect a value.

That does not automatically make the person entering it an authorized approver for a governed access process.

Keep interaction, validation, and governance ownership separate.

---

## 13. Core Pattern Checkpoint

You should now be able to describe a simple pattern without drawing its exact canvas.

Consider:

> Acme wants the application owner notified whenever a provisioning event reaches a result that requires human follow-up.

Before building, write:

```text
PURPOSE:
...

EVENT:
...

CONTEXT:
...

DECISION:
...

WORK:
...

BOUNDARY:
...

RISK:
...
```

A strong answer might look like:

```text
PURPOSE
Route a provisioning result that requires human follow-up.

EVENT
Provisioning Completed.

CONTEXT
The provisioning event fields needed to identify
the subject, source, and relevant result.

DECISION
Does this result require application-owner attention?

WORK
Resolve the owner and notify or create a ticket.

BOUNDARY
The Workflow successfully performed the follow-up orchestration.

RISK
Treating the Workflow or provisioning event as proof
that the final target state is correct.
```

If you can produce that without memorizing a previous canvas, you are using patterns correctly.

---

# Part II: Working Engineer Patterns

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

# Part III: Advanced Recognition

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

# Part IV: Combining Patterns

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

# Part V: Pattern Transfer

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

# Part VI: Final Pattern Checkpoint

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

[← Previous: Module 09 When to Use Workflows and When Not](09-when-to-use-workflows.md) | [Course home](README.md) | [Next: Module 11 Challenges, Failure Modes & Edge Cases →](11-challenges-and-edge-cases.md)