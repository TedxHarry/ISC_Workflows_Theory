# Module 07: Testing, Debugging & Execution

Module 06 ended with a question:

> **The Workflow ran. What actually happened?**

That question sounds simple until something goes wrong.

Priya moves into Finance, but her manager does not receive the expected message.

An access request is approved, but Priya still cannot use the application.

A Workflow shows green, but one item inside an action did not succeed.

Or perhaps there is no Workflow execution at all.

The weak debugging method looks like this:

```text
something is wrong
        ↓
open the Workflow
        ↓
change a few things
        ↓
test again
        ↓
hope
```

That is not debugging. It is guessing with extra steps.

A better method starts with evidence.

```text
What did I expect?
        ↓
What actually happened?
        ↓
Where do those two first stop matching?
```

That **first divergence** is where diagnosis begins.

By the end of this module, I want you to have one repeatable method you can use whether the problem involves a trigger, a missing value, a branch, an action, an approval, provisioning, or an outside system.

---

## 1. Why debugging needs an order

Suppose Acme reports:

> “Priya's Finance onboarding Workflow is broken.”

That statement does not tell you much.

Maybe the Workflow never started.

Maybe it started with different data than expected.

Maybe the data was correct but a comparison took the wrong path.

Maybe the correct action ran and returned a problem in its result.

Maybe everything inside the Workflow worked and the unfinished part belongs to provisioning or the target application.

Those are different problems.

If you begin at the final symptom, every step looks suspicious.

Instead, write down two things.

```text
EXPECTED
What did I believe would happen?

OBSERVED
What evidence do I actually have?
```

Then ask:

> **Where is the first place those two differ?**

If the trigger input is already wrong, there is little value debugging the fifth action.

If the trigger input and first four steps are correct, there is little value rewriting the trigger.

If approval is already proven, stop treating approval as the unresolved problem.

That sounds obvious when written out.

Under pressure, engineers violate it constantly.

---

## 2. Core — Test safely before trusting the result

Before we diagnose a Workflow, we need evidence.

Testing is one way to create that evidence.

But there is an important safety rule:

> **A Workflow test is not automatically a harmless rehearsal.**

Enabled actions can actually execute.

That matters when an action can:

- send a message;
- create something;
- request or remove access;
- change an account;
- call another system;
- otherwise affect real tenant state.

### Simulated testing

Simulated Testing lets you choose actions that should use simulated behavior instead of performing their normal action.

Conceptually:

```text
step enabled during simulated testing
        ↓
action executes normally
```

versus:

```text
step disabled during simulated testing
        ↓
action is simulated
        ↓
mock output can support later testing
```

That means you can exercise the surrounding Workflow logic while keeping a dangerous action from changing real state.

But simulated output still matters.

Suppose you simulate a step that normally produces an identity ID, and the next **enabled** action depends on that ID.

A placeholder that cannot be used by the enabled downstream action does not give you a meaningful test.

Use safe, meaningful tenant data appropriate to what you are testing, and make simulated output usable when later enabled steps depend on it.

A sandbox tenant remains the safest environment for testing because real actions that do execute are acting on test identities, accounts, access, and integrations rather than production objects.

### Use test data that resembles the real event

You learned this habit in Module 02:

> **Inspect the data you actually have.**

Testing deserves the same discipline.

If you are testing Priya's mover logic, use data shaped like the event the Workflow was designed to receive.

For example:

```json
{
  "identity": {
    "type": "IDENTITY",
    "id": "<SAFE_TEST_IDENTITY_ID>",
    "name": "workflow.test"
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

Use a safe identity that makes sense for the test rather than assuming any arbitrary identifier will behave meaningfully throughout the execution.

### One important boundary

A successful manual or simulated test can prove useful things about:

- the supplied data;
- references;
- branches;
- rendered values;
- selected action behavior.

It does **not** prove that the real production event will later occur, be detected, qualify for the trigger, and start the Workflow.

Keep those facts separate:

```text
test execution succeeds
        ≠
real production event delivery proven
```

Testing proves what you actually exercised.

Nothing more.

---

## 3. Core — The five diagnostic questions

This is the method I want you to carry out of this module.

```text
1. Did the Workflow start?
        ↓
2. What data actually arrived?
        ↓
3. Where did the first unexpected value appear?
        ↓
4. What did that action actually guarantee?
        ↓
5. Which system or process owned the next boundary?
```

Do not treat these as five unrelated troubleshooting tips.

They are an order.

You move forward only when the earlier boundary has enough evidence.

A slightly wider view looks like this:

```text
BUSINESS / TARGET EVENT
Did the thing we care about actually happen?
        ↓
EVENT DETECTION
Did ISC detect the relevant event?
        ↓
WORKFLOW START
Did the trigger qualify and create an execution?
        ↓
INPUT
Did the expected data arrive?
        ↓
LOGIC
Did runtime values produce the expected path?
        ↓
ACTION
What result or Error did the step actually produce?
        ↓
HUMAN / PROCESS
Did the next governed or human process complete?
        ↓
DOWNSTREAM SYSTEM
Which system now owns the next fact?
        ↓
TARGET STATE
Is the intended business state independently confirmed?
```

You do not need to memorize that whole ladder.

The five questions are enough to navigate it.

---

## 4. Core — Question 1: Did the Workflow start?

Start with the simplest distinction:

```text
no execution
```

versus:

```text
execution exists
```

If an execution exists, the Workflow started.

Now you have runtime evidence to inspect.

If no execution exists for the situation you expected, stay at or before the start boundary.

Do **not** immediately decide:

> “The filter is wrong.”

A missing execution does not tell you why the Workflow did not start.

Several boundaries may exist before execution:

```text
business event happened
        ≠
ISC detected the event
        ≠
Workflow trigger qualified
        ≠
Workflow execution started
```

The right next question depends on the trigger family.

You may need to determine:

- whether the event actually occurred;
- whether ISC detected the event;
- whether the Workflow was enabled and eligible to receive it;
- whether required trigger conditions were satisfied;
- whether the filter allowed that event instance to qualify.

Notice the discipline:

> **No execution means stay upstream.**

Do not debug downstream actions in a Workflow that has no execution.

### Execution status is a clue, not the whole diagnosis

Once an execution exists, its overall status helps orient you.

Current Workflow execution states include:

```text
Completed
Failed
Canceled
Queued
Running
```

A failed execution and a Workflow that never started are completely different diagnostic situations.

But even `Completed` is only the beginning of the investigation when the business result is wrong.

You already know why:

> **Green Does Not Mean Done.**

---

> **Work It Out**
>
> Acme expects a Workflow to react to an event this morning. Nobody sees the expected notification, and no Workflow execution can be found.
>
> An engineer immediately rewrites the trigger filter.
>
> What is wrong with that debugging move?
>
> <details>
> <summary>Check your answer</summary>
>
> The engineer has skipped the start boundary.
>
> No execution proves only that there is no Workflow execution to inspect. It does not prove the filter caused that outcome.
>
> First determine whether the relevant event occurred or was detected, whether the Workflow was eligible to start, and whether the trigger conditions were satisfied. Filtering becomes one possible boundary inside that investigation.
>
> The useful rule is:
>
> ```text
> no execution
> → stay upstream
> ```
>
> Do not change downstream logic or blame one start condition without evidence.
>
> </details>

---

## 5. Core — Question 2: What data actually arrived?

Once an execution exists, resist the urge to jump to the step that looks broken.

Start with the real input.

You learned in Module 02 that a Workflow cannot use data merely because you expected it to exist.

That becomes a debugging rule now:

> **Do not debug the value you imagined. Debug the value the execution actually received.**

Ask:

- Is the field present?
- Is it missing?
- Is it null?
- Is it empty?
- Is it the type you expected?
- Does an array contain the item you expected?
- Is the value usable for the next step?

### Priya's mover event

Suppose the Workflow is intended to run when Priya moves from Sales to Finance.

The execution exists.

Before examining the later branch, open the trigger input.

You expect the `changes` data to show something conceptually like:

```text
attribute: department
oldValue: Sales
newValue: Finance
```

If the real input says something else, you have already found an important divergence.

The problem is not yet the comparison.

The comparison can only evaluate what it received.

### Optional data is still optional at runtime

Now imagine an onboarding Workflow needs manager information.

An Identity Created event can contain identity attributes that ISC knows at that point, but you should not assume every optional attribute is present and usable in every execution.

So the diagnostic method is:

```text
inspect actual event data
        ↓
validate the value you need
        ↓
retrieve current ISC-known information if required
        ↓
still handle missing or unusable data deliberately
```

A lookup does not manufacture information ISC does not know.

That is why validation remains useful even when a Get Identity step exists.

---

> **Work It Out**
>
> Priya's onboarding Workflow starts successfully, but the manager-related path does not behave as expected.
>
> The engineer says:
>
> “The trigger should have manager information, so the comparison must be broken.”
>
> What do you inspect first?
>
> <details>
> <summary>Check your answer</summary>
>
> Start with the real trigger input.
>
> Determine whether usable manager data actually arrived before changing the comparison.
>
> If the Workflow later retrieves current identity data, inspect that result too. A lookup can tell you what ISC currently knows; it does not guarantee that previously missing source or relationship data now exists.
>
> The first divergence might therefore be the data boundary rather than the logic boundary.
>
> </details>

---

## 6. Core — Question 3: Where did the first unexpected value appear?

Now walk the execution **in order**.

Execution history is your black box recorder.

For a Workflow execution, you can use its playback and runtime evidence to see what went into steps and what came out.

The goal is not to inspect every step forever.

The goal is to find the first place where:

```text
expected value
        ≠
observed value
```

Once you find that point, stop walking forward.

Later symptoms may simply be consequences.

### Priya's blank welcome message

Suppose Priya receives a message that effectively renders as:

```text
Welcome to Acme,
```

You expected:

```text
Welcome to Acme, Priya
```

Do not immediately decide:

> “JSONPath is wrong.”

The blank value tells you where to investigate, not yet why it happened.

Open the execution and compare the evidence.

Ask:

1. Did the source step actually contain Priya's first name?
2. Did the later step reference the correct value?
3. Was the reference or expression valid for the environment where it ran?
4. What value actually rendered at runtime?

Imagine the trigger input clearly contains Priya's first name, but the later input references a different location.

Now you have evidence for a reference/path problem.

That is much stronger than guessing from the empty message.

### Rendered values are often more useful than the expression you remember writing

The canvas tells you what you intended.

Execution playback tells you what that execution actually ran with.

That distinction matters even more when a Workflow has been edited since the historical execution occurred.

When diagnosing an old run, reason from the evidence associated with **that execution**, not only from what the current canvas looks like today.

### Comparisons work the same way

Suppose a comparison takes the unexpected branch.

Do not begin by replacing the operator.

First inspect the exact runtime values that reached it.

Maybe one value is missing.

Maybe the wrong field was selected.

Maybe whitespace, casing, formatting, or another representation differs from what you expected.

Do not assume undocumented normalization behavior.

Read the rendered values and diagnose from evidence.

---

> **Engineering Habit:** Walk forward until the first unexpected value or state. Once you find it, stop blaming later steps until you understand that divergence.

---

## 7. Core — Question 4: What did that action actually guarantee?

This is where Module 05 becomes a debugging skill.

When a step looks green, ask:

> **What did this action actually complete?**

Do not translate:

```text
green
```

into:

```text
the entire business requirement succeeded
```

An action can produce several kinds of evidence.

### Native action Error

With Error handling enabled, an action can take its native Error path.

That is a technical action-execution problem.

Read the execution's Error evidence.

Do not turn every unwanted business result into a technical Error.

### Normal result containing a problem signal

Some actions can complete normally while their documented output tells you that part of the requested work did not succeed.

**Manage Access** is the clearest example.

Its result includes:

```text
successfulAccessRequests
failedAccessRequests
```

Those fields matter more than the color alone.

A Manage Access step can complete while one or more requested items appear in `failedAccessRequests`.

So:

```text
Manage Access step completed
        ≠
every requested item succeeded
```

And even `successfulAccessRequests` is easy to overread.

It does **not** mean:

```text
approved
```

It does **not** mean:

```text
provisioned
```

It does **not** mean:

```text
confirmed live on the target
```

Keep the ladder explicit:

```text
successfulAccessRequests
        ≠
approval completed
        ≠
provisioning completed
        ≠
target state independently confirmed
```

That is Green Does Not Mean Done applied as diagnosis.

### Normal business result

A Workflow may also reach a perfectly valid business outcome that is not the outcome one person hoped for.

A governed approval may result in rejection.

That is not automatically a broken Workflow.

A human step may follow its documented non-response contract.

That is not automatically the same thing as a generic action failure.

Classify the result before trying to “fix” it.

---

> **Work It Out**
>
> Priya's offboarding execution is `Completed`.
>
> The Manage Access step is also green.
>
> A reviewer later finds one access item that should have been removed but was not.
>
> Where do you start?
>
> <details>
> <summary>Check your answer</summary>
>
> Do not start by rewriting the trigger or assuming the whole access-removal action succeeded.
>
> Open the Manage Access result and inspect both `successfulAccessRequests` and `failedAccessRequests`.
>
> If the relevant removal appears in `failedAccessRequests`, the first divergence is already inside the action result.
>
> If the request appears successful at the Manage Access boundary, move forward to the later approval or provisioning boundary instead of assuming the target state is already proven.
>
> </details>

---

## 8. Core — Question 5: Which system or process owned the next boundary?

This question prevents endless Workflow debugging after the Workflow has already done its job.

Return to Priya's Finance request.

Suppose the approval Workflow ran and produced an approved result.

Priya still cannot use the Finance application.

What is proven?

```text
approval completed
```

What is not yet proven?

```text
provisioning completed
target access confirmed
```

Do not restart at the trigger.

Do not change the approval policy merely because the final application state is wrong.

The unresolved fact belongs later in the process.

Move to provisioning evidence.

A **Provisioning Completed** event can provide meaningful evidence about provisioning activity, warnings, errors, account requests, and provisioning results.

That is stronger evidence than approval alone.

But keep the final boundary distinct:

```text
Provisioning Completed
        ≠
independent confirmation of current target state
```

If the business requirement demands certainty that Priya can actually use the Finance application, the next evidence must come from the target side or another independent confirmation mechanism.

### Once a boundary is proven, move forward

This is an engineering habit worth making explicit.

```text
trigger data is correct
→ stop rewriting the filter without evidence

comparison input is correct
and branch is correct
→ stop debugging the trigger

approval is proven
→ stop treating approval as unresolved

Workflow sent the expected request
and received the expected response
→ investigate the next system boundary
```

Do not move backward merely because the final symptom is emotionally attached to the Workflow.

Evidence decides where you work next.

### Human non-response follows the same rule

Module 06 established that human mechanisms do not share one universal non-response rule.

So if a person never responded, do not conclude:

```text
human did not respond
→ generic Workflow failure
```

Ask:

> What does this specific mechanism's documented non-response contract say happened?

A Form, an Interactive Form, and an approval policy can represent non-response differently.

Module 07 diagnoses the result.

It does not invent a new universal timeout rule.

---

## 9. Core — Classify the first divergence

Once you have found the first point where evidence differs from expectation, give the problem a useful class.

| First evidence | Likely class | Next reasoning move |
|---|---|---|
| No execution | Start / event boundary | Determine whether the event occurred or was detected and whether the Workflow qualified |
| Trigger data differs | Data boundary | Work from the real payload and validate what is missing or different |
| Rendered value differs | Data-reference / logic boundary | Trace the value backward to its source |
| Action enters Error | Native action failure | Read the actual Error evidence and the action contract |
| Action is green but output reports failed items | Normal result with problem signal | Read the documented result instead of trusting color |
| Human interaction does not end as expected | Human/process boundary | Apply that mechanism's own contract |
| Approval is complete but access is absent | Downstream process boundary | Move to provisioning evidence |
| Provisioning evidence exists but target state is still wrong | Target/external boundary | Investigate the system that now owns the state |

This classification is not a troubleshooting catalog.

You still locate the divergence first.

Classification only helps you decide what kind of evidence comes next.

---

## 10. Core — One hypothesis, one change, one safe retest

Once you find the first divergence, form one explanation that fits the evidence.

Then change one thing.

```text
observe
        ↓
form one hypothesis
        ↓
change one thing
        ↓
retest safely
        ↓
compare the new evidence
```

Why one thing?

Because if you change the trigger filter, JSONPath, comparison, and action input at the same time and the Workflow starts working, you have learned almost nothing.

You do not know which assumption was wrong.

That makes the next incident harder.

### Do not blindly rerun side-effecting work

Sometimes the proposed “retest” is a rerun of a Workflow that already executed halfway.

Before doing that, ask:

> **What already happened?**

Suppose the Workflow already created something, changed access, or sent a request before failing later.

A second full run does not start from a clean mental slate merely because you pressed Run again.

For Module 07, carry this safety rule:

> **If earlier side effects may already have happened, determine what occurred before rerunning the whole process.**

Later in the course we will go deeper into replay, idempotency, duplicate effects, correlation, and concurrency.

For now, do not create a second incident while fixing the first one.

---

## 11. Working Engineer — Apply the same method to harder boundaries

The five questions are valuable only if they transfer.

Here are three situations that look very different but use the same method.

### Native Change — add the upstream detection boundary

Suppose someone adds `Finance Privileged Operators` directly to an AD account.

Acme expects a Native Change Workflow to react.

No execution appears.

Do not start by editing the Workflow.

Native Change adds an important upstream question:

```text
target change happened
        ↓
did ISC detect it?
        ↓
did the Workflow start?
```

Native Change Detection depends on the relevant source configuration and aggregation boundary.

So diagnosis stays upstream until detection is established.

If an execution **does** exist, continue normally:

```text
What account/change data arrived?
        ↓
Where did the first unexpected value appear?
        ↓
What did remediation actually prove?
        ↓
What evidence owns the current target state?
```

Also keep attribution narrow.

If the account is not correlated to a real identity, do not convert a technical account-change signal into a confident statement about a known human owner or actor.

```text
technical change detected
        ≠
human intent proven
        ≠
authorization proven
```

Native Change is not a different debugging method.

It is the same method with an extra detection boundary before the Workflow.

---

> **Work It Out**
>
> A sensitive group is added directly to an AD account, but no Native Change Workflow execution appears.
>
> What should you *not* debug yet?
>
> <details>
> <summary>Check your answer</summary>
>
> Do not start with downstream Workflow actions or remediation logic.
>
> First establish the upstream evidence: did the target change occur, did ISC detect it through the relevant Native Change/aggregation boundary, and did the Workflow then qualify to start?
>
> Only after an execution exists should you debug the data and later Workflow steps.
>
> </details>

---

### Access request — follow the business boundaries

Priya requests sensitive Finance access.

The request goes through its governed approval process.

The approval Workflow completes with an approved result.

The next day Priya still cannot use the application.

Walk the five questions.

#### 1. Did the Workflow start?

Yes.

You have the approval Workflow execution.

#### 2. What data arrived?

The request data is present and corresponds to Priya's Finance request.

#### 3. Where did the first unexpected value appear?

So far, nowhere inside the approval execution.

#### 4. What did the action actually guarantee?

The approval process reached an approved result.

That proves the approval boundary.

#### 5. Who owns the next boundary?

Provisioning.

And after provisioning evidence:

the target system.

The useful conclusion is:

```text
approval is proven
→ stop debugging approval
→ move forward
```

That is systematic diagnosis.

### HTTP integration — separate Workflow evidence from remote-system evidence

Suppose Acme's separation Workflow should create a case in an external security platform.

The Workflow starts.

Its trigger input is correct.

Validation and branching are correct.

Then you reach **HTTP Request**.

At that point, inspect what the action actually returned or what Error evidence the execution recorded.

Do not create a universal rule such as:

```text
HTTP status X
→ always means one specific Workflow outcome
```

Read the actual execution.

If HTTP Request entered Error, diagnose the action and remote response from that evidence.

If it returned the expected Workflow-side result but the security case is still absent, the unresolved fact has moved outside the Workflow.

```text
Workflow request evidence
        ↓
remote system response
        ↓
remote business state
```

Again, the method did not change.

Only the owner of the next boundary changed.

---

## 12. Advanced — What this module is deliberately not solving yet

At this point you know how to diagnose **one execution**.

That does not yet make you responsible for every production-operations problem around the Workflow.

Module 08 will deal with questions such as:

- ownership;
- production monitoring;
- retention strategy;
- limits;
- promotion;
- credentials and secrets;
- maintenance over time.

And later modules will go deeper into:

- replay;
- idempotency;
- duplicate side effects;
- concurrency;
- race conditions;
- durable correlation;
- reconciliation.

You have already seen why those ideas matter.

For now, your responsibility is narrower:

```text
find what actually happened
        ↓
locate the first divergence
        ↓
classify the boundary
        ↓
form one evidence-based hypothesis
```

That is enough to make debugging dramatically less random.

---

## 13. Work It Out — Full diagnosis

Priya requests a Finance access profile.

You are told:

> “The Workflow worked, but she still has no access.”

You find the following evidence:

```text
Access-request approval Workflow:
Completed

Approval result:
Approved

Provisioning evidence:
contains an error for the Finance source
```

An engineer proposes changing the approval logic.

Walk the diagnosis.

<details>
<summary>Check your answer</summary>

Start with what is already proven.

```text
Did the Workflow start?
→ Yes

What data arrived?
→ The expected Finance request

Where is the first unexpected state?
→ Not in the approval Workflow

What did the approval guarantee?
→ The governed approval reached Approved

Which process owns the next boundary?
→ Provisioning
```

The first relevant divergence is in the provisioning evidence.

Changing the approval logic would move backward without evidence.

Investigate the Finance provisioning problem.

Only return to the approval Workflow if new evidence points back there.

</details>

---

## 14. Checkpoint — Diagnose before you redesign

You should now be able to take a Workflow incident and walk it systematically rather than changing random steps.

Given an expected business event, you should be able to ask:

```text
1. Did the Workflow start?

2. What data actually arrived?

3. Where did the first unexpected value or state appear?

4. What did the relevant action or human process actually prove?

5. Which system or process owned the next unproven fact?
```

You should also be able to turn the answer into a controlled debugging loop:

```text
expected
        ↓
observed
        ↓
first divergence
        ↓
one hypothesis
        ↓
one change
        ↓
one safe retest
```

And you should know when **not** to keep debugging the Workflow.

If approval is already proven, move to provisioning.

If provisioning evidence is already proven, move to the target state.

If an external system now owns the missing fact, investigate that system.

If there is no execution, stay upstream.

That is the habit I want you to carry forward:

> **Debug from evidence, and stop at the first place reality differs from expectation.**

Module 08 changes the scale of the problem.

You now know how to diagnose one execution.

Next we ask how to operate the Workflow itself as a production asset over time.

---

## Official References

- [Workflows — SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/index.html)
- [Building Workflows — SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-build.html)
- [Creating Data for Testing Workflows — SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-test-data.html)
- [Managing Workflows — SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-manage.html)
- [Workflow Actions — SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-actions.html)
- [Workflow Triggers — SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-triggers.html)
- [Identity Attributes Changed — SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/identity-attribute-changed/)
- [Identity Created — SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/identity-created/)
- [Provisioning Completed — SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/provisioning-completed/)
- [Native Change Account Updated — SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/native-change-account-updated/)

---

[← Previous: Module 06 Forms, Approvals & Interactive Workflows](06-forms-and-interactive-workflows.md) | [Course home](README.md) | [Next: Module 08 Operations, Limits & Governance →](08-operations-limits-and-governance.md)