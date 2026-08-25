# Module 12.1: Paper Design Framework
**Prove the theory without a tenant.**

You have reached the end of the theory.

The question now is not whether you have read the modules.

It is whether you can use them.

Designing on paper is not a lesser version of building. It is where you decide whether the thing you are about to build makes sense at all.

A bad event boundary is cheaper to discover on paper.

So is missing data.

So is an action whose success proves less than you thought.

So is a recovery path that creates duplicate work.

So is a design that cannot actually prove the business outcome it promises.

The progression of the last three modules has been deliberate:

```text
Module 10

This pattern fits.

        ↓

Module 11

Which assumption inside the pattern fails
when reality stops being orderly?

        ↓

Module 12

Can I design and defend
the whole solution before I build it?
```

That is the job now.

You are going to turn everything you have learned into a paper architecture another engineer could review.

---

## 1. Core: From stress testing to complete design

Module 11 taught you to attack a design with:

```text
REPEAT
OVERLAP
PARTIAL
DEPEND
SCALE
INTERPRET
CORRELATE
```

That exposed assumptions.

Module 12 does not replace that stress test.

It uses the result.

A complete paper design should be able to explain:

```text
what business outcome is required

why Workflow owns the orchestration

what starts the process

what data the design can trust

what decisions it makes

what actions change the world

what failure looks like

what repetition and overlap do

what evidence proves success

what assumptions still need verification
```

Notice the difference between:

```text
I know which trigger and actions I want.
```

and:

```text
I can defend why this architecture
should reach the required business outcome.
```

The second is the standard for this module.

You are no longer designing as someone discovering Workflow features.

You are designing as a junior engineer who expects another engineer to ask:

> Why?

---

## 2. Core: Before the seven: should Workflow own this?

Before answering any architecture question, make one capability decision:

> **Should Workflow own this requirement at all?**

This is a gate.

It is not question 0.

It is not question 8.

The seven-question framework remains seven questions.

```text
REQUIREMENT
     ↓
Should Workflow own it?
     |
     ├── no
     │    ↓
     │  choose the appropriate capability
     │
     └── yes
          ↓
        run the seven engineering questions
```

Module 09 already taught you that Workflow is an orchestration tool, not the answer to every IAM requirement.

If the real requirement is better owned by another ISC capability, choose that capability.

For example, do not build a Workflow merely because you already know how.

Ask:

- Is this event-driven orchestration?
- Are several steps or systems being coordinated?
- Does the process need branching, human interaction, notification, or recovery?
- Or am I forcing Workflow around something another capability owns more naturally?

A good paper design can end here:

```text
WORKFLOW OWNERSHIP:
No.

REASON:
The requirement belongs to another capability.

NEXT DESIGN DECISION:
Use that capability instead.
```

That is not failure.

That is architecture.

---

## 3. Core: The seven engineering questions

If Workflow passes the ownership gate, run the seven questions.

Use them exactly.

```text
1. What actually starts this process?

2. What data arrives, and what is missing?

3. What decisions must be made?

4. What actions belong here?

5. What can fail, and how will failure be handled?

6. What happens if this runs twice or concurrently?

7. What evidence proves the intended business outcome?
```

These are not seven builder steps.

They are seven ways to discover whether your design is complete.

### Question 1: What actually starts this process?

Find the real business event.

Do not begin with:

> Which trigger do I remember?

Begin with:

> What changed in the business?

Then ask which supported event boundary represents that change closely enough.

You may also need a filter so the Workflow does not treat every technically similar event as relevant.

The failure this question prevents is:

```text
wrong event boundary
        ↓
correct-looking Workflow
        ↓
wrong business process
```

A trigger tells you why an execution began.

It does not automatically tell you everything you need to know about the business situation.

---

### Question 2: What data arrives, and what is missing?

Inspect the real event data.

Separate:

```text
ARRIVES WITH EVENT

MUST BE RETRIEVED

MUST BE VALIDATED

MUST COME FROM AN AUTHORITATIVE SOURCE
```

Do not assume:

- an identifier means the identifier you need;
- a field is present because a sample contained it;
- a field is usable because its type is valid;
- a list contains the complete population required by the business promise.

That last distinction matters.

```text
retrieval succeeded
        ≠
population completeness proven
```

Suppose the requirement says:

> Process every expired contractor.

A retrieval action returning successfully proves that it returned a result.

It does not, by itself, prove that the result represents every contractor the requirement expects.

Your architecture therefore needs to establish one of these:

```text
the expected population fits the supported retrieval boundary

OR

the scope is deliberately constrained
so completeness is defensible

OR

another supported architecture is required

OR

population completeness remains
an explicit fact to verify before implementation
```

Do not invent pagination, batching, or other behavior that the selected action does not document.

The failure this question prevents is:

```text
valid data
        ↓
incomplete or misunderstood context
        ↓
confidently wrong decision
```

---

### Question 3: What decisions must be made?

Now model the decisions.

Ask:

```text
What conditions matter?

What branches exist?

What should stop?

What should continue?

What is a valid no-op?

What requires escalation?

What must be re-checked close to a sensitive action?
```

A good design includes the branch where nothing should happen.

It also distinguishes policy from signal.

For example:

```text
event detected
        ≠
policy verdict
```

and:

```text
unusual condition
        ≠
automatic authorization
for a destructive response
```

The failure this question prevents is:

```text
event observed
        ↓
assumption made
        ↓
action taken without enough reasoning
```

---

### Question 4: What actions belong here?

Actions perform the work.

For every important action, state:

```text
what it changes

what input it needs

what success means

what output matters later
```

Be especially careful with world-changing actions.

Ask:

> What does this action actually prove when it reports success?

Do not silently turn:

```text
action succeeded
```

into:

```text
business outcome achieved
```

Those are often different boundaries.

Also distinguish discovery from capability.

```text
account discovered
        ≠
requested account action supported
```

If your design expects ISC to change an account, source and connector capability are part of the architecture.

The failure this question prevents is:

```text
green step
        ↓
stronger conclusion than the step earned
```

---

### Question 5: What can fail, and how will failure be handled?

Do not stop at:

> Add an error branch.

Ask what failure leaves behind.

```text
nothing changed
        ↓
failure
```

is easy.

This is harder:

```text
side effect succeeded
        ↓
another side effect succeeded
        ↓
later step failed
```

Now you have partial completion.

Recovery begins with evidence.

Ask:

```text
What definitely happened?

What might have happened?

What can safely repeat?

What requires reconciliation?

What needs escalation?

What does the next execution need to know?
```

Keep the Module 11 distinction:

```text
RETRY

Repeat an operation believed to have failed.
```

```text
RECOVERY

Determine what actually happened,
then continue from the correct state.
```

The failure this question prevents is blind recovery that multiplies damage.

---

### Question 6: What happens if this runs twice or concurrently?

Always ask both parts.

```text
REPLAY

What if this happens again later?
```

and:

```text
OVERLAP

What if another execution reaches
the same business state before this one finishes?
```

A current-state check can reduce unnecessary repeated work.

It does not automatically create concurrency-safe idempotency.

```text
check current state
        ≠
concurrency lock
```

Likewise:

```text
stable eventId carried
        ≠
duplicate suppression
```

and:

```text
check
→ see "not processed"
→ record
→ act
```

does not automatically become safe merely because durable storage exists.

Two overlapping executions can both pass an ordinary check before either establishes ownership.

Where duplicate side effects are unacceptable, you need an appropriate boundary such as:

```text
atomic uniqueness / claim

OR

a downstream idempotency contract
when the downstream system actually documents one

OR

durable coordination plus reconciliation
```

Do not claim an idempotency guarantee that the real interface does not provide.

And do not make correctness depend on the relative ordering of independent Workflow executions unless the applicable product contract explicitly guarantees that ordering.

The failure this question prevents is a design that works only when reality politely executes one thing at a time.

---

### Question 7: What evidence proves the intended business outcome?

This is the final architecture question.

Not:

> Did the Workflow turn green?

Not:

> Did the last action succeed?

Ask:

> **What evidence would make me willing to tell the business that the promised outcome occurred?**

This may require several layers.

```text
Workflow execution status
        ↓
action result
        ↓
per-item result
        ↓
later lifecycle event
        ↓
independent target observation
```

Different requirements stop at different evidence boundaries.

For example:

```text
approval handled
        ≠
access provisioned
        ≠
access independently confirmed live
```

A denial can also be the correct business outcome.

A Workflow that correctly processes a rejection may finish successfully even though no access was granted.

For actions that can report individual success and failure inside a successful Workflow execution, the design must inspect the evidence needed before claiming that every requested change succeeded.

Population completeness belongs here too.

```text
retrieval action succeeded
        ≠
every intended subject was covered
```

If the business promise says:

> Disable every relevant account.

your evidence must address both:

```text
Did the required action succeed
for the accounts processed?
```

and:

```text
Do I know the intended account population
was actually covered?
```

This is the final form of:

> **Green Does Not Mean Done.**

---

## 4. Core: Turn answers into a paper architecture

Seven answers are useful.

A reviewable architecture is better.

Use this sheet.

```text
PURPOSE
What business outcome are we trying to achieve?


OWNERSHIP GATE
Should Workflow own this?
Why?


1. START
Business event:
Workflow event boundary:
Filter / scope:


2. DATA
Available:
Missing:
Validation:
Authoritative source:
Population-completeness concern:


3. DECISIONS
Branches:
Guards:
No-op / stop conditions:
Policy decisions:


4. ACTIONS
Work performed:
Order:
World-changing steps:
Success boundary of each important action:
Capability dependencies:


5. FAILURE
Failure points:
Partial-completion risks:
Recovery:
Escalation:


6. REPEAT
Later replay:
Overlapping execution:
Current-state checks:
Idempotency / uniqueness boundary:
Correlation / reconciliation:


7. EVIDENCE
What proves the intended business outcome?
What does Workflow success prove?
What does it not prove?
How is complete population coverage established?


ASSUMPTIONS TO VERIFY
Current product behavior:
Tenant configuration:
Source / connector capability:
Identifiers:
Population / execution constraints:
Other dependencies:


IMPLEMENTATION NOTES
Safe testing:
Monitoring / observation:
Operational owner:
```

This is your design artifact.

It lets another engineer separate:

```text
WHAT I KNOW ARCHITECTURALLY

WHAT I AM ASSUMING

WHAT MUST BE VERIFIED BEFORE BUILD
```

That separation matters.

An engineer does not need to pretend every implementation fact is already known.

A strong paper design can say:

```text
DESIGN DECISION

Use this event boundary.


VERIFY BEFORE BUILD

Confirm the exact current payload fields
needed by the filter.
```

That is stronger than false certainty.

---

---

[← Previous: Module 11.2: Scale, Correlation & External State](11-2-scale-correlation-and-external-state.md) | [Course home](README.md) | [Next: Module 12.2: Capstone Design Lab →](12-2-capstone-design-lab.md)
