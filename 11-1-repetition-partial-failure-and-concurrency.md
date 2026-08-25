# Module 11.1: Repetition, Partial Failure & Concurrency
Module 10 taught you to recognize a good Workflow shape.

You learned to ask:

```text
PURPOSE
→ EVENT
→ CONTEXT
→ DECISION
→ WORK
→ BOUNDARY
→ RISK
```

That gets you to an apparently sound design.

Now we do something different.

We try to break it.

```text
Module 10

This pattern fits.

        ↓

Module 11

Which assumption inside the pattern fails
when reality stops being orderly?

        ↓

Module 12

Design the whole solution deliberately
before opening the builder.
```

This is where Workflow design starts to look less like building a diagram and more like engineering a production system.

A Workflow does not live in a tidy private machine.

It lives in an event-driven world containing:

- other Workflow executions;
- changing identity and account state;
- external systems;
- connectors;
- schedules;
- human decisions;
- retries and recovery;
- partial results;
- temporary outages;
- uncertain timing.

The goal is not to assume that world will behave perfectly.

The goal is to make the design remain correct when it does not.

One question will follow us through the entire module:

> **If this happens twice, does the system still end in the correct state?**

Keep that question close.

It exposes more production defects than another hour spent polishing the happy path.

---

## 1. Core: Stress the design

Module 10 gave you a pattern anatomy.

Module 11 gives you a stress test.

For any apparently good Workflow pattern, attack it from these directions:

```text
REPEAT
Could this business situation be processed again?

OVERLAP
Could two executions touch the same state
at roughly the same time?

PARTIAL
Could some work succeed before failure
becomes visible?

DEPEND
Could another system be unavailable,
slow, ambiguous, or incapable?

SCALE
What changes when one subject becomes hundreds
or scheduled work starts to overlap?

INTERPRET
What does the event actually prove?
Are we treating a signal as a verdict?
```

And when one business process continues through later executions:

```text
CORRELATE
How does the later execution know
which business object or process it belongs to?
```

You can remember the method as:

```text
GOOD-LOOKING DESIGN
        ↓
STRESS IT

REPEAT
OVERLAP
PARTIAL
DEPEND
SCALE
INTERPRET

+ CORRELATE when work crosses executions
```

You are not expected to solve every distributed-systems problem with Workflow.

Sometimes the result of the stress test will be:

> This design needs a stronger external coordination mechanism.

Sometimes it will be:

> Workflow should orchestrate less of this.

That is a valid engineering conclusion.

---

### Three kinds of statements

This module mixes SailPoint behavior with broader engineering reasoning.

Keep three categories separate.

#### Documented SailPoint behavior

Examples:

```text
Scheduled executions can overlap.

Parallel Loop work can execute concurrently,
and processing order is not guaranteed.

Manage Access can report failed requested items
without automatically making the Workflow execution fail.
```

These are product behaviors.

#### Engineering failure model

Examples:

```text
Two executions could both read the same state
before either changes it.

A remote system could perform an action
before its response becomes unavailable.

A later execution could reason from state
that changed after an earlier read.
```

These are possible failure conditions we design against.

They are not claims that SailPoint specifically caused them.

#### Engineering control

Examples:

```text
re-read authoritative state

use a documented downstream idempotency key

enforce uniqueness on a stable business key

store durable correlation

reconcile after ambiguity

route uncertain cases for recovery
```

These are design techniques.

They are not automatic Workflow guarantees.

That distinction becomes important immediately.

---

## 2. Core: When the same thing happens twice

Start with something simple.

Priya joins Acme.

The Joiner Workflow:

```text
Identity Created
        ↓
validate required context
        ↓
send welcome notification
        ↓
create starter ticket
```

The first run creates:

```text
INC-10428
```

Then a later step fails.

An engineer investigates the execution and reruns the process.

What happens?

---

### Ask before answering

Do not start with:

> How do I retry the failed step?

Start with:

> **What already changed in the world?**

The welcome notification may already have been sent.

The starter ticket may already exist.

The Workflow failure does not rewind those external side effects.

So a second execution can produce:

```text
welcome notification
welcome notification

INC-10428
INC-10491
```

The Workflow may be functioning exactly as designed.

The design is still wrong for the business requirement.

---

### Where can repetition come from?

Do not invent a duplicate-event guarantee.

You do not need one.

The same business work can become relevant again because of:

- an operator rerun;
- scheduled execution overlap;
- a caller retrying an External Trigger;
- repeated external or business changes;
- recovery after partial completion;
- a later recalculated condition;
- concurrent work touching shared state.

The engineering rule is broader:

> **Do not make correctness depend on exactly-once processing unless the applicable contract explicitly guarantees it.**

That rule is more useful than guessing why a second execution appeared.

---

### A current-state check helps, but it is not enough

A common first improvement is:

```text
Does Priya already have a starter ticket?
        |
        +---- yes → skip creation
        |
        +---- no  → create ticket
```

That is useful.

It prevents obviously unnecessary repeat work.

But do not call it a concurrency-safe idempotency guarantee.

Imagine two executions overlap:

```text
Execution A
check → no ticket

Execution B
check → no ticket

Execution A
create ticket

Execution B
create ticket
```

Both checks were correct when they happened.

You still created two tickets.

The problem is the gap between:

```text
CHECK
```

and:

```text
ACT
```

Another execution can enter that gap.

---

### Separate three mechanisms

This distinction is important enough to learn explicitly.

#### 1. Current-state check

```text
read current state
        ↓
avoid obviously unnecessary work
```

Useful for:

- skipping an already-disabled account;
- avoiding a notification when the required condition no longer exists;
- checking whether access is already held;
- detecting that a previous process appears complete.

But a separate read followed by a separate write can still race.

---

#### 2. Idempotency or uniqueness contract

The side-effect boundary itself understands a stable operation identity.

Conceptually:

```text
business operation key:
ONBOARDING-TICKET:PRIYA:2026-08-24
```

If the downstream interface documents a mechanism that guarantees the same key cannot create the same business operation twice, overlapping callers can safely present that key.

The important part is not the string format.

The important part is where uniqueness is enforced.

```text
same stable business operation
        ↓
same idempotency / uniqueness contract
        ↓
one intended side effect
```

Do not claim a downstream API provides that guarantee unless its contract actually does.

---

#### 3. Durable coordination or reconciliation

Sometimes the Workflow cannot enforce uniqueness at the side-effect boundary.

Then the design may require durable state outside the individual execution.

That state can help answer questions such as:

```text
Has this business operation already been claimed?

Which execution owns it?

What remote object was created?

Was the result confirmed?

Does current state match intended state?
```

A later reconciliation process can also compare:

```text
INTENDED STATE
        vs
AUTHORITATIVE CURRENT STATE
```

and repair or escalate the difference.

Durable state is not magic either.

A design that merely performs:

```text
read marker
→ marker absent
→ perform side effect
→ write marker
```

can still contain a race.

Where competing executions matter, the coordination mechanism itself needs an appropriate uniqueness or atomic-claim property.

That property belongs to whatever durable system is being used.

---

### The engineering habit

Before every world-changing step, ask:

> **If another execution performs this same business operation, what prevents duplicate or contradictory state?**

Possible answers include:

- the repeated operation is naturally harmless;
- current state makes the second operation unnecessary;
- the downstream system guarantees uniqueness;
- a durable coordination mechanism chooses one owner;
- reconciliation will resolve ambiguity;
- the operation is too risky to automate without a human recovery path.

Those are very different answers.

That is the point.

---

### Work It Out

Acme's Joiner Workflow creates a starter ticket and then sends a welcome message.

The ticket is successfully created.

The notification step fails.

An operator reruns the process.

What must you know before saying that the rerun is safe?

You need to know what already happened and what each repeated side effect does.

The failed Workflow execution does not prove the starter ticket was rolled back.

A current-state lookup can help determine whether work already exists, but a lookup followed by creation is not by itself a concurrency-safe uniqueness guarantee.

If duplicate ticket creation is unacceptable, the design needs a stronger duplicate-prevention or reconciliation strategy appropriate to the ticketing interface.

The notification has its own repeat behavior and may require a different decision.

Recovery begins by determining actual state, not by assuming that every step before the visible failure needs to run again.

---

## 3. Core: When two correct executions collide

Repetition is one problem.

Concurrency is another.

Picture Priya during a chaotic afternoon.

At nearly the same time:

```text
Finance mover condition
        ↓
Workflow A begins

leaver lifecycle transition
        ↓
Workflow B begins
```

Workflow A retrieves Priya and sees:

```text
department = Finance
lifecycle = Active
```

Workflow B begins the leaver process.

A few moments later, Workflow A uses the state it already read.

Is that state still safe to act on?

Maybe.

Maybe not.

That is a race condition.

---

### The stale-state problem

A Workflow can make a perfectly logical decision from information that was true a moment ago.

```text
READ
Priya is Active

        ↓

another execution changes relevant state

        ↓

ACT
perform action based on old Active state
```

Nothing about the first read was incorrect.

The world changed after it.

For sensitive actions, that can matter.

---

### Re-read current state near the decision boundary

Suppose Workflow A is about to send a routine Finance onboarding request.

Before performing a sensitive or expensive action, it can re-read the current authoritative state it depends on.

```text
initial event
        ↓
build context
        ↓
...
        ↓
before sensitive action:
re-read required current state
        ↓
still eligible?
```

This reduces stale-state decisions.

But remember the previous lesson.

A fresh re-read is still not automatically a concurrency lock.

Two executions can both re-read the same current state and then both act.

So distinguish the purposes:

```text
RE-READ CURRENT STATE
helps reduce stale decisions

        ≠

UNIQUENESS / COORDINATION
prevents competing executions
from multiplying a side effect
```

Both may be necessary.

---

### Do not depend on undocumented cross-Workflow ordering

A fragile design says:

```text
Workflow A will always finish first.

Then Workflow B will run.

Then Workflow C will see B's result.
```

Do not make correctness depend on that assumption unless the current product contract explicitly guarantees the required ordering.

Use the safer engineering rule:

> **Do not make correctness depend on the relative ordering of independent Workflow executions unless the current product contract explicitly guarantees that ordering.**

If one operation truly must happen after another, design around a supported lifecycle boundary, authoritative state, explicit correlation, or another mechanism that actually establishes the dependency.

Do not use optimism as sequencing.

---

### Scheduled overlap is the same problem wearing different clothes

Suppose Acme has a scheduled operational Workflow.

```text
06:00
run starts
        ↓
large population still processing

07:00
next scheduled execution starts
```

SailPoint currently documents that a new scheduled execution can begin before the previous scheduled execution completes.

Now both executions may discover Priya.

```text
06:00 execution
find Priya
        ↓

07:00 execution
find Priya
```

Ask:

- Can both create the same ticket?
- Can both send the same form?
- Can both submit the same business operation?
- Does a state check merely reduce duplicates, or is true uniqueness required?
- Should the schedule be redesigned because the work routinely exceeds its interval?

This is why schedule overlap is not merely a Module 08 limit fact.

It is a correctness question.

---

### Work It Out

A scheduled Workflow searches for unfinished contractor offboarding every hour.

At 07:00 it finds Priya and begins a slow downstream operation.

At 08:00 the previous execution is still running, and the new execution finds Priya again.

An engineer proposes:

```text
Just check whether Priya is still marked unfinished.
```

What does that fix, and what does it not fix?

The check may prevent work if Priya has already reached a clearly completed state.

It does not by itself prevent both executions from observing the same unfinished state and then acting concurrently.

If duplicate side effects are harmful, the design needs an appropriate uniqueness, coordination, or reconciliation mechanism in addition to any current-state check.

The schedule itself also deserves review if overlap is becoming normal rather than exceptional.

---

## 4. Core: When half the Workflow already happened

Clean failure is easy to reason about:

```text
nothing changed
        ↓
failure
```

Partial completion is harder:

```text
change
        ↓
change
        ↓
change
        ↓
failure
```

Suppose Priya's leaver process does this:

```text
remove access
        ↓
disable account
        ↓
open ServiceNow ticket
        ↓
send final confirmation
```

The first three operations happen.

The confirmation fails.

Now someone says:

> Retry the Workflow.

That sentence is incomplete.

---

### Retry and recovery are not the same thing

Use these definitions:

```text
RETRY

Repeat an operation believed to have failed.
```

```text
RECOVERY

Determine what actually happened,
then continue from the correct state.
```

Those can produce very different behavior.

---

### Why blind retry is dangerous

Suppose the first execution already:

- removed access;
- disabled an account;
- opened `INC-7734`.

A blind rerun may:

- request the access removal again;
- send another account action;
- open `INC-7791`;
- send another notification.

Some repeated actions may be harmless.

Some may not.

You cannot decide from the Workflow's final status alone.

---

### Recovery begins with evidence

A recovery design asks:

```text
What did the first execution definitely complete?

What outputs did important actions return?

What current state exists now?

Which side effects can safely repeat?

Which side effects need reconciliation?

Where is human intervention safer?
```

This is another form of:

> **Green Does Not Mean Done.**

And the inverse also matters:

> **Red Does Not Mean Nothing Happened.**

A failed execution can leave successful business side effects behind.

---

### Order cheap certainty before expensive side effects

If a Workflow needs to validate:

- identity state;
- required identifiers;
- policy eligibility;
- source capability;
- required business values;

do that before an expensive or destructive action whenever the design allows it.

Prefer:

```text
validate
        ↓
retrieve required context
        ↓
confirm eligibility/capability
        ↓
world-changing action
```

over:

```text
world-changing action
        ↓
discover required data was missing
        ↓
fail
```

This does not eliminate every partial failure.

It reduces how often you create one unnecessarily.

---

### Partial results inside a successful action matter too

Partial completion is not limited to a Workflow ending red.

Manage Access is a useful example.

Its current Workflow action contract can return both:

```text
successfulAccessRequests
```

and:

```text
failedAccessRequests
```

A populated `failedAccessRequests` result does not automatically make the overall Workflow execution fail.

So this is unsafe reasoning:

```text
Manage Access box is green
        ↓
all requested access work succeeded
```

Instead:

```text
Manage Access completed
        ↓
inspect important result data
        ↓
did every required item meet
the business success condition?
```

This is the Module 05 action-contract lesson under production stress.

---

### Work It Out

Priya's leaver Workflow:

1. removes required access;
2. disables an account;
3. creates a ServiceNow ticket;
4. sends confirmation.

The first three complete.

The fourth fails.

Which question is better?

```text
How do I rerun the Workflow?
```

or:

```text
What state did the first execution leave behind,
and what is the safe recovery point?
```

Explain why.

The second question is the correct starting point.

The first execution may have already changed multiple systems. Recovery has to determine actual state before deciding which work should repeat.

A repeated account or access operation may be harmless only if its current contract and current state make it so. Ticket creation may require duplicate prevention or reconciliation. The failed notification may simply need a targeted retry.

Recovery continues from reality. It does not pretend the failed execution never existed.

---

## 5. Core: When another system gives you an ambiguous answer

External dependencies create a special kind of failure.

Consider this sequence.

Acme's Workflow calls a case-management API.

```text
HTTP Request
        ↓
remote system creates SEC-8821
        ↓
response becomes unavailable
        ↓
Workflow cannot determine the final remote result
```

This is an **engineering failure model**.

It is not a claim that SailPoint causes a remote system to behave this way.

The important fact is that distributed systems can lose certainty between:

```text
REMOTE SIDE EFFECT
```

and:

```text
LOCAL CONFIRMATION
```

---

### Local failure does not prove remote failure

Suppose the Workflow sees an HTTP failure or timeout.

This reasoning is unsafe:

```text
my request failed locally
        ↓
the remote object definitely does not exist
        ↓
create it again
```

The remote system may have received and committed the first request before the response became unavailable.

A second create may produce:

```text
SEC-8821
SEC-8840
```

Now your recovery action created the defect.

---

### Retry versus recovery appears again

If the operation is known not to have happened:

```text
RETRY
may be appropriate
```

If the outcome is ambiguous:

```text
RECOVERY
determine what happened first
```

That may mean querying:

- the remote object;
- a stable external event ID;
- an integration record;
- authoritative current state;
- a reconciliation queue.

Then continue based on evidence.

---

### Downstream idempotency keys

Some APIs provide a documented idempotency-key or uniqueness contract.

If the case-management API documents that behavior, Acme could send:

```text
hr-event-id = hr-00421
```

as the stable operation key in the way that API requires.

Then the API itself can prevent repeated application of the same business operation according to its contract.

Do not generalize that technique into:

> Every API accepts an idempotency key.

It does not.

The downstream contract has to provide it.

---

### When the remote system offers no such contract

Then the design may require reconciliation:

```text
ambiguous result
        ↓
query remote system
        ↓
does object for business key already exist?
        |
        +---- yes → continue from existing object
        |
        +---- no  → decide whether create is safe
        |
        +---- uncertain → human / recovery path
```

Again, a simple query followed by a create is not automatically concurrency-proof.

The mechanism has to match the risk.

---

### Failure needs ownership

An external dependency can be:

- unavailable;
- slow;
- rate-limiting;
- returning unexpected data;
- rejecting credentials;
- partially completing work;
- unable to prove its own final business state.

The Workflow cannot make those facts disappear.

It has to decide:

```text
STOP?
FALL BACK?
RECONCILE?
ESCALATE?
RETRY?
WAIT FOR LATER CONTROL?
```

That is production design.

---

### Work It Out

Acme's HR service calls an External Trigger using stable event ID:

```text
hr-00421
```

The Workflow validates the event and calls a case-management API.

The remote API creates:

```text
SEC-8821
```

but the Workflow never receives a usable success response.

Later, the HR system retries `hr-00421`.

What should the second execution determine before creating another case?

It should determine whether the business side effect associated with `hr-00421` already happened.

If the case-management API provides a documented idempotency mechanism, the stable event key can be used according to that contract.

Otherwise the design needs a durable lookup or reconciliation strategy that can connect the external event to any case already created.

The important distinction is:

```text
the local HTTP step did not confirm success
        ≠
the remote side effect definitely did not happen
```

---

---

[← Previous: Module 10.3: Advanced Patterns & Pattern Transfer](10-3-advanced-patterns-and-pattern-transfer.md) | [Course home](README.md) | [Next: Module 11.2: Scale, Correlation & External State →](11-2-scale-correlation-and-external-state.md)
