# Module 05: Actions & Error Handling

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

## 8. Integrate: HTTP Request and the dependency you do not control

Sooner or later, a requirement may need a Workflow to call an external HTTP service.

**HTTP Request** is a general-purpose Workflow action for supported HTTP integrations when that integration genuinely belongs inside the Workflow.

That wording matters.

It is not:

> “the universal answer for anything external.”

An HTTP integration still has to fit:

- the action's supported HTTP contract;
- the external system's interface and authentication;
- the Workflow's architectural role;
- the scale and operational needs of the process.

Module 09 will handle the larger “should Workflow own this?” decision.

### Request in, response out

Conceptually:

```text
Workflow data
        ↓
HTTP Request
        ↓
external HTTP service
        ↓
JSON response when provided
        ↓
action output becomes available to later Workflow logic
```

The external system controls the meaning and shape of its response.

Do **not** memorize a guessed response path such as:

```text
$.getDeskInfo.building
```

as though every HTTP Request output is flattened that way.

Use the engineering habit you already know:

```text
inspect actual HTTP Request output
        ↓
use the current Variable Selector / execution data
        ↓
reference the structure actually produced
```

The response shape is evidence, not something to invent from the API's example body.

### External dependency changes the failure surface

Once your Workflow calls another system, that system can be:

- unavailable;
- slow;
- rejecting the request;
- returning data your later logic does not expect.

That does not make HTTP Request a bad action.

It means the action boundary needs a deliberate design.

Do not hard-code secrets into the Workflow definition.

Module 08 owns the production secret/credential-management details.

For this module, carry the principle:

> **External calls introduce dependencies you do not fully control. Build the next path from the actual result or error, not from optimism.**

### Do not invent a universal HTTP-status-to-Error rule

`workflowStatusCode` exists on the generic native Error path.

Its name does not make it universally an HTTP response status code.

Likewise, do not teach a fixed rule such as:

```text
HTTP 4xx/5xx
→ always this exact Workflow behavior
```

unless the current action contract explicitly establishes it.

When the exact HTTP behavior matters, verify the current action documentation and inspect the action's actual result.

---

## 9. Pause: Wait gives time, not evidence

**Wait** moves the Workflow across a time boundary.

It can wait for a configured duration or until a configured time.

That can be useful when the design intentionally needs a delay.

But the contract is simple:

```text
Wait completed
=
the configured time boundary passed
```

It does **not** prove:

```text
provisioning finished
external API work finished
source account changed
human completed a task
target state is correct
```

Time is not verification.

If you use Wait after an asynchronous process because the product guidance recommends allowing time for an update, treat the Wait as exactly that:

> **time allowance**

not:

> **evidence that the update occurred**

This is one of the cleanest examples of **Green Does Not Mean Done**.

### Timeouts are action-specific lookup facts

Actions have different timeout behavior.

The exact values are implementation details you should verify when they matter.

Do not memorize a table of timeouts from this module.

Keep the stronger habit:

> **Before relying on an action that may run for a meaningful amount of time, check that action's current documented timeout and failure behavior.**

One caution survives the current documentation boundary:

- a timeout is a failure condition;
- current documentation does **not** establish a universal guarantee that every timeout will always route through an enabled native Error branch.

If your design depends on that exact routing behavior, verify it for the action you are using.

---

## 10. When an Action Fails: native Error Handling

So far we have mostly talked about the action's **normal result**.

Now we need a different boundary:

> What if the action itself encounters an error?

Current Workflows support native error handling on actions.

When error handling is enabled, the action has separate:

```text
Success
and
Error
```

branches.

Conceptually:

```text
                ACTION
                  │
        ┌─────────┴─────────┐
        │                   │
     Success              Error
     branch               branch
        │                   │
normal result          native action error
```

Without error handling enabled, an action error stops the Workflow in a failed state.

With error handling enabled, the Error branch can contain additional Workflow logic or actions.

That is a major design change:

> **An action error can become a deliberate engineering decision instead of an implicit stop.**

### Success branch does not mean “business success”

The branch is called **Success** because the action followed its normal successful path.

Do not confuse that with proof that the final business outcome is complete.

Manage Access already showed why:

```text
native Success branch
        ↓
normal Manage Access output
        ↓
maybe inspect failedAccessRequests
        ↓
approval / provisioning / target-state boundaries still separate
```

Native branch status and business evidence are different questions.

---

## 10.1 Four outcomes that beginners often collapse together

This distinction is worth making explicit.

### 1. Valid business branch

Operator logic says:

> “No action is needed for this case.”

Example:

```text
Priya's move is not Finance
→ take another valid path
```

Nothing failed technically.

A business rule simply chose a different route.

### 2. Normal action result contains a problem signal

The action followed its normal result path, but the output says something the business cares about.

Examples:

```text
Manage Access
→ failedAccessRequests contains items
```

or:

```text
Manage Accounts
→ normal output includes failedAccounts
```

That result may require operator logic.

It is not automatically the native Error branch.

### 3. Native action error

The action itself hits an error condition.

With native error handling enabled:

```text
action
→ Error branch
```

Now the Workflow can decide what to do.

Without error handling enabled, the action error stops the Workflow failed.

### 4. Downstream business outcome is still unproven

The action may be green.

The normal output may even look clean.

But a later boundary still has not been established.

Example:

```text
Manage Access success
≠
approval
≠
provisioning
≠
target verification
```

These four situations need different reasoning.

If you call all of them “failure,” you will design the wrong response to at least one of them.

---

## 10.2 Read the native error information

On the native Error branch, current generic error information includes:

```text
workflowErrorMessage
workflowStatusCode
```

Treat them according to their documented meaning.

`workflowErrorMessage` gives the error message.

`workflowStatusCode` is a numeric error status code.

Do **not** rename it mentally to:

```text
httpStatusCode
```

and assume it always means an HTTP response status.

It is generic Workflow error information.

### Preserve useful error information

If an action fails, replacing every error with:

```text
"Something went wrong."
```

throws away information you may need later.

A better design asks:

```text
What error did the action expose?
What context will an operator need?
What can the next step safely use?
```

Module 07 will teach how to investigate execution history systematically.

Module 05 only needs the habit:

> **Do not hide useful native error evidence unless you have a reason to.**

---

## 10.3 An Error branch does not have to fail immediately

A native Error branch can contain more Workflow steps.

That means this is valid in principle:

```text
primary action errors
        ↓
Error branch
        ↓
operator decision
        ↓
acceptable recovery / compensating action
        ↓
continue
```

The existence of an error does not force the next box to be Failure.

The correct question is:

> **Can the process still satisfy the requirement honestly?**

If yes, a recovery path may be valid.

If no, pretending otherwise only makes the execution look healthier than the process really is.

---

## 10.4 Fallback is a design pattern, not a SailPoint action

This course will use the word **fallback** in its normal engineering sense.

It means:

> an alternate path that still satisfies the requirement when the primary path cannot.

It is not the name of a Workflow action called `Fallback`.

Suppose an external ticket API is unavailable.

A theoretical fallback might be valid only if Acme has an approved alternate mechanism that still creates the required operational record.

This is **not** a fallback:

```text
ticket creation failed
        ↓
send a cheerful email
        ↓
mark everything successful
```

if Acme's business requirement was:

> “A ticket must exist.”

The alternate path has to satisfy the requirement, not merely avoid a red execution.

Use this test:

```text
Primary action failed.
        ↓
Does the alternate path still fulfill
the business requirement?
     ↙ yes              ↘ no
valid fallback        not a fallback
```

---

## 10.5 Success and Failure end steps tell the truth about execution status

Every Workflow branch ultimately ends.

The **Success** and **Failure** end steps have specific execution-status semantics.

```text
Success
→ stops the Workflow
→ marks the execution successful

Failure
→ stops the Workflow
→ marks the execution failed
```

That is what those end steps prove.

They do **not** automatically prove the final business outcome outside the Workflow.

This keeps **Green Does Not Mean Done** consistent even at the end of the execution.

### Failure is sometimes the most accurate design

Suppose a required external ticket action fails.

The Error branch tries the only approved fallback.

That fallback also cannot create the required record.

If the ticket is mandatory, continuing to a Success end step would misrepresent what happened.

A deliberate Failure may be the truthful outcome:

```text
required action failed
        ↓
no acceptable recovery
        ↓
End Step - Failure
```

Failure is not something to avoid for cosmetic reasons.

It is a status that should tell the truth about the Workflow execution.

### Failure Details carries the explanation

If the Failure path needs explanatory information, use the **Failure Details** concept for the explanation.

Do not treat **Failure Name** as the human-readable failure reason.

The current product uses Failure Name as the step name used for linking.

That is exactly the kind of implementation detail worth being precise about because a misleading field name can lead to poor design.

---

## 10.6 Technical failure versus valid business outcome

A technically successful Workflow does not mean every branch had to “do something.”

And a business answer of “no” is not a technical failure.

Suppose Acme's rule says:

```text
If Priya did not move into a department
that requires this follow-up,
do nothing and end normally.
```

That can be a completely valid successful execution.

Compare:

```text
BUSINESS OUTCOME
Rule says no action required.
→ valid branch
→ may end Success
```

with:

```text
TECHNICAL ERROR
Required action could not perform its job.
→ Error branch or unhandled failure
```

Do not use Failure merely because a condition evaluated false.

And do not use Success merely because you would prefer not to see a failed execution.

Choose the end status that accurately represents the Workflow's execution according to the design.

---

## 11. The Error branch still needs normal engineering judgment

Enabling error handling is not the same as designing error handling.

An Error branch that says:

```text
error
→ ignore
→ Success
```

may be technically valid and operationally dishonest.

When you design an Error branch, ask:

```text
1. Was the failed action required?
2. What native error information is available?
3. Can the requirement still be met?
4. Is there a genuine alternate path?
5. Should someone or something be informed?
6. If the requirement cannot be met, should this execution end Failure?
7. What later business evidence would still be required even after recovery?
```

That is error handling.

The branch itself is only the mechanism.

### Compensation, retry, and idempotency come later

An Error branch can contain further actions, including compensating work.

But generalized retry strategy is not a Core Module 05 problem.

Retries raise questions such as:

- Did the first call actually fail, or did the response fail?
- Could retrying duplicate a side effect?
- Is the operation idempotent?
- What happens if two executions overlap?

Module 11 owns those edge cases.

For now:

> **Do not add retry behavior casually just because an Error branch gives you somewhere to put it.**

---

## 12. Working Engineer: know that specialized actions exist

The representative actions in this module are not the entire action catalog.

ISC has additional actions for other lookup, platform, certification, ticketing, and specialized tasks.

You do not need to memorize them.

Use the current action documentation when a requirement calls for a capability you have not learned here.

The later course boundaries are intentional:

```text
Forms / interactive / governed human decisions
→ Module 06

Testing and execution diagnosis
→ Module 07

Secrets, ownership, operations, limits
→ Module 08

Should this even be a Workflow?
→ Module 09

Reusable production patterns
→ Module 10

Retry, replay, concurrency, idempotency
→ Module 11
```

### Inheriting an older Workflow

You may open an older Workflow and see actions that current documentation describes as replaced.

For example:

- **Create Request for Access** has been replaced by Manage Access for Add Access;
- **Request Access Removal** has been replaced by Manage Access for Remove Access.

Do not memorize legacy names as active design choices.

The useful engineering habit is:

> **When an inherited Workflow contains an unfamiliar or legacy action, check the current documentation before copying the old pattern forward.**

---

## 13. A compact action-and-error decision method

At this stage of the course, you should be able to design from the requirement rather than from the builder menu.

Use this sequence:

```text
1. What work must happen?
   Notify, fetch, change, integrate, pause,
   or another specialized job?

2. Do I already have the required data?
   If yes, use it.
   If no, what fetch is actually justified?

3. Which action owns this job?
   Choose by the work, not by familiarity.

4. What boundary does the action own?
   What does normal completion actually prove?

5. What output must I inspect?
   Does normal output contain item-level
   success/failure or other evidence?

6. Did I get a normal result or a native action error?
   Do not confuse the two.

7. If it is an action error, what error information exists?
   Preserve what the next decision needs.

8. Can the business requirement still be satisfied?
   If yes, a real recovery/fallback may fit.

9. If not, should this execution end Failure?
   Do not hide a required failure.

10. What later business boundary remains unproven?
    Green does not mean done.
```

If you can follow that sequence, you can approach an unfamiliar action without needing the whole catalog in your head.

---

## Work It Out: action contract before action name

Priya moves into Finance.

The Workflow has already started and the operator logic has routed the run down the Finance path.

Acme's design says:

1. Notify Priya's new manager.
2. The manager change supplied an identity reference, but the Workflow does not currently have the manager's email.
3. Request a specific Finance access profile for Priya.
4. Acme requires every requested access item in this step to be accepted by Manage Access before the Workflow may treat that step as satisfactory.
5. Call an approved external HTTP ticket service to create a Finance onboarding ticket.
6. If the ticket action encounters a native action error, Acme has **no** approved alternate ticket mechanism. The ticket is mandatory.
7. After the ticket is created, Acme wants to wait before a later process checks another system.

Reason through the design before looking at exact builder configuration.

### Questions

1. What should the Workflow do before Send Email if the manager email is not present in the manager identity reference?
2. Why is adding Get Identity justified here, and what would make it unnecessary in a different Workflow?
3. What does successful Get Identity completion **not** prove about the returned manager email?
4. Manage Access completes on its normal path. Which output matters if Acme requires every requested item to be accepted by that action?
5. If `failedAccessRequests` contains an item, is that automatically the same thing as the action taking its native Error branch?
6. If `successfulAccessRequests` contains the Finance access profile, may Acme now claim the access was approved, provisioned, and verified on the target?
7. The HTTP Request takes its native Error branch. Which two generic native error values are available?
8. Is “send an email saying the ticket failed” a valid fallback if Acme's actual requirement is that the ticket must exist?
9. With no valid fallback, which end status best tells the truth about this execution?
10. If the HTTP Request follows its normal path, should later logic guess a fixed JSONPath for the response body?
11. What does the later Wait prove?
12. Which part of this scenario belongs to Module 06 rather than this module if Acme later wants a person to make a governed access decision?

<details>
<summary>Check your reasoning</summary>

**1. Fetch the missing identity data.**  
The manager change gives the Workflow a manager identity reference, not the manager's email in the documented example. Get Identity is a natural fetch action when the Workflow genuinely needs manager identity data that the reference does not provide.

**2. The missing value justifies the lookup.**  
The Workflow can point to the exact data it lacks. If another trigger or earlier step already supplied a usable manager email, the extra lookup would add latency, data, and another failure surface without solving a real data gap.

**3. Get Identity success does not prove the email is present and usable.**  
Inspect the returned identity data. A successful fetch is not a guarantee that every later business-required attribute exists in the form you expect.

**4. Inspect the normal Manage Access result, especially `failedAccessRequests`.**  
If Acme requires every requested item to be accepted by Manage Access, the normal output must be part of the decision.

**5. No.**  
A failed item represented in normal Manage Access output is not automatically the same boundary as a native action Error branch.

**6. No.**

```text
Manage Access action succeeded
        ≠
Access request approved
        ≠
Provisioning completed
        ≠
Target state independently confirmed
```

The action's successful request-submission boundary is not final fulfillment evidence.

**7.**

```text
workflowErrorMessage
workflowStatusCode
```

Do not assume `workflowStatusCode` is universally an HTTP response status code.

**8. No.**  
That notification may be useful operationally, but it does not satisfy the stated requirement that the ticket must exist. A fallback must actually fulfill the requirement.

**9. Failure.**  
If the required HTTP ticket action errors and there is no acceptable recovery that creates the mandatory ticket, a deliberate Failure end is the truthful execution outcome.

**10. No.**  
Inspect the actual HTTP Request output and use the current Variable Selector/execution data. Do not promote an example API body into an invented fixed Workflow output path.

**11. Only that the configured time boundary passed.**

```text
Wait completed
≠
proof another system finished
```

**12. Governed human approval mechanics.**  
Module 05 only keeps approval as a later boundary that Manage Access success does not prove. Module 06 teaches the human-in-the-loop and governed approval mechanisms.

</details>

---

## Checkpoint

You should now be able to take a path that Module 04 designed and reason through the work in this order:

```text
What work must happen?
        ↓
Do I already have the required data?
        ↓
Which action fits the job?
        ↓
What does its normal completion prove?
        ↓
What output must I inspect?
        ↓
Normal result or native action error?
        ↓
If error:
Can the requirement still be met honestly?
        ↓
recovery / valid fallback
or
Failure
        ↓
What business boundary remains unproven?
```

You should also be able to explain:

- why notify / fetch / change / integrate / pause is a teaching map rather than a product taxonomy to memorize;
- why a fetch action should solve a specific missing-data problem;
- why an unnecessary Get Identity adds work and failure surface but is not another Workflow execution by itself;
- why a manager identity reference is not automatically a manager email address;
- why Manage Access success is not approval, provisioning, or independent target-state proof;
- why `failedAccessRequests` can be a normal-result problem rather than a native Error-branch event;
- why Manage Accounts normal output can contain successful and failed item information;
- why partial normal output and native action error are different boundaries;
- why HTTP Request output must be inspected rather than guessed from an example response body;
- why `workflowStatusCode` should not be treated universally as an HTTP status code;
- why Wait gives time rather than evidence;
- why action-specific timeout values are lookup facts rather than Core memorization;
- why enabling an Error branch does not automatically make the error handling design good;
- why a fallback must still satisfy the business requirement;
- why Success and Failure end steps describe Workflow execution status rather than proving the external business outcome;
- why Failure can be the correct design when a required action cannot complete and no valid recovery exists;
- why a valid business “no action needed” branch is not the same thing as a technical action failure;
- why **Green Does Not Mean Done** applies to the whole action layer.

You can now make the Workflow act without confusing action completion with proven business completion.

The next question changes the shape of the Workflow:

> **What if the process needs a person to provide information or make a governed decision?**

That is where Module 06: Forms, Approvals & Interactive Workflows begins.

---

## Official References

- [Workflow Actions - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-actions.html)
- [Building Workflows - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-build.html)
- [Workflow Operators - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-operators.html)
- [Managing Workflows - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-manage.html)
- [Identity Attributes Changed - SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/triggers/identity-attribute-changed/)
- [Filtering Events - SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/filtering-events/)

---

[← Previous: Module 04 Operators & Logic](04-operators-and-logic.md) | [Course home](README.md) | [Next: Module 06 Forms, Approvals & Interactive Workflows →](06-forms-and-interactive-workflows.md)
