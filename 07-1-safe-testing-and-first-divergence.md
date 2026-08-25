# Module 07.1: Safe Testing & First Divergence

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

## 2. Core: Test safely before trusting the result

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

## 3. Core: The five diagnostic questions

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

## 4. Core: Question 1: Did the Workflow start?

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

## 5. Core: Question 2: What data actually arrived?

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

## 6. Core: Question 3: Where did the first unexpected value appear?

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
