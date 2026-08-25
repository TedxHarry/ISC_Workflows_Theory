# Module 10.1: Pattern Method & Core Patterns
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

## Part I: Core Patterns

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

---

[← Previous: Module 09.2: Architecture Decisions & Tradeoffs](09-2-architecture-decisions-and-tradeoffs.md) | [Course home](README.md) | [Next: Module 10.2: Working Engineer Patterns →](10-2-working-engineer-patterns.md)
