# Module 11.2: Scale, Correlation & External State
## 6. Working Engineer: When the design grows

A pattern that works for five subjects can become unsafe for five hundred.

Scale does not create entirely new laws.

It makes your existing assumptions fail more often.

Consider this design:

```text
Scheduled Trigger
        ↓
find identities needing review
        ↓
loop
        ↓
call external service
        ↓
create work
```

At small scale:

```text
10 identities
```

it appears harmless.

Then the population grows.

Now ask:

```text
What if another scheduled run begins
before this one finishes?

What if the loop contains mixed success and failure?

What if an external dependency slows down?

What if every failed subject creates another alert?

What if the returned population or payload is much larger
than the Workflow was designed to handle?
```

That is the Module 11 version of scale.

---

### Do not rebuild the Module 08 limit catalog

Module 08 owns detailed production limits and current operational numbers.

Here the habit is:

> **When volume changes, re-evaluate the architecture and verify the current limits for the Workflow, actions, and tenant involved.**

Do not memorize a number and assume the design is safe because today's population sits just below it.

Ask what the number means for the architecture.

---

### Parallel work changes your reasoning

Parallel Loop work can execute concurrently, and its processing order is not guaranteed.

That matters if loop items touch shared state.

Suppose several iterations update the same external object.

The question is no longer:

> Does each iteration work?

It is:

> What happens when several valid iterations act at the same time?

Similarly, mixed results matter.

If some items succeed and others fail, a later recovery run must not blindly treat the entire population as untouched.

---

### Serial work has a different failure shape

Sequential work avoids some concurrency questions.

It creates another:

```text
item 1 succeeds
item 2 succeeds
item 3 succeeds
item 4 fails
        ↓
later items do not run
```

Now the population is partially processed.

Your recovery design needs to know where truth lives.

---

### Noise is also a scale failure

Return to Acme's aggregation-failure alert.

One source begins failing every hour.

The Workflow sends:

```text
08:00 ALERT
09:00 ALERT
10:00 ALERT
11:00 ALERT
12:00 ALERT
...
```

Eventually the team mutes the channel.

The next genuinely new failure is missed.

Technically, the Workflow delivered messages.

Operationally, the control failed.

A stronger design may model:

```text
source failure begins
        ↓
open / identify incident
        ↓
notify once

same failure continues
        ↓
update / suppress / remind by policy

source recovers
        ↓
close / clear incident state

new failure later
        ↓
new actionable signal
```

That requires state lasting beyond one execution when the business requirement needs it.

Again, do not reduce this to:

```text
if I sent an alert last time,
the Workflow will remember
```

A business incident that spans executions needs an appropriate durable representation.

---

### Scale can change the correct tool

Sometimes the right conclusion is:

```text
This is no longer bounded orchestration.
```

If the design is becoming:

```text
every hour
→ discover a huge population
→ loop everything
→ call several systems
→ maintain large durable processing state
→ reconcile extensive partial results
```

return to Module 09.

Ask whether Workflow should still own that workload.

A supported capability is not automatically the right architecture.

---

## 7. Working Engineer: When one business process crosses executions

Users describe business processes as one thing:

> Priya's access request.

> The Finance certification.

> The offboarding process.

The platform may represent that business process through several independent boundaries.

So learn this explicitly:

```text
ONE BUSINESS PROCESS
        ≠
ONE WORKFLOW EXECUTION
```

That introduces correlation.

---

### Access request example

Consider this business chain:

```text
request submitted
        ↓
decision
        ↓
approved path
        ↓
provisioning
        ↓
provisioning evidence
        ↓
target observation when required
```

Those are different facts.

Do not collapse them.

---

### Manage Access does not wait for the whole business lifecycle

A successful Manage Access action can establish its own documented action boundary.

It does not automatically prove:

```text
every requested item succeeded

approval completed

provisioning completed

target access is independently confirmed
```

The action may also return both:

```text
successfulAccessRequests
failedAccessRequests
```

So important business logic must inspect the result that actually matters.

---

### Approval is another boundary

For an Adaptive Approval design, Approval Policy owns the configured governed decision inside that Workflow.

Once the action completes and the Workflow branches on that decision, do not describe the decision as though it were still pending.

But an approved decision is still not the same thing as provisioning completion.

Keep:

```text
approved
        ≠
provisioned
```

And:

```text
denied path handled successfully
        ≠
access granted
```

A green Workflow execution can be the correct result for a denied request if the Workflow handled the rejection branch exactly as intended.

Again:

> **Green Does Not Mean Granted.**

---

### Provisioning Completed is real evidence

Do not swing too far in the other direction.

Provisioning Completed is meaningful documented ISC/connector provisioning evidence about the provisioning action and its result.

It is not meaningless.

But it is also not necessarily an independent observation of the target application's final business state.

Use the distinction:

```text
Provisioning Completed

→ meaningful provisioning evidence
  within its documented boundary

Independent target observation

→ different/stronger evidence
  when the control specifically requires
  proof of final target state
```

Match the evidence to the claim you need to make.

---

### Certification: correlation over time

A certification is another useful example because its lifecycle naturally crosses boundaries.

Conceptually:

```text
campaign creation
        ↓
generation / readiness
        ↓
activation
        ↓
review activity
        ↓
certification sign-off
        ↓
campaign end
        ↓
remediation / target evidence where required
```

Do not turn those into synonyms.

---

#### Creation and activation are distinct boundaries

The stable teaching rule is:

```text
CAMPAIGN CREATION
        ≠
CAMPAIGN ACTIVATION
```

The current Create Certification Campaign action can be configured to start the campaign when it is created.

If that option is not used, activation can be a later explicit lifecycle step.

So do not memorize:

```text
Create
→ always Activate separately
```

Learn the boundary instead.

Know what the configured design actually does.

---

#### Do not assume campaign creation is idempotent

Current Workflow action documentation does not document an idempotency guarantee for Create Certification Campaign.

Therefore:

> **Do not assume one.**

That is different from claiming:

> Create Certification Campaign is definitely non-idempotent.

The first statement respects the documented contract.

The second invents a guarantee about behavior we do not have.

If duplicate campaign creation would be harmful, the design needs deliberate correlation and duplicate-control reasoning.

---

#### Durable correlation

Suppose Workflow A creates a campaign.

A later Workflow reacts to another certification lifecycle event.

How does the later execution know:

> This event belongs to the Finance mover process we started for Priya.

The technical campaign or certification identifiers available at the relevant lifecycle boundaries are far stronger correlation values than:

```text
"Finance Review"
```

or:

```text
Priya's display name
```

A later execution can use appropriate technical identifiers plus current authoritative state to understand which governance object it is handling.

The larger lesson is reusable:

```text
BUSINESS PROCESS
        ↓
may create durable business/platform object
        ↓
later event references that object
        ↓
later Workflow correlates and re-reads state
```

That is how work survives beyond one execution.

---

#### Certification Signed Off is not Campaign Ended

One campaign can contain more than one certification.

Therefore:

```text
Certification Signed Off
        ≠
Campaign Ended
```

One reviewer finishing one certification does not prove everyone is finished.

And even:

```text
Campaign Ended
```

does not automatically prove:

```text
every target-side remediation
has been independently observed
```

Follow the evidence chain only as far as each boundary allows.

---

#### Work It Out

Acme creates a Finance certification for Priya.

The campaign exists.

Later one reviewer signs off with a revoke decision.

Another reviewer has not finished.

An engineer says:

> The certification is done, so the access should be gone.

Identify at least three boundary errors.

First, one Certification Signed Off event is certification-level evidence, not whole-campaign completion.

Second, campaign lifecycle completion and remediation are separate concerns.

Third, remediation evidence and independent target-state evidence can be different boundaries.

The design should correlate later work to the correct campaign/certification technical object, re-read authoritative governance state when needed, and make only the claim that the available evidence supports.

---

## 8. Working Engineer: When the source or caller cannot support your assumption

Many production failures begin with an assumption that looked small.

Two common forms are:

```text
the caller sent the field
        ↓
therefore the value must be trustworthy
```

and:

```text
ISC discovered the account
        ↓
therefore ISC can perform the desired action on it
```

Neither is safe.

---

### External Trigger crosses a trust boundary

Suppose Acme's HR system starts a Workflow using External Trigger.

It sends:

```json
{
  "eventId": "hr-00421",
  "eventType": "SEPARATION_FILED",
  "workerId": "W-18422"
}
```

The invocation may be authenticated.

That establishes an authentication boundary.

It does not establish every business fact inside the payload.

Keep these distinctions:

```text
authenticated caller
        ≠
business data is correct

basic type is valid
        ≠
business value is valid

external worker identifier
        ≠
ISC technical identity identifier

valid request
        ≠
safe to execute twice
```

---

### Validation has layers

A useful sequence is:

```text
STRUCTURE
Does the field exist?
Does it have the expected basic type?

        ↓

BUSINESS VALUE
Is this eventType allowed?
Is this date meaningful?
Is this reasonCode accepted?

        ↓

IDENTITY RESOLUTION
Does W-18422 map to exactly
the intended ISC identity?

        ↓

AUTHORIZATION
Is this business operation allowed
for this caller/context?

        ↓

REPEAT SAFETY
Has this stable business event
already produced the intended side effect?
```

Verify Data Type helps with the first layer.

Its job is not to prove all the later layers.

A string can be the wrong string.

---

### Identifier confusion is dangerous

This mistake is easy because many objects are called `id`.

```text
HR worker id
        ≠
ISC identity id

source-native account identifier
        ≠
ISC account object id

external case id
        ≠
campaign id
```

Do not make them interchangeable because their JSON fields have the same name.

Resolve identifiers deliberately.

Missing or ambiguous resolution deserves a deliberate branch.

---

### Source capability is another gate

Now suppose Acme discovers Priya's accounts and wants to disable them.

This reasoning is wrong:

```text
Get Accounts found account
        ↓
therefore automatic Disable is supported
```

Discovery and action capability are different questions.

Use:

```text
ACCOUNT EXISTS
        ↓
What source owns it?
        ↓
Does that source/configuration support
the required operation?
        |
        +---- yes → eligible automatic path
        |
        +---- no  → manual / escalation path
```

This is especially important for destructive automation.

An unsupported account should not silently disappear from the success count.

It needs ownership.

---

### The reusable principle

```text
DATA EXISTS
        ≠
DATA IS AUTHORITATIVE

OBJECT EXISTS
        ≠
ACTION IS SUPPORTED
```

Those two statements prevent a surprising number of bad automations.

---

## 9. Advanced: When a signal looks stronger than it really is

Security signals can make engineers overconfident because the event sounds serious.

Two good examples are:

- Native Change;
- Outlier Detected.

They represent different security conditions.

But they share one crucial lesson:

> **Signal does not automatically equal verdict.**

---

### Native Change: detected change is not intent

Suppose Acme detects that Priya's Active Directory account was directly added to:

```text
Finance Privileged Operators
```

outside ISC.

A Native Change event can establish that an out-of-band account change was detected through the configured Native Change Detection boundary.

That is important security evidence.

But keep the chain precise:

```text
detected out-of-band change
        ≠
malicious change
        ≠
unauthorized change
        ≠
automatic authorization
for destructive remediation
```

The change could represent:

- malicious activity;
- a documented emergency grant;
- break-glass procedure;
- manual operational work;
- another approved external process.

The event tells you what changed.

It does not read the administrator's mind.

---

#### Priya's emergency-access scenario

During an outage, the AD team directly adds Priya to:

```text
Finance Privileged Operators
```

under an approved emergency process.

Later aggregation detects the native change.

A Workflow automatically revokes the addition.

The Workflow is green.

Security says:

> Good. The Workflow fixed the unauthorized change.

There are two problems.

First:

```text
Native Change detected
```

did not prove:

```text
unauthorized
```

Second:

```text
Workflow green
```

did not prove:

```text
the chosen business response was correct
```

The automation may have successfully performed the wrong policy decision.

---

#### A safer response shape

For high-impact signals:

```text
detect
        ↓
classify
        ↓
gather required context
        ↓
apply explicit Acme policy
        ↓
notify / ticket / investigate
        ↓
remediate only when authorized
```

Automatic remediation may be appropriate.

But it needs stronger proof than:

> An event fired.

Ask:

- What exact change occurred?
- What current state exists?
- What policy says about this case?
- Are emergency exceptions possible?
- Does the source support the action?
- What happens if remediation repeats?
- What evidence proves the intended correction?

That is Advanced reasoning.

---

### Outlier: risk signal is not security judgment

Outlier Detected gives a different kind of signal.

It indicates unusual access/risk information according to the supported outlier capability.

Do not translate that directly into:

```text
malicious identity
```

or:

```text
this entitlement is definitely unauthorized
```

Instead:

```text
OUTLIER SIGNAL
        ↓
potential risk / unusual access

        +

ACME POLICY
        +

current business/security context

        ↓
authorized response
```

The response may be:

- notify;
- investigate;
- create governed review;
- escalate;
- perform explicitly authorized containment.

The correct action comes from policy and context.

Not from the existence of the score alone.

---

#### Do not memorize somebody else's threshold as your policy

Product templates can demonstrate supported response patterns.

They are examples.

They do not automatically become Acme's security policy.

If an exercise says:

> Acme policy routes this Outlier signal to certification.

then certification is the scenario response because **Acme adopted that rule for the scenario**.

The reusable lesson is:

```text
signal
        ↓
policy interpretation
        ↓
authorized response
```

not:

```text
memorized number
        ↓
universal response
```

---

### Native Change and Outlier side by side

Keep the comparison simple:

```text
NATIVE CHANGE

Evidence:
an out-of-band account change
was detected at that boundary.

Does not by itself prove:
malicious intent
or unauthorized intent.
```

```text
OUTLIER

Evidence:
ISC supplied the documented
risk/outlier signal.

Does not by itself prove:
malicious intent
or one specific unauthorized entitlement.
```

Both require judgment.

Both can lead to destructive action if designed poorly.

Both deserve:

- explicit policy;
- current context;
- source-capability checks;
- repeat-safety thinking;
- recovery planning;
- appropriate business-outcome evidence.

---

### Green still does not mean risk resolved

Suppose an Outlier Workflow creates a certification successfully.

You can safely say:

```text
the configured campaign-creation boundary
completed according to its action contract
```

You cannot jump to:

```text
risky access was removed
```

Between those claims may be:

```text
campaign lifecycle
        ↓
review
        ↓
decision
        ↓
remediation
        ↓
target-state evidence
```

A security Workflow becomes dangerous when its language outruns its evidence.

---

## 10. Production reality: Testing does not remove these questions

Module 07 taught you how to test and debug Workflows.

Keep doing that.

But do not assign testing a job it cannot perform.

A passing test can show that:

- a tested input followed the intended path;
- the tested JSONPath worked for that data;
- selected conditions produced the expected branch;
- simulated or enabled actions behaved as observed.

It cannot prove the permanent absence of:

- production races;
- every schedule overlap;
- every dependency outage;
- every ambiguous external result;
- production-scale behavior;
- every future source capability difference;
- every combination of two executions touching shared state.

That does not make testing weak.

It means:

```text
TESTING
        +
SAFE DESIGN
        +
MONITORING
        +
RECOVERY
        +
RECONCILIATION WHERE NEEDED
```

work together.

A production system is not safe because you discovered every possible failure in advance.

It is safer because the failures you did not predict still have bounded consequences and visible recovery paths.

---

## 11. Production Stress-Test Exercise

Now take one of the familiar patterns from Module 10.

Acme's leaver coordination pattern is:

```text
Identity Lifecycle State Changed
        ↓
qualify the leaver transition
        ↓
retrieve required context
        ↓
notify Security
        +
create Facilities ticket
```

Assume the architecture decision is already correct.

Workflow belongs here.

Your job is not to redraw the canvas.

Your job is to attack the design.

Write your own answers.

---

### REPEAT

```text
What could cause this business work
to become relevant again?

What happens to the notification?

What happens to the ticket?

Which repeated operations are harmless?

Which can multiply side effects?
```

Your answer:

```text
REPEAT:
...
```

---

### OVERLAP

```text
Could another execution touch Priya
while this one is running?

Could two executions both believe
they should create the same ticket?

What state could become stale?
```

Your answer:

```text
OVERLAP:
...
```

---

### PARTIAL

```text
What if the Security notification succeeds
and ticket creation fails?

What if ticket creation succeeds
but later confirmation fails?

Where would recovery resume?
```

Your answer:

```text
PARTIAL:
...
```

---

### DEPEND

```text
What if Facilities' ticketing system
is unavailable?

What if the request outcome is ambiguous?

Which failure stops the process?
Which one escalates?
Which one waits for reconciliation?
```

Your answer:

```text
DEPEND:
...
```

---

### SCALE

```text
What if a large population of leavers
is processed during a reorganization?

What if a scheduled recovery process overlaps?

At what point should the design
be reconsidered as bulk processing?
```

Your answer:

```text
SCALE:
...
```

---

### INTERPRET

```text
What does the lifecycle event actually prove?

Does it prove the Facilities ticket was completed?

Does a green Workflow prove offboarding is finished?

Which business outcomes remain outside
the Workflow's success boundary?
```

Your answer:

```text
INTERPRET:
...
```

---

### CORRELATE

Only if your design continues in later executions:

```text
What durable object or technical identifier
connects later work back to this offboarding?

Where does authoritative state live?

How does recovery know which business process
it is continuing?
```

Your answer:

```text
CORRELATE:
...
```

---

Do not compare your answers against a memorized canvas.

Instead ask whether you found the dangerous assumptions.

A strong Module 11 answer should identify things such as:

```text
duplicate side effect

stale state

concurrent check-then-act race

partial completion

ambiguous remote outcome

unsupported target action

cross-execution correlation

signal stronger than its evidence

business outcome beyond Workflow success
```

You are now evaluating the design, not merely describing it.

---

## 12. Checkpoint: Ready to design independently

You should now be able to take a Workflow pattern that looks correct on the happy path and stress it deliberately.

Ask:

```text
REPEAT
What if this business situation is processed again?

OVERLAP
What if another execution acts at the same time?

PARTIAL
What if some side effects already succeeded?

DEPEND
What if another system is slow, unavailable,
ambiguous, or incapable?

SCALE
What changes when the population grows
or schedules overlap?

INTERPRET
What does this event or result actually prove?

CORRELATE
If work continues later,
how does the later execution know
which process it belongs to?
```

You should also be able to explain these distinctions:

```text
current-state check
        ≠
concurrency-safe idempotency guarantee

retry
        ≠
recovery

local failure
        ≠
remote side effect definitely failed

approved
        ≠
provisioned

Provisioning Completed
        ≠
independent target observation

campaign created
        ≠
review complete

Certification Signed Off
        ≠
Campaign Ended

signal
        ≠
verdict

account discovered
        ≠
action capability established

green execution
        ≠
business outcome proven
```

Most importantly, this question should now feel automatic:

> **If this happens twice, does the system still end in the correct state?**

If your answer is:

> I do not know yet.

that is not failure.

That is an engineering finding.

Now you know which assumption has to be solved before production.

---

## From stress-testing to paper design

You have reached the final transition in the theory course.

```text
Module 09
Should Workflow participate?

        ↓

Module 10
What reusable Workflow shape fits?

        ↓

Module 11
How does that shape fail
under production stress?

        ↓

Module 12
Design the complete solution deliberately
before opening the builder.
```

Module 12 will bring the course together.

You will take the trigger, data, decisions, actions, boundaries, failure handling, repeat safety, evidence, and operating assumptions and turn them into a complete paper design.

At this point, you should no longer look at a clean Workflow diagram and ask only:

> Does the happy path work?

You should ask:

> What assumptions have to remain true for this design to stay correct?

That is the difference between recognizing a Workflow pattern and engineering one.

---

## Official References

- [Workflow Triggers - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-triggers.html)
- [Workflow Operators - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-operators.html)
- [Workflow Actions - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-actions.html)
- [Managing Workflows - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-manage.html)
- [Event Trigger Types - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/trigger-types/)
- [Provisioning Completed - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/provisioning-completed/)
- [Campaign Generated - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/campaign-generated)
- [Native Change Detection - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/sources/native_change_detection.html)
- [Native Change Account Updated - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/native-change-account-updated/)
- [Outlier Detected - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/outlier-detected/)

---

[← Previous: Module 11.1: Repetition, Partial Failure & Concurrency](11-1-repetition-partial-failure-and-concurrency.md) | [Course home](README.md) | [Next: Module 12.1: Paper Design Framework →](12-1-paper-design-framework.md)
