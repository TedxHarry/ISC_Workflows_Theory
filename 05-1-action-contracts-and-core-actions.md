# Module 05.1: Action Contracts & Core Actions
How a running Workflow performs work, reads the result honestly, and handles action errors deliberately.

Module 04 ended here:

```text
The Workflow has started.
The data has been inspected.
The conditions have been evaluated.
The path has been chosen.
```

Now the Workflow has to **do something**.

That gives us the next engineering questions:

```text
What work must happen?
        ↓
Which action belongs on this path?
        ↓
What does successful completion actually prove?
        ↓
What output should I inspect?
        ↓
What happens if the action errors?
```

Operators decide.

Actions perform work.

Some actions notify a person. Some fetch information. Some request changes. Some call another system. Some pause execution.

Many of those actions cross a boundary the Workflow does not fully control:

```text
Workflow
   ↓
ISC service / request process / source / external API / time
```

That is why an action is more than a box with a green check mark.

Every useful action has a **contract**.

Your job as the engineer is to know where that contract ends.

---

## 1. Read an action as a contract

Before we look at individual action names, use the same questions for all of them.

```text
1. Job
   What work am I asking this action to perform?

2. Input
   What data or reference does it need?

3. Success boundary
   What does normal successful completion actually prove?

4. Output
   What result should later logic inspect?

5. Error
   What does it mean if the action takes its native Error path?

6. Next decision
   Continue, inspect, recover, use a valid fallback,
   or end the Workflow in Failure?
```

If you inherit a Workflow with an action you have never used, this model is more useful than memorizing an action catalog.

Start with the contract.

### Action completion and business completion are different questions

You have already seen this style of reasoning with triggers.

Module 03 asked:

> What event boundary did the trigger actually prove?

Now ask the action version:

> What completion boundary did this action actually prove?

Those two questions share the same engineering discipline:

```text
name of feature
≠
permission to infer everything nearby
```

An action called “Manage Access” does not make every later access boundary automatically true.

A Wait finishing does not mean the system you were waiting on finished.

A successful notification step does not prove the person read the message.

The action proves its own contract.

Your business requirement may need more evidence.

---

## 2. A five-verb map for choosing the job

You do not need the whole action menu in your head.

For this course, use a simple teaching map:

```text
NOTIFY
Tell a person something.
Example: Send Email

FETCH
Retrieve data the Workflow genuinely needs.
Example: Get Identity

CHANGE
Request or perform an ISC-managed change.
Examples: Manage Access, Manage Accounts

INTEGRATE
Call a supported external HTTP service.
Example: HTTP Request

PAUSE
Move the Workflow across a time boundary.
Example: Wait
```

This is a **learning map**, not SailPoint's official action taxonomy.

Its purpose is to help you start with:

> What kind of job is this?

rather than:

> Which menu item looks familiar?

We will use one or two representative actions from each family.

---

## 3. Notify: Send Email

A notification is a good first action because the contract is easier to see than a provisioning or access boundary.

Suppose Priya moves into Finance and Acme wants her manager notified.

A **Send Email** action needs the message inputs that matter to the notification, such as:

- recipient;
- subject;
- body.

Those inputs may come from data already available in the running Workflow.

Before adding another step, inspect what you have.

If the recipient address is already present and usable, use it.

If it is not, solve that data problem first.

### What does Send Email success prove?

Keep the claim narrow.

A successful Send Email action does **not** provide evidence that:

```text
the human read the message
or
the human acted on the message
```

Those are later human outcomes.

Do not turn the absence of read/acknowledgement evidence into a made-up mailbox-delivery contract either.

The safe engineering statement is:

> **Send Email success is not proof of human receipt, reading, or action.**

If the business process merely requires the Workflow to perform its documented notification action, that may be enough.

If Acme needs acknowledgement from a person, you have crossed into a human-interaction requirement.

Module 06 handles that family of problems.

### Input problems are not something to guess about

Suppose the configured recipient points to data that is not actually present.

You already know how to reason about that from Module 02:

```text
expected path
        ↓
inspect real available data
        ↓
is the value actually there and usable?
```

Do not invent a universal rule about whether one particular empty or unresolved recipient configuration will make the action succeed or error.

Inspect the actual data and the action behavior.

The broader lesson is stable:

> **Wrong input means you have not established a reliable notification design.**

### Working Engineer: current product quirks are lookup facts

Send Email has current formatting and timeout details that can matter in a real build.

They are not Core memory targets.

When the exact formatting rule or timeout matters, check the current action documentation.

What you should keep in your head is:

> Action-specific implementation details change. The action contract and the evidence you need are the engineering problem.

---

## 4. Fetch: use what you have before Get Identity

Fetch actions are useful.

They are also easy to add when you do not actually need them.

Before using **Get Identity**, ask:

> What value is missing?

That question protects you from building lookup-heavy Workflows by habit.

### Priya's manager reference

Return to the mover data you already know.

An Identity Attributes Changed event contains an identity reference and a `changes` array.

For a manager change, the manager `newValue` can be an identity reference containing information such as:

```text
id
name
type
```

That reference is useful.

It is not the same thing as having every manager attribute.

If Acme needs the manager's email address and that address is not present in the reference, **Get Identity** is a natural fetch action to evaluate.

The reasoning is:

```text
manager reference available
        ↓
required manager email not supplied there
        ↓
Get Identity using the manager identity ID
        ↓
inspect the returned identity data
        ↓
use the required attribute
```

Notice what we did **not** say:

> “The trigger contains only what changed.”

That is too broad.

The trigger contains other event data as well.

The relevant point is narrower:

> **The manager change gives you an identity reference, and that reference does not itself contain the manager email in the documented example.**

### Do not fetch data you already have

Suppose the value you need is already present in the trigger or an earlier action output.

Adding Get Identity anyway gives you:

- another action/service lookup;
- more latency;
- more returned data;
- another place the Workflow can fail.

It does **not** create another Workflow execution merely because the Get Identity action ran.

That distinction matters.

> **Engineering Habit:** Before adding a fetch action, point to the exact value you need and prove that the Workflow does not already have it.

### What does Get Identity success prove?

Get Identity retrieves identity data according to its action contract.

That does not automatically mean:

- every attribute your later logic wants is present;
- every attribute is non-null;
- every attribute is usable for your business rule.

You already know the next move from Module 04:

```text
action output
        ↓
inspect / validate
        ↓
operator logic
```

A successful fetch can still give you data that needs to be checked before you depend on it.

That is another form of **Green Does Not Mean Done**.

---

## 5. Change: access and accounts are different jobs

Now we cross into actions where the difference between **action completion** and **business completion** becomes much more visible.

Acme may need to manage:

```text
ACCESS
roles / access profiles / entitlements

or

ACCOUNT STATE
disable / enable / unlock / supported delete operation
```

Those are different layers.

The representative actions are:

```text
Manage Access
→ access changes

Manage Accounts
→ account operations
```

Do not choose between them because both sound like “change something for Priya.”

Ask what object the requirement is actually about.

---

## 6. Manage Access: the action boundary is not the final access boundary

Suppose Acme has a legitimate Workflow-owned requirement to request a specific access change for Priya.

**Manage Access** can add or remove supported access.

This is where you need to slow down and separate several boundaries that can all sound like “the access change worked.”

### What does Manage Access success prove?

Manage Access submits access requests for processing.

If approval is required, the Workflow continues after request submission rather than waiting for the approval decision.

If approval is not required, the action still does not wait for confirmation from the source that the access was updated.

So hold these as separate facts:

```text
Manage Access action succeeded
        ≠
Access request approved
        ≠
Provisioning completed
        ≠
Target state independently confirmed
```

This is not edge-case trivia.

This is the contract.

A successful action tells you something meaningful.

It just does not tell you *everything*.

### Inspect the normal output

Manage Access exposes result data including:

```text
successfulAccessRequests
failedAccessRequests
```

A Workflow can have entries in `failedAccessRequests` without those entries automatically making the Workflow execution fail.

That gives you an important distinction:

```text
native action completed on its normal path
        ↓
normal output contains information
that your business rule may dislike
```

That is **not automatically the same thing** as:

```text
action took its native Error branch
```

If Acme requires every submitted access item to be accepted by the Manage Access action, later operator logic should inspect the normal output and make a deliberate decision.

Do not stare only at the green action box.

Read the result.

### What does `successfulAccessRequests` mean?

Do not translate the field name into:

> “The access is live.”

The safe meaning is narrower:

> The Manage Access action treated those request submissions as successful.

The field does not by itself prove:

- approval;
- provisioning completion;
- independent target state.

If the process later cares about approval, that is a later boundary.

Module 06 teaches the human and governed-decision mechanisms.

For now, your job is simply not to smuggle that later boundary into the word *successful*.

### A short architecture reminder

The existence of Manage Access does not mean Workflow should own every access-assignment requirement.

Module 09 will teach the full tool-selection decision.

For Module 05, keep only this discipline:

> **Choose an action only after you have already decided that this work belongs in Workflow.**

---

## 7. Manage Accounts: normal output can contain mixed item results

**Manage Accounts** is the account-layer counterpart.

Current operations include account actions such as:

- Disable;
- Enable;
- Unlock;
- supported Delete behavior.

You do not need that operation list as a memorization test.

The deeper lesson is the result boundary.

Current Manage Accounts output can include:

```text
successfulAccounts
failedAccounts
accountsErrorDetails
```

and documented normal output can contain both successful and failed account items.

That means this pattern is possible conceptually:

```text
Manage Accounts
        ↓
normal action output
        ↓
some items described as successful
some items described as failed
```

Again:

```text
item-level failure information in normal output
≠
native action Error branch
```

Do not infer one universal overall Workflow status from a particular mix of those output arrays unless the current action contract says so.

Inspect what the action returned.

Then decide what your business requirement says to do with that result.

### Access success and account success still do not equal target verification

A green Manage Accounts action is not documented as an independent target read-back verification mechanism.

If the business control requires proof of final target state, that is a separate evidence question.

This is the same engineering habit you are building across the course:

> **Do not promote action status into stronger evidence than the contract provides.**

---

## Green Does Not Mean Done

You have now seen enough actions to name the principle directly.

A green action means:

> **The action satisfied its documented success/completion contract.**

It does not automatically mean:

> **The business outcome you ultimately care about is proven.**

For Manage Access, the ladder is explicit:

```text
Workflow action succeeded
        ≠
Access request approved
        ≠
Provisioning completed
        ≠
Target state independently confirmed
```

Each line is a separate boundary.

Do not collapse them.

### The same principle appears in every action family

#### Notify

```text
Send Email action succeeded
        ≠
human read the message
        ≠
human acted on it
```

#### Fetch

```text
Get Identity succeeded
        ≠
every required attribute is present
        ≠
every returned value is usable
```

#### Change

```text
Manage Access succeeded
        ≠
every requested business outcome completed

Manage Accounts returned normal output
        ≠
every account item necessarily succeeded
        ≠
independent target state was verified
```

#### Integrate

```text
HTTP Request action completed on its normal path
        ≠
response data automatically proves your business rule
```

#### Pause

```text
Wait completed
        ≠
external work was verified complete
```

This is why “green” is useful evidence, but not the last question.

The last question is:

> **What boundary do I still need to prove?**

---

---

[← Previous: Module 04: Operators & Logic](04-operators-and-logic.md) | [Course home](README.md) | [Next: Module 05.2: Error Handling, External Actions & Success Boundaries →](05-2-error-handling-external-actions-and-success-boundaries.md)
