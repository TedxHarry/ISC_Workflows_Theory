# Module 09.1: Capability Ownership
Module 08 ended with a different kind of engineering question:

> **Should this requirement be implemented as a Workflow at all?**

Up to this point, you have spent most of the course learning how to reason **inside** a Workflow.

You learned how to:

- choose the correct event boundary;
- inspect actual data;
- route with operators;
- understand what actions really prove;
- build governed human interactions;
- test and diagnose executions;
- operate a Workflow responsibly over time.

Now we change perspective.

```text
Module 08

Can we operate this Workflow responsibly?

        ↓

Module 09

Should this requirement be a Workflow at all?
```

That is a harder question.

A Workflow can technically participate in many kinds of automation.

That is exactly why judgment matters.

The engineer who asks only:

> Can I make Workflow do this?

will eventually build something that works but belongs in the wrong place.

The better question is:

> **Which capability naturally owns the outcome, and does Workflow have an orchestration job around it?**

That is what this module teaches.

---

## 1. Core: From operating Workflows to choosing architecture

Imagine Priya moves from Sales to Finance.

Acme has several requirements around that move:

1. Priya should receive the standard access appropriate for Finance.
2. The Finance access owner should be notified.
3. A ticket should be opened for a manual downstream task.
4. If Priya later requests privileged Finance access, that request should go through the governed approval process.
5. Any approved target access change still has to be fulfilled.

You could look at that list and say:

> I know Workflows. I will build one Workflow that does all of it.

But that skips the architecture question.

These requirements do not all have the same natural owner.

Conceptually:

```text
standard Finance access
        ↓
access model

target access change
        ↓
provisioning

governed privileged request
        ↓
native access-request governance

notification + ticket orchestration
        ↓
Workflow may fit
```

That does not mean the capabilities are isolated from one another.

Quite the opposite.

A good ISC architecture can involve several capabilities working together.

The important skill is knowing **which one owns which responsibility**.

---

## 2. Core: “Can” is not “should”

Every module before this showed you what Workflows can do.

This one teaches the more valuable lesson:

> **“It can” is not “it should.”**

Technical possibility is not architecture.

Suppose you can build a Workflow that calculates a derived attribute.

That does not prove Workflow should own attribute calculation.

Suppose you can build a Workflow that grants standard employee access one identity at a time.

That does not prove Workflow should own Acme's standard-access model.

Suppose a scheduled Workflow can repeatedly call an API looking for a change.

That does not prove polling is the right design if a suitable event-driven mechanism already exists.

Architecture asks a different set of questions:

```text
WHAT OUTCOME IS REQUIRED?
        ↓
WHICH CAPABILITY OWNS THAT OUTCOME?
        ↓
DOES WORKFLOW ADD ORCHESTRATION?
        ↓
DOES WORKFLOW'S EXECUTION MODEL FIT?
        ↓
CAN I DEFEND THE CHOICE?
```

Notice what is missing.

We did not begin with:

> Which Workflow trigger should I use?

That question comes too early.

First decide whether Workflow belongs in the solution.

---

> **Engineering Habit**
>
> Do not start architecture with the capability you know best.
>
> Start with the outcome that must be owned.

---

## 3. Core: Find the primary owner first

When someone gives you an automation requirement, resist the urge to choose a tool immediately.

First ask:

> **What business state or process must actually change?**

Then ask:

> **Which capability naturally owns that state or process?**

That gives us the concept of a **primary owner**.

```text
REQUIREMENT
        ↓
WHAT MUST CHANGE?
        ↓
PRIMARY OWNER
```

But real architecture is rarely a one-tool competition.

After identifying the primary owner, ask a second question:

> **Does Workflow need to coordinate something around that owner?**

```text
PRIMARY OWNER
Which capability owns the business state or governed process?

        +

SUPPORTING ORCHESTRATION
Does Workflow coordinate work around it?
```

That distinction matters.

### Example: Priya moves to Finance

Suppose Acme says:

> When Priya moves into Finance, give her normal Finance access and tell the Finance access owner.

There are at least two outcomes here.

```text
Outcome 1
Determine Priya's standard Finance access

        ↓
access model owns it


Outcome 2
React to the move and send a notification

        ↓
Workflow may orchestrate it
```

So the architecture does not have to be:

```text
Access model
OR
Workflow
```

It can be:

```text
Access model
        +
Workflow
        +
Provisioning
```

with each capability doing the job it naturally owns.

That is a much stronger way to think than:

> Find the first tool that can technically perform every step.

---

## 4. Core: The capability decision map

Now that you have the reasoning model, we can examine the neighboring capabilities.

Do not memorize this as a feature comparison table.

For each capability, ask:

> **What does this capability naturally own?**

---

### Attribute-value calculation or manipulation → Transform

Transforms are the purpose-built configurable mechanism for calculating and manipulating attribute values.

Think:

```text
derive
normalize
format
combine
calculate
conditional value logic
fallback logic
```

For example:

```text
givenName = Priya
surname   = Patel

        ↓

displayName = Patel, Priya
```

A Transform can also contain conditional logic.

So do **not** use this old rule:

```text
Transform
→ cannot make decisions
```

That is wrong.

The architectural boundary is different:

```text
Transform
→ calculate / derive / normalize / manipulate values

Workflow
→ react to events and orchestrate actions,
   integrations, human steps, and process decisions
```

If you catch yourself building a Workflow whose real purpose is to calculate one identity attribute, pause.

You may be looking at **a Transform wearing a Workflow costume**.

---

### Standard access based on identity criteria → Role using Access Profiles

The access-model family contains several capabilities with different jobs.

Do not collapse them into one thing.

An **Access Profile** represents a bundle of access.

A **Role** can group Access Profiles and can use assignment criteria to determine who should receive that access automatically.

Conceptually:

```text
identity meets business criteria
        ↓
Role assignment logic
        ↓
Access Profiles describe the access
```

Suppose Finance employees should receive Acme's normal Finance application access because their identity attributes identify them as Finance workers.

That is fundamentally an access-model requirement.

A Workflow might notify someone that Priya entered Finance.

It should not become the primary mechanism that reconstructs standard access identity by identity when the access model owns that decision.

---

### Access driven by lifecycle status → Lifecycle State using Access Profiles

Lifecycle States represent employment or lifecycle conditions and can drive access changes associated with those states.

For example:

```text
Active
Leave of Absence
Terminated
```

can represent different lifecycle conditions.

So a requirement such as:

> When a person enters Acme's leaver state, apply the access behavior associated with that lifecycle condition.

naturally points toward Lifecycle State configuration and the access model.

Again:

```text
Lifecycle State
→ owns lifecycle-state-driven access behavior

Access Profile
→ represents bundled access

Workflow
→ may coordinate surrounding activity
```

A Workflow might open an offboarding ticket or notify Facilities.

That does not mean it should replace the lifecycle-access model.

---

### Governed access request and approval → Native access-request governance

Suppose Priya wants privileged Finance access.

The business requirement is not merely:

> Send somebody a form and wait for yes or no.

It is:

> Run a governed access-request process.

That process has a natural owner.

```text
governed access request
        ↓
native access-request governance
```

Workflow can participate through supported approval mechanisms or react around the request lifecycle.

But Workflow participation does not turn generic Workflow into a replacement for the native governance subsystem.

Keep the boundary simple:

```text
Native access-request governance
→ owns the governed request process

Workflow
→ may participate in supported approval logic
  or orchestrate around that process
```

Module 06 taught the mechanics.

Here we care only about architecture ownership.

---

### Fulfillment of supported target access/account changes → Provisioning

Eventually, some access or account state may need to change.

That fulfillment belongs to provisioning.

```text
approved or configured access change
        ↓
provisioning process
        ↓
target-side fulfillment
```

A Workflow can initiate or coordinate around provisioning-related work.

But Workflow does not replace the provisioning process itself.

Also be careful with the word **fulfillment**.

Do not assume every provisioning process means ISC directly performs every change through a connector in exactly the same way.

Depending on the source and configuration, fulfillment may involve different supported mechanisms.

The durable ownership boundary is:

> **Provisioning owns the fulfillment process for supported target access and account changes.**

---

### Event-driven bounded orchestration → Workflow may fit

Now we reach Workflow's natural territory.

Workflow is a strong candidate when the requirement looks like:

```text
event occurs
        ↓
inspect context
        ↓
make bounded decisions
        ↓
coordinate supported actions
        ↓
notify / integrate / route / request
```

Examples might include:

- react to an aggregation problem and notify an operator;
- react to Priya's department move and open a ticket;
- react to an identity event and coordinate several bounded actions;
- route a supported process according to event data;
- call an external service as one step in an event-driven process.

That is orchestration.

Workflow is good at connecting these boundaries without requiring you to build and operate a custom application for every automation.

---

### External event-driven processing → Event Trigger subscription plus external service may fit

Sometimes the event is useful, but the work belongs outside the managed Workflow service.

SailPoint supports Event Trigger subscriptions that can deliver supported events to external subscribers through supported subscription mechanisms.

Conceptually:

```text
supported Event Trigger
        ↓
external subscriber
        ↓
your service / processing environment
```

Do not assume this is the same surface as Workflow triggers.

There is overlap between the available event families, but:

```text
Workflow trigger catalog
        ≠
Event Trigger subscription catalog
```

and the mechanisms are not interchangeable.

A Workflow trigger starts managed Workflow orchestration.

A supported Event Trigger subscription delivers an event to an external subscriber.

That distinction becomes important when your own service, infrastructure, scaling model, libraries, or state management should own the processing.

---

### Purpose-specific code extension → Supported Rule type may fit

Rules require even more discipline.

Do not use:

```text
Nothing configurable fits
        ↓
use a Rule
```

That turns Rules into a generic escape hatch.

ISC Rules are supported, purpose-specific code extension points.

A better decision is:

```text
supported configurable capabilities do not solve the requirement
        ↓
is there a supported Rule type
for this specific extension point and purpose?
        ↓
if yes, consider that Rule
```

Rules use BeanShell and execute in defined contexts depending on Rule type.

They also carry code lifecycle and support considerations.

The important architecture lesson is not that Rules are the “most powerful” feature.

Remove that idea from your mental model.

The better model is:

> **A Rule is code used at a supported ISC extension point for a documented purpose, and should be considered deliberately rather than treated as a universal fallback.**

---

### Put the map together

At a high level:

```text
Need to calculate or manipulate attribute data?
        ↓
Transform


Need standard access based on shared identity criteria?
        ↓
Role, using Access Profiles


Need lifecycle-status-driven access behavior?
        ↓
Lifecycle State, using Access Profiles


Need a governed request and approval process?
        ↓
Native access-request governance
        +
Workflow may participate


Need fulfillment of supported target access/account changes?
        ↓
Provisioning
        +
Workflow may initiate or coordinate around it


Need to react to an event and coordinate bounded work?
        ↓
Workflow may own the orchestration


Need custom processing, libraries, application state,
or execution characteristics poorly matched to Workflow?
        ↓
Consider an external service / integration


Need code at a specific supported ISC extension point?
        ↓
Consider the applicable supported Rule type
```

Notice that several boxes can belong to the same business process.

That is intentional.

---

---

[← Previous: Module 08.2: Limits, Change & Governance](08-2-limits-change-and-governance.md) | [Course home](README.md) | [Next: Module 09.2: Architecture Decisions & Tradeoffs →](09-2-architecture-decisions-and-tradeoffs.md)
