# Module 06.1: Forms, Input & Human Delay

What changes when a Workflow needs a person?

Module 05 gave you a way to reason about actions:

```text
What job must happen?
        ↓
What input does the action need?
        ↓
What does success actually prove?
        ↓
What output should I inspect?
        ↓
What happens if the action errors?
```

Now add a human.

The process may need information that ISC cannot determine on its own. It may need someone to make a governed decision. Or it may need a user to deliberately launch a process and interact with it while it runs.

Those requirements can look similar on the surface because all of them involve a person.

They are not the same engineering problem.

The useful question is not:

> Which human-interaction feature should I add?

Start one level earlier:

> **What exactly do I need the person to do, and where does that person enter the process?**

---

## 1. Core: Start with the human-interaction decision map

Use this map before you think about individual action names.

```text
What do I need from the person?
        │
        ├── INFORMATION
        │
        │   Does the person's submission START the Workflow?
        │          │
        │          ├── Yes
        │          │    → Form Submitted trigger
        │          │
        │          └── No
        │               │
        │               ├── Is a running Workflow asking
        │               │   a selected person for input?
        │               │       → Form action
        │               │
        │               └── Does a user deliberately launch
        │                   a delegated process and interact
        │                   with it?
        │                       → Interactive Process
        │
        └── GOVERNED DECISION
                   │
                   └── Approval tooling
                       → Adaptive Approvals
```

This is a teaching map, not a replacement for current product documentation.

Its job is to keep you from choosing a feature merely because its name sounds close to the requirement.

You have already learned this engineering habit with triggers and actions:

```text
business requirement
        ↓
correct boundary
        ↓
product mechanism
```

Human interaction deserves the same discipline.

---

## 2. The human interaction contract

Module 05 taught you to read an action as a contract.

Use a similar contract whenever a Workflow involves a person:

```text
PURPOSE
What do I need from the person?

PARTICIPANT
Who is supposed to respond?

INITIATION
Who starts the interaction?

RESPONSE / EVIDENCE
What does completion actually prove?

NON-RESPONSE
What happens if the person does not respond?

DOWNSTREAM BOUNDARY
What is still not proven afterward?
```

Suppose Acme says:

> “We need Priya's manager involved.”

That is not enough information to choose a mechanism.

You still need to know what the manager is doing.

Are they supplying onboarding choices?

Approving sensitive Finance access?

Submitting the request that starts the whole process?

Those are different contracts.

---

## 3. Core: Intake: the person acts first

You met **Form Submitted** earlier as a specialized trigger.

Now you can place it in the human-interaction model.

A Form Submitted Workflow begins because somebody submitted a form.

```text
person
  ↓
submits form
  ↓
Form Submitted event
  ↓
Workflow starts
```

The person acts first.

The Workflow does not exist as a running execution waiting for that person. Their submission is the event that creates the execution.

Think of this as **intake: the front door**.

Acme might provide a form for requesting a shared mailbox:

```text
Mailbox name
Owner
Business reason
```

Someone submits it.

That submission starts the Workflow that processes the request.

The **Form Submitted** event includes submitted form data. The exact fields under that data depend on the form definition, so later logic should work from the actual technical keys and payload rather than assuming a field path from its display label.

The same habit from Module 02 still applies:

> **Inspect the data you actually received.**

### What does submission prove?

Keep the evidence boundary narrow.

```text
form submitted
        ≠
request fulfilled
```

Submission proves that the form-submission boundary occurred and supplied its documented data.

It does not prove whatever business process comes afterward has completed.

That distinction will keep appearing throughout this module.

---

## 4. Core: Assigned response: the Workflow acts first

Now reverse the direction.

Suppose Priya's onboarding Workflow is already running.

It has identity data. It knows her department. It has performed its earlier logic.

Then it reaches a question ISC cannot answer:

> Which optional systems does Priya's manager want included in her onboarding?

This is not intake.

The Workflow already exists.

It now needs information from a selected person.

That is where the **Form** action fits.

You will often hear it described naturally as the **Form action**.

The pattern is:

```text
Workflow already running
        ↓
needs information from a selected person
        ↓
Form action
        ↓
person receives the assigned form
        ↓
Workflow waits
        ↓
person submits
        ↓
Workflow resumes
```

Compare that with Form Submitted:

```text
FORM SUBMITTED

person
→ submission
→ Workflow starts
```

versus:

```text
FORM ACTION

Workflow starts earlier
→ Workflow asks person
→ person responds
→ same Workflow continues
```

The shared word **Form** should not hide that boundary.

## Priya's manager-input example

The Workflow can assign Priya's manager a short form asking which optional systems Priya needs.

Information the Workflow already knows can be supplied to the form rather than asking the manager to type it again.

So the manager might see:

```text
Employee: Priya Patel
Department: Finance

Select optional systems:
[ ... ]
```

The human contributes only the information the process is missing.

After successful submission, submitted form data becomes available to later Workflow logic.

Do not invent a universal JSONPath for those answers.

When you need an exact answer path, use the current Variable Selector or inspect the actual Form step output and reference the structure ISC produced.

The Form action also documents a `Submitted` attribute that can be evaluated with **Compare Boolean** when later logic needs to verify submission state.

That gives you another useful boundary:

```text
action completed
        ↓
inspect the response data you actually need
        ↓
validate before depending on it
```

A human entered the value.

That does not make the value automatically suitable for every later business decision.

---

## 5. Core: Human delay is part of the contract

A system action may finish in seconds.

A person may respond in five minutes, tomorrow, or not at all.

That changes the design.

Waiting for a human is not just a slower version of waiting for a deterministic action.

Human delay is part of the process contract.

The wrong model is:

```text
human step
→ eventually succeeds
```

Use this instead:

```text
human interaction
        │
        ├── response arrives
        │       → inspect response
        │       → continue deliberately
        │
        └── response does not arrive
                → follow that mechanism's
                  documented non-response behavior
```

That last line matters because there is **not one universal human-timeout rule in ISC**.

Different mechanisms resolve non-response differently.

## Form deadline

A Form action has a submission deadline.

When that deadline is reached, ISC generates a **cancellation error**.

If the Workflow must continue after that condition, its error handling has to account for it.

Conceptually:

```text
Form deadline reached
        ↓
cancellation error
        ↓
deliberate Error path if continuation is required
```

The Form action also supports reminder configuration.

Do not build your mental model around memorizing the current maximum deadline or reminder limits. Those are lookup facts.

Keep the engineering rule:

> **A Form deadline is part of the Form action's error contract.**

## Interactive Form cancellation

An **Interactive Form** has different documented cancellation behavior.

If the Interactive Form is canceled and Error handling is enabled:

```text
Interactive Form canceled
        ↓
Error branch
```

If Error handling is not enabled:

```text
Interactive Form canceled
        ↓
Workflow canceled
```

Notice the wording.

Do not casually replace **canceled** with **failed** simply because Module 05 taught generic failure handling.

The specific action contract wins.

## Approval-policy timeout

Approval policies introduce a different kind of non-response again.

An approval review can reach its configured review timeout.

That timeout is governed by the approval policy and can resolve according to its configured timeout action:

```text
review timeout
        ↓
configured policy outcome
        ↓
Approve
or
Expire
```

So this reasoning is unsafe:

```text
reviewer did not respond
        ↓
must mean denial
```

And this is also unsafe:

```text
reviewer did not respond
        ↓
must mean technical Workflow Error
```

The policy defines what that review timeout means.

That is why you inspect the contract instead of generalizing from another human step.

> **Engineering Habit:** When a Workflow waits for a person, ask how that specific mechanism represents non-response. Do not invent one global “human timeout” rule.

---
