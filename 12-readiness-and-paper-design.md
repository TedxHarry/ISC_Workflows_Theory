# Module 12: Readiness & Paper Design

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

## 5. Core: One complete worked design

Now watch the full method once.

### Scenario

Acme hires contractors.

Each contractor has a contract end date.

When the contract ends, Acme wants:

1. the contractor's required accounts disabled;
2. the sponsoring manager notified;
3. the sponsor asked to confirm the offboarding;
4. Security alerted if confirmation does not arrive within the required deadline.

Design it.

---

### PURPOSE

The business outcome is not:

> Run an account action.

It is:

> Expired contractors are moved into the required offboarding state, the sponsor is brought into the process, unresolved cases become visible to Security, and Acme can prove that the intended contractor population was covered.

That last clause matters.

---

### OWNERSHIP GATE

Should Workflow own this?

The requirement coordinates:

```text
event / schedule
        ↓
identity selection
        ↓
account work
        ↓
human interaction
        ↓
escalation
```

That is orchestration.

Workflow is a reasonable owner **if** the population and required actions fit supported product and source capabilities.

If the expected population cannot be processed completely by the selected retrieval and execution approach, that assumption can invalidate the architecture.

So the ownership answer is:

```text
YES, CONDITIONALLY

Workflow fits the orchestration pattern.

Before implementation, verify that
population retrieval and execution boundaries
can support the promised scope.
```

---

### 1. START: What actually starts this process?

"Contract end date has passed" is a business condition.

It does not force one technical event design.

Two plausible boundaries are:

```text
Scheduled Trigger
        ↓
find contractors whose end date
is now eligible for processing
```

or:

```text
Lifecycle-state transition
        ↓
process the identity that entered
the offboarding state
```

For this worked design, choose a Scheduled Trigger because we are not assuming the tenant already drives contractor expiration through a lifecycle transition.

That decision creates an immediate consequence:

> A schedule starts the execution, but it does not identify one contractor for us.

That becomes a data problem.

---

### 2. DATA: What arrives, and what is missing?

The Workflow needs enough context to establish:

- which contractors are in scope;
- their contract state;
- their sponsor;
- which accounts require action;
- whether those accounts can be changed through the intended operation.

The scheduled execution therefore needs a supported way to retrieve the intended contractor population.

Now ask the capstone question the old design missed:

> Does a successful retrieval prove every expired contractor was returned?

No.

```text
retrieval succeeded
        ≠
complete population proven
```

Before build, Acme must establish one of these:

```text
the expected population fits the current supported boundary

OR

the retrieval scope is deliberately constrained
so completeness can be defended

OR

a different supported architecture is required
```

Do not invent a pagination or batching strategy merely because the design needs one.

Record the uncertainty.

```text
ASSUMPTION TO VERIFY

Expected expired-contractor population
can be retrieved and processed completely
using the chosen supported approach.
```

---

### 3. DECISIONS: What decisions must be made?

For each contractor, the design may need to decide:

```text
Is this contractor actually eligible now?

Has the required offboarding already completed?

Which accounts are in scope?

Can ISC perform the required operation
on each account/source?

Is sponsor context available?

Did the sponsor respond?

Did the response arrive before escalation is required?
```

A valid no-op matters.

If the intended state is already confirmed, unnecessary repeat work should stop.

If required identity or sponsor context is missing, do not invent it.

Route the case deliberately.

If an account is visible but its source does not support the required automatic operation, the design needs an alternate manual or escalation path.

```text
account discovered
        ≠
automatic action capability established
```

---

### 4. ACTIONS: What actions belong here?

A reasonable action sequence is:

```text
retrieve eligible contractors
        ↓
for each contractor:
validate current eligibility
        ↓
discover required accounts
        ↓
verify capability
        ↓
perform supported account-changing work
        ↓
inspect important results
        ↓
notify sponsor
        ↓
request sponsor confirmation
        ↓
continue or escalate
```

Do not collapse all of that into:

> Disable account, send form, done.

Each world-changing action has a success boundary.

For example:

```text
account action accepted / reported successful
        ≠
every business control automatically proven
```

If Acme's control requires independent confirmation of the target state, the evidence design must include it.

Likewise, sending the sponsor interaction proves the request was issued.

It does not prove the sponsor responded.

---

### 5. FAILURE: What can fail, and how will failure be handled?

Consider failures separately.

```text
contractor retrieval incomplete or unavailable

required identity context missing

source does not support the required action

some account work succeeds while other work fails

sponsor cannot be resolved

notification fails

human interaction is cancelled or reaches its deadline

escalation fails
```

Now examine partial completion.

Suppose:

```text
Account A changed successfully.

Account B failed.

Sponsor notification succeeded.

Later step failed.
```

A blind rerun is not a recovery plan.

Recovery asks:

```text
What actually succeeded?

Which account still needs work?

Does the sponsor already have a request?

Can the failed operation safely repeat?

What must be reconciled?

What requires manual handling?
```

The design should preserve evidence from important actions and make unresolved work visible.

---

### 6. REPEAT: What happens if this runs twice or concurrently?

Ask two different questions.

#### Later replay

What happens tomorrow when the scheduled search runs again?

An already completed contractor should not blindly receive the entire process again.

A current-state check can avoid clearly unnecessary work.

But:

```text
current-state check
        ≠
concurrency-safe idempotency
```

#### Overlapping execution

Now ask the harder question:

> What if another scheduled execution starts while this one is still processing?

Both executions could discover the same contractor before either records a completed state.

If duplicate sponsor requests, tickets, or other side effects would be harmful, the design needs a stronger boundary appropriate to that operation:

```text
atomic uniqueness / claim

documented downstream idempotency

or

durable coordination / reconciliation
```

Do not label an ordinary check-before-act sequence as a lock.

Do not assume one scheduled execution always finishes before another begins.

---

### 7. EVIDENCE: What proves the intended business outcome?

The evidence must match the promise.

Acme needs to be able to answer:

```text
Did we cover the complete intended contractor population?

For each contractor,
were all required accounts handled
or explicitly routed as exceptions?

Were failures surfaced?

Was the sponsor notified?

Did the sponsor respond,
or did the case reach the required escalation path?

If policy requires confirmed target state,
what independently proves that state?
```

A green Workflow execution alone is insufficient.

So the evidence model is:

```text
POPULATION COVERAGE
        +
PER-CONTRACTOR ACTION RESULTS
        +
EXCEPTION / ESCALATION EVIDENCE
        +
HUMAN-RESPONSE EVIDENCE
        +
TARGET-STATE EVIDENCE
when the control requires it
```

Now the architecture can defend its claim.

---

### ASSUMPTIONS TO VERIFY

Before implementation, record facts such as:

```text
- Which exact current retrieval action and query shape will be used?

- Can it cover Acme's expected contractor population?

- Which current action / loop / execution constraints matter?

- Which sources support the required account operation?

- What exact identifiers are required?

- What current Form behavior matters for the chosen interaction?

- Which action outputs must be inspected?

- What evidence source will be used when target-state confirmation
  is required?
```

Notice what we did **not** do.

We did not turn Module 12 into a table of current limits and timeout values.

The engineering habit is:

```text
identify the implementation fact
that could invalidate the design

        ↓

verify it against current documentation
before building
```

---

### IMPLEMENTATION NOTES

Only after the architecture exists do we ask:

```text
How will this be tested safely?

Which world-changing steps need controlled testing?

Which conditions cannot be fully reproduced?

What will be monitored?

Who owns recovery?
```

Testing belongs here.

It is not question 7.

And remember the Module 07 lesson:

> A Workflow test must not be assumed harmless merely because it is called a test.

---

### Completed paper architecture

The result can now be summarized:

```text
PURPOSE
Offboard expired contractors and prove coverage.

OWNERSHIP
Workflow coordinates retrieval, account work,
human interaction, and escalation.

START
Scheduled execution.

DATA
Retrieve intended contractor population,
validate current eligibility and sponsor/account context.
Population completeness must be proven or verified.

DECISIONS
Eligible?
Already complete?
Account operation supported?
Sponsor available?
Response received?
Escalation required?

ACTIONS
Retrieve
→ validate
→ account work
→ inspect results
→ notify
→ request confirmation
→ escalate when required

FAILURE
Preserve partial results.
Recover from actual state.
Route unsupported or unresolved cases.

REPEAT
Handle tomorrow's replay.
Handle overlapping scheduled execution.
State checks reduce unnecessary work
but do not replace uniqueness / coordination.

EVIDENCE
Population coverage
+ per-subject results
+ exceptions
+ sponsor response/escalation
+ target evidence when required.

ASSUMPTIONS
Current population, action, source,
identifier, and execution details must be verified.

IMPLEMENTATION
Safe testing, monitoring, and recovery ownership.
```

That is a complete paper design.

No builder was required.

---

## 6. Working Engineer: Now you drive

The mentor steps back now.

### Scenario

Acme wants a security notification whenever a privileged account on a critical source is changed directly on the target outside the normal governed process.

The first version is alert-only.

Later, Acme may consider automatic remediation.

Design it on the paper sheet before reading further.

At minimum, answer:

```text
OWNERSHIP GATE

1. START

2. DATA

3. DECISIONS

4. ACTIONS

5. FAILURE

6. REPEAT

7. EVIDENCE

ASSUMPTIONS TO VERIFY
```

**Stop here and complete your design first.**

---

### Review your reasoning

A defensible design should recognize Native Change as the relevant event family when the business meaning is specifically an out-of-band target change.

Do not turn a sample payload into a universal contract.

Your data section should say something like:

```text
inspect the actual Native Change payload
        ↓
validate the context this design requires
        ↓
enrich only when necessary
```

The source must also be configured so the relevant kind of Native Change can be detected.

Record the exact current configuration and payload details as facts to verify before build.

Now the most important interpretation:

```text
Native Change detected
        ≠
malicious change

Native Change detected
        ≠
unauthorized change
```

The event is a signal.

Acme policy and context determine the authorized response.

For the alert-only design, evidence may be straightforward:

```text
relevant event identified
        ↓
required context established
        ↓
security notification delivered
```

If Acme later wants automatic remediation, the architecture becomes harder.

It now needs to establish:

- the policy actually authorizes the reversal;
- the exact changed object can be identified safely;
- the source supports the required corrective action;
- exceptions have a deliberate path;
- replay does not create a change/revert loop;
- the required evidence proves the target reached the intended state.

That is why alerting and remediation should not be treated as the same design with one extra action.

---

## 7. Working Engineer: Independent paper designs

No model answer comes first now.

Use the same paper-design sheet for every scenario.

### Scenario A: Joiner welcome

Priya joins Acme.

On her first day, Acme wants Priya and her manager to receive a welcome message containing the correct onboarding information.

Design it.

Do not assume the manager context is already available merely because the business requirement mentions a manager.

---

### Scenario B: Sensitive Finance approval

Priya requests sensitive Finance access.

The request must go through the required governed approval process.

A rejection is a valid business outcome.

If the request is approved and later provisioned, Acme wants the design to be clear about what each stage proves.

Design it.

---

### Scenario C: External HR separation event

An external HR service tells Acme that worker:

```text
W-18422
```

has a high-priority separation event.

The inbound contract includes a stable business event identifier plus worker and event information.

The process may eventually perform world-changing IAM work.

Design it.

Do not assume:

```text
authenticated caller
        =
business data is correct
```

Do not assume:

```text
external worker identifier
        =
ISC technical identity identifier
```

And do not assume:

```text
eventId carried
        =
duplicate suppression
```

---

### Scenario D: Leaver with partial failure

Priya enters the leaver lifecycle state.

The process must:

```text
remove required access
        ↓
open an external ticket
        ↓
notify the required people
```

Some requested access changes may succeed while others fail.

The ticket may already have been created before a later failure becomes visible.

Design recovery.

---

### Scenario E: The requirement that should not use Workflow

Choose one IAM requirement that another capability should own.

Your paper design ends at the ownership gate.

Explain:

```text
why Workflow should not own it

what capability should

what design problem you avoid
by not forcing Workflow into the solution
```

This scenario matters as much as the others.

Knowing when **not** to build a Workflow is part of readiness.

---

### Check your work only after you finish

Across the five scenarios, your designs should demonstrate these habits.

#### Joiner

You should identify a real joiner event boundary and validate the trigger data you actually need rather than assuming every business attribute is already present and usable.

#### Approval

You should keep these boundaries separate:

```text
approval handled
        ≠
provisioning completed
        ≠
independent target-state proof
```

A correctly handled rejection can still be a successful business process.

#### External HR event

You should validate the external contract and map the external worker identifier deliberately.

A stable event ID helps correlation.

It does not create idempotency.

If duplicate side effects are unacceptable, the design needs an appropriate atomic uniqueness/idempotency boundary, a documented downstream idempotency contract, or durable coordination/reconciliation.

An ordinary check-then-record sequence is not automatically concurrency-safe.

#### Leaver

Your recovery logic should inspect actual state and important action results.

Do not assume:

```text
Workflow failed
        =
nothing happened
```

and do not assume:

```text
Workflow green
        =
every requested access change succeeded
```

#### Wrong tool

You should be able to defend the capability decision without apologizing for not using Workflow.

That is the point of the exercise.

---

## 8. Advanced: Design under ambiguity

These scenarios are intentionally harder.

They are not final-course trivia tests.

Use them to expose architecture boundaries.

### Challenge 1: Event-driven certification

Priya moves into Finance.

Acme policy requires governance review after that transition.

Design the architecture.

Do not collapse the lifecycle into one state.

Keep distinctions such as:

```text
campaign creation
        ≠
activation

activation
        ≠
review / sign-off

review / sign-off
        ≠
campaign completion

campaign completion
        ≠
remediation proof

remediation proof
        ≠
independent target-state proof
```

If the selected campaign-creation configuration can also start the campaign, state that as a configuration choice to verify.

Do not assume every campaign must always follow the same activation path.

For repetition, do not state that campaign creation is definitely non-idempotent.

The safer engineering statement is:

> Current Workflow action documentation does not document an idempotency guarantee for campaign creation, so the design must not assume one.

What durable correlation or reconciliation prevents a rerun from blindly creating another governance process?

What evidence proves the business review actually reached the required boundary?

---

### Challenge 2: Outlier response

ISC emits an Outlier signal for Priya.

Acme has an approved policy describing when an Outlier should:

- notify;
- create governance review;
- escalate;
- or trigger a stronger containment path.

Design the response without memorizing template thresholds.

Use:

```text
OUTLIER SIGNAL
        +
ACME POLICY
        +
CURRENT CONTEXT
        ↓
AUTHORIZED RESPONSE
```

Do not use:

```text
signal
        ↓
automatic destructive verdict
```

If the authorized response includes account containment, add two separate questions:

```text
Did we discover the complete account population
required by the control?
```

and:

```text
Does each source support
the requested automatic operation?
```

An account being discoverable does not prove it is automatically controllable.

Unsupported accounts require an alternate path.

And a successful retrieval still does not prove population completeness.

---

### Challenge 3: Work that continues across executions

Imagine a Workflow creates a business object whose lifecycle continues after the first execution ends.

A later event starts another Workflow execution.

How does the later execution know which business process it belongs to?

Do not answer:

> The executions should happen in order.

That is not correlation.

Design:

```text
stable business identity
        ↓
durable correlation
        ↓
later event
        ↓
prove this event belongs
to this business process
```

Now add ambiguity.

What if the earlier execution failed after the remote object may already have been created?

Do you retry creation?

Or do you reconcile first?

This is the Module 11 distinction again:

```text
RETRY
        ≠
RECOVERY
```

At Advanced level, a good design is allowed to conclude:

> Workflow alone does not provide the coordination guarantee this requirement needs.

That is an engineering answer.

---

## 9. Core: Defend the design

A paper architecture is not finished when the boxes are filled in.

Defend it.

Imagine another engineer has your design in front of them.

They ask:

> **Why does Workflow own this?**

Can you answer without saying:

> Because we can build it in Workflow.

---

> **Why is this the correct event boundary?**

Can you describe the actual business event and why your selected trigger represents it?

---

> **Which data is authoritative?**

Can you separate:

```text
event seed
current state
external input
derived value
authoritative evidence
```

---

> **Which action changes the world?**

Can you identify the side-effect boundary and say what success really means?

---

> **What remains true if two executions overlap?**

Can you distinguish:

```text
state check
uniqueness
idempotency
coordination
reconciliation
```

instead of calling all of them "duplicate prevention"?

---

> **What happens after partial completion?**

Can you explain recovery from actual state rather than proposing a blind rerun?

---

> **What proves the intended business outcome?**

Can you name evidence strong enough for the business claim?

If the requirement says:

> every contractor

or:

> every account

can you prove population coverage rather than merely action success?

---

> **Which assumption still needs verification?**

This is not a trick question.

Every real design has assumptions.

A mature answer sounds like:

```text
Architecturally, this is the correct boundary.

Before build, I still need to verify
this current product behavior,
this tenant configuration,
and this source capability.
```

That is stronger than pretending uncertainty does not exist.

---

### A useful design-review test

If your defense relies on any of these sentences, inspect the design again:

```text
"It should only happen once."

"The other Workflow will probably finish first."

"The action was green, so it must be done."

"We returned records, so that must be everyone."

"We have an eventId, so duplicates are handled."

"The account exists in ISC, so Disable should work."

"The event says it is suspicious, so we can remediate it."

"We can just rerun the Workflow."

"The test button will be safe."
```

Each sentence hides an assumption.

Your job is to expose it.

---

## 10. Checkpoint: Are you ready to build?

You are ready to move into labs when you can do these without being handed the answer first.

-  Decide whether Workflow should own the requirement at all.
-  Identify the real business event and choose a defensible event boundary.
-  Inspect event data instead of assuming the payload contains everything you need.
-  Distinguish retrieved data from proof that the complete required population was retrieved.
-  Model decisions, including stop, no-op, exception, and escalation paths.
-  Choose actions and state what their success actually proves.
-  Design for partial completion, recovery, and imperfect dependencies.
-  Stress later replay and overlapping execution separately.
-  Distinguish current-state checks from concurrency-safe uniqueness or idempotency.
-  Define evidence that proves the intended business outcome.
-  Identify implementation assumptions that must be verified against current product behavior and tenant configuration.
-  Explain which parts of the design require safe testing and operational monitoring.
-  Defend the architecture when another engineer asks why.
-  Recognize when another capability should own the requirement instead.

You do **not** need to memorize every current:

- action timeout;
- execution threshold;
- payload field;
- specialized status;
- connector capability;
- template threshold.

You need to know when one of those facts can invalidate your architecture.

Then you verify it.

That is a better engineering habit than memorizing an aging number.

---

## 11. From paper to the lab

The theory course ends here.

The next sequence is practical:

```text
paper architecture
        ↓
verify current product facts
        ↓
build
        ↓
test safely
        ↓
inspect actual behavior
        ↓
monitor
        ↓
compare reality with assumptions
        ↓
revise when needed
```

The paper design does not replace implementation.

It makes implementation deliberate.

Before opening the builder, you should already know:

```text
why Workflow owns the problem

what starts the process

what data you require

what decisions exist

what actions change the world

what failure leaves behind

what repetition and overlap do

what evidence proves success

what facts still need verification
```

Then the builder becomes a representation of decisions you have already made.

Testing also becomes more useful because you know what each test is trying to prove.

And when reality disagrees with the paper design, do not defend the paper.

Update the architecture.

That is engineering.

You followed Priya from her first day through access changes, approvals, governance, failures, operational stress, and eventually her last day.

The course was never really about memorizing a Workflow menu.

It was about learning to reason about automation.

Carry these habits forward:

```text
Choose the right capability.

Inspect rather than assume.

Know what success proves.

Design for repetition and partial failure.

Make uncertainty visible.

Demand evidence for the business outcome.
```

A trustworthy Workflow is not one you assume will never fail.

It is one whose behavior you can explain, observe, recover, and defend.

---

## Official References

- [Workflow Triggers - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-triggers.html)
- [Workflow Actions - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-actions.html)
- [Building Workflows - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-build.html)
- [Managing Native Change Detection - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/sources/native_change_detection.html)
- [Configuring Sources - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/sources/config_sources.html)
- [Outlier Detected - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/outlier-detected/)

---

[← Previous: Module 11 Challenges, Failure Modes & Edge Cases](11-challenges-and-edge-cases.md) | [Course home](README.md)
