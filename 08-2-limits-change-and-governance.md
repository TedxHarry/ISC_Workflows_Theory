# Module 08.2: Limits, Change & Governance
## 5. Core: What constrains it?

Every production system has an operating envelope.

Workflows are no different.

When you encounter a current limit, do not just memorize the number.

Ask:

```text
What is limited?

At what scope?

Over what period?

What counts?

What happens at the boundary?

What design decision does that constrain?

Where do I verify the current value?
```

That is the model worth remembering.

### Execution volume: two different scopes

ISC currently applies execution constraints at both tenant and individual-Workflow scope.

They do not count the same things.

#### Tenant level

Current documentation describes approximately:

```text
~400,000 executions per day
```

for the tenant-level threshold.

Loop executions are excluded from that tenant count.

After the tenant threshold is reached, executions continue at a rate of approximately:

```text
5 executions per second
```

for the remainder of the day.

So:

```text
tenant threshold reached
        ≠
all Workflows stop
```

The boundary changes execution rate.

#### Individual Workflow

An individual Workflow has separate high-execution thresholds.

Its count includes:

```text
Workflow executions
+
loop executions
```

Current documented thresholds are:

```text
100,000
→ warning

150,000
→ remaining executions blocked
```

Do not attach an undocumented reset period to those two values.

For this course, the durable lesson is:

```text
tenant execution accounting
        ≠
individual Workflow accounting
```

A loop can therefore matter greatly to the individual Workflow count even though loop executions are excluded from the tenant-wide daily threshold.

### Trigger selectivity is operational design

You first learned trigger filtering as a correctness boundary.

It is also operational.

Suppose Acme needs a Workflow only for department moves into Finance.

A broad trigger that allows many irrelevant events to start the Workflow and then rejects them later has already consumed operational activity.

Compare:

```text
event occurs
→ Workflow starts
→ later logic discovers it was irrelevant
```

with:

```text
event occurs
→ supported trigger filter determines relevance
→ only qualifying events start the Workflow
```

Filtering should still be designed primarily around the correct event and data boundary.

But once that boundary is correct, unnecessary starts are operational noise.

### Definition and payload size

Volume is not the only operating constraint.

Current documented reference values include:

```text
Workflow definition              400 KB maximum

Workflow definition + input      1.5 MB maximum

Maximum payload                  10 MB
```

Do not memorize those numbers as if they were permanent architecture truths.

Instead remember that Workflows have:

- definition-size boundaries;
- combined definition/input boundaries;
- payload boundaries.

Verify the current values when a design approaches them.

Also keep SailPoint's wording intact: **maximum payload**.

Do not silently reinterpret that 10 MB value as a universal HTTP Request body or response limit.

---

> **Engineering Habit**
>
> When someone quotes a platform limit, ask for its **scope and counting rule** before making a design decision.
>
> “The limit is 150,000” is incomplete.
>
> You still need to know:
>
> ```text
> 150,000 of what?
> counted where?
> what happens next?
> ```

---

## 6. Core: What evidence shows that it is healthy?

Module 07 taught you to use execution evidence to diagnose a failure.

Operations uses evidence differently.

You are no longer asking only:

> What happened to Priya's execution?

You are also asking:

> Is this production asset behaving normally over time?

That requires more than one green run.

### Workflow-engine evidence

Useful evidence can include:

- successful executions;
- failed executions;
- execution history;
- error rate;
- unexpected changes in execution volume;
- tenant-limit warnings;
- high-execution warnings for individual Workflows.

These signals help answer:

```text
Did it run?

Is it failing?

Is activity normal?

Is volume approaching a boundary?
```

That is Workflow-engine health.

### Business-outcome evidence

Now apply **Green Does Not Mean Done** one level higher.

```text
Workflow appears healthy
        ≠
business outcome proven
```

Suppose Priya's mover Workflow successfully calls an external ticketing API.

The Workflow execution may provide evidence that the HTTP action completed according to its contract.

That does not automatically prove:

- the ticket reached the correct queue;
- a human processed it;
- the requested access change completed;
- the target system reached the intended state.

The business process may cross several ownership boundaries after the Workflow has finished its own work.

A mature operational design asks:

> **What evidence proves the outcome we actually care about?**

That evidence might live in ISC.

It might live in the external system.

It might require another governed process.

The correct answer depends on the business boundary.

### Define healthy before something breaks

For an important Workflow, decide in advance what normal operation looks like.

For example:

```text
Expected activity
How often should this Workflow normally run?

Failure evidence
What failures require attention?

Volume evidence
What sudden increase or decrease is suspicious?

Dependency evidence
How will we know an external service is unavailable?

Outcome evidence
What proves the intended downstream state?

Response owner
Who acts when those signals appear?
```

“Monitor the Workflow” is not an operational plan.

Those questions are.

### Execution evidence is not permanent audit storage

Workflow execution evidence has a finite documented operational horizon.

Current SailPoint material around the Workflow UI and Workflow Executions API does not support treating the API as a guaranteed permanent archive.

The safe rule is:

> **If evidence must survive beyond the documented operational history horizon, retain the required evidence somewhere designed for that requirement.**

Do not wait until an auditor asks for a year-old execution to discover that your operational history was never your long-term evidence strategy.

---

## 7. Core: How do we change it safely?

A production Workflow is not just a canvas you edit until it looks right.

Treat a change as maintenance.

SailPoint currently requires a Workflow to be **disabled before editing**.

That alone creates an operational boundary.

While the Workflow is disabled, do not assume that events occurring during that period will later be replayed into it when it is re-enabled unless the documentation for that specific trigger establishes such behavior.

Do not invent a universal model such as:

```text
disabled
→ every event is safely queued
```

or:

```text
disabled
→ every event is permanently discarded
```

The stable lesson is:

> **Disabling a production Workflow changes its availability. Plan the change accordingly.**

### A safe-change shape

A useful engineering process is:

```text
understand current state
        ↓
preserve known-good definition
        ↓
review the intended change
        ↓
disable when required
        ↓
make the change
        ↓
test safely
        ↓
enable
        ↓
observe real executions
        ↓
document what changed
```

Some of that sequence is SailPoint product behavior.

Some is engineering practice.

For example:

- **Workflow must be disabled before editing**: product behavior.
- **Keep a known-good copy**: engineering practice.
- **Peer review important changes**: engineering practice.
- **Observe the first production executions after the change**: engineering practice.

Do not confuse “SailPoint supports this” with “SailPoint forces our organization to operate this way.”

### Ownership changes are changes too

Owner reassignment also requires the Workflow to be disabled.

That means succession work belongs in the same operational planning as other changes.

Do not wait until ownership has already become a production problem.

---

## 8. Working Engineer: Promotion and maintainable artifacts

A Workflow has a structured definition underneath the visual builder.

That gives you more than one way to manage its lifecycle.

### Workflow JSON

Workflow JSON can be downloaded.

JSON can also be used when creating a Workflow.

A known-good exported definition is useful for:

- comparison;
- review;
- backup;
- recreation;
- controlled movement between environments.

### Configuration Management and Configuration Hub

SailPoint also provides configuration-management capabilities.

For Workflows, current Configuration Hub support includes **Backup** and **Deploy**.

That is different from saying:

> The ordinary Workflow builder has a Git-like revision history for every edit.

Treat these as separate surfaces:

```text
Workflow builder
→ visual creation and editing
→ no documented Git-like per-edit revision history

Configuration Management / Configuration Hub
→ supported Workflow backup/deploy capabilities

External source control
→ engineering practice for reviewable history
```

Keeping exported Workflow definitions in source control can give a team useful history, peer review, and comparison outside the product UI.

That is a recommendation, not a SailPoint requirement.

### Do not assume references are portable unchanged

Suppose the Acme test tenant contains a source with one identifier and production contains the corresponding source with another.

A reference that works in test is not automatically correct in production.

The safe rule is:

> **Do not assume tenant object references are portable unchanged.**

Supported configuration tooling can resolve or map some references during promotion.

That does not remove the need for destination validation.

After promotion, ask:

```text
Does this reference resolve to the intended object here?

Does this environment have the required dependency?

Does the credential exist here?

Does this Workflow behave correctly with destination data?
```

That is stronger than blindly replacing every ID, and safer than assuming every ID will work unchanged.

### Secrets move differently

Configuration backups do not simply export sensitive values such as passwords and secret tokens.

That is a feature, not an inconvenience.

It also means promotion planning must include the credential boundary:

```text
definition moved
        ≠
all secure dependencies automatically moved
```

The destination environment may require its own supported credential or parameter setup.

---

## 9. Working Engineer: Scheduled work can collide with itself

A schedule answers:

> When may another execution begin?

It does not necessarily answer:

> Has the previous execution finished?

For **Scheduled Trigger**, SailPoint documents that another execution can begin before the previous execution finishes, depending on the configured schedule.

So compare:

```text
schedule cadence
        ↓
every 2 hours
```

with:

```text
possible execution duration
        ↓
3 hours
```

You now have an operational question:

```text
Can two executions exist at the same time?
```

That is the level of reasoning Module 08 needs.

Do not assume SailPoint will automatically serialize every scheduled execution for you.

And do not solve the whole concurrency problem here.

Later, in Module 11, we will deal with questions such as:

- What if both executions update the same thing?
- What if an action happens twice?
- What state makes replay safe?
- What if two runs race?
- How should retries behave?

For now, recognize the production condition:

> **If execution duration can exceed schedule cadence, overlap is possible and deserves deliberate design review.**

---

## 10. Core: Handoff, governance, and retirement

Eventually, someone other than the original author will operate your Workflow.

Design for that person.

### Name for the person who inherits it

A name such as:

```text
Workflow 17
```

forces the next engineer to open it before learning anything.

A consistent process-oriented convention is easier to operate.

For example:

```text
Mover - Finance - Notify Access Owner
Leaver - Create ServiceNow Ticket
Ops - Aggregation Failure Alert
```

The exact convention is less important than consistency.

### Keep scope understandable

A giant Workflow with unrelated responsibilities is harder to:

- reason about;
- test;
- promote;
- monitor;
- change;
- hand off.

Modularity is therefore an operational property, not only a design preference.

### Document why

Step names and descriptions should explain intent where the definition alone does not.

The next engineer should be able to answer:

- Why is this filter here?
- Why is this delay necessary?
- Which system owns the next step?
- What credential does this action rely on?
- What failure should page someone?
- What value is environment-specific?

Good documentation reduces the number of assumptions the next person must reconstruct.

### A useful handoff record

For an important production Workflow, an operational handoff might capture:

```text
PURPOSE
What business process does it support?

OWNER
Who is accountable now?

SUCCESSOR
Who can inherit it?

DEPENDENCIES
What objects, systems, people, schedules, and credentials matter?

OPERATING ENVELOPE
What limits or volume assumptions matter?

HEALTH EVIDENCE
What signals show normal or abnormal behavior?

CHANGE PROCESS
How do we preserve, review, test, and promote changes?

CREDENTIAL RESPONSIBILITY
Who owns rotation and replacement?

RETENTION REQUIREMENT
What evidence must survive beyond normal execution history?

RETIREMENT CONDITION
How will we know this Workflow should no longer exist?
```

That is governance practice.

ISC does not magically create a complete operating model because a Workflow exists.

### Retirement

A Workflow also needs an end-of-life path.

“Retire” here is an engineering and governance process, not the name of a special SailPoint Workflow feature.

A responsible retirement can look conceptually like:

```text
understand dependencies
        ↓
confirm the process is no longer needed
        ↓
preserve required definition and evidence
        ↓
address owner and credentials
        ↓
deliberately stop future activity
        ↓
delete when appropriate
```

The exact organizational controls will vary.

The important idea is that deletion should be the end of a decision process, not the first step.

---

## 11. Work It Out: You inherit Priya's production Workflow

You join Acme's IAM team and inherit this Workflow:

```text
Identity Attributes Changed
        ↓
detect department move to Finance
        ↓
notify Finance access owner
        ↓
HTTP Request to ticketing platform
        ↓
end
```

The Workflow has been running for more than a year.

Its original creator is leaving.

The ticketing action uses an external credential.

The team wants to make a production change next month.

Security also tells you that evidence for this process may need to be retained longer than ordinary Workflow execution history.

Before changing the Workflow, work through the six operational questions.

### 1. OWNER

What ownership questions do you need answered?

### 2. DEPENDENCIES

What could the Workflow depend on beyond the visible canvas?

### 3. CONSTRAINTS

What operating boundaries would you check rather than assume?

### 4. EVIDENCE

What would tell you that the Workflow is healthy, and what would prove that the downstream business result occurred?

### 5. CHANGE

How would you preserve and promote a known-good definition without assuming destination references and secrets are portable?

### 6. LIFECYCLE

What must be handed off before the current owner leaves, and what should remain documented for the next engineer?

Think through those before opening the answer.

A strong answer does not need to reproduce product documentation.

It should identify the operational boundaries.

**OWNER**

Determine the current Workflow owner and deal with succession before departure. The Workflow owner relationship matters because of the owner-associated PAT. If ownership is reassigned, the Workflow must be disabled and the new owner must be an appropriate `ORG_ADMIN`; reassignment generates a new Workflow PAT.

**DEPENDENCIES**

Inventory the tenant objects and references used by the Workflow, the external ticketing system, the ticketing credential, permissions, notification recipients, and whatever downstream process owns the ticket after creation.

Keep the Workflow PAT separate from the integration credential.

**CONSTRAINTS**

Check current execution volume and relevant Workflow limits rather than assuming last year's operating assumptions are still safe. If the definition, input, or payload is unusually large, verify the current size limits too.

**EVIDENCE**

Use Workflow execution evidence to understand runtime health, but do not stop there. Determine what proves that the ticketing process or downstream access process reached the intended business state.

If evidence must survive longer than Workflow operational history, arrange separate retention.

**CHANGE**

Preserve a known-good definition. Review the change. Account for the fact that the Workflow must be disabled for editing. Do not assume events during that period will later be replayed.

Use supported JSON/configuration-management capabilities as appropriate, validate destination references, establish destination credentials separately where needed, test, enable, and observe the resulting production executions.

**LIFECYCLE**

Document purpose, ownership, successor, dependencies, credentials, health evidence, change expectations, and eventual retirement conditions.

The test is not whether you personally understand the Workflow today.

The test is whether another engineer can operate it safely after you are gone.

---

## 12. Checkpoint: Can another engineer operate it?

You should now be able to look at a production Workflow and reason through:

```text
OWNER
Who is accountable, and what happens when ownership changes?

DEPENDENCIES
What must remain valid outside the visible Workflow?

CONSTRAINTS
What operating boundaries can the design reach?

EVIDENCE
What proves Workflow health, and what proves the business result?

CHANGE
How can the Workflow be changed or promoted without relying on assumptions?

LIFECYCLE
Can another engineer inherit, maintain, and eventually retire it safely?
```

That is the operational step beyond Module 07.

Module 07 taught you to diagnose what happened in an execution.

Module 08 taught you to keep the Workflow itself supportable over time.

Next we ask a different engineering question:

> **Should this requirement be implemented as a Workflow at all?**

---

## Official References

- [Managing Workflows - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-manage.html)
- [Building Workflows - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-build.html)
- [Workflow Triggers - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-triggers.html)
- [Workflow Actions - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-actions.html)
- [Managing Parameter Storage - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/parameter_storage/managing_parameters.html)
- [Configuration Management - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/configuration-management/)
- [SaaS Configuration Support - SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/configuration-management/saas-configuration/)
- [Workflow Execution History API - SailPoint Developer Community](https://developer.sailpoint.com/docs/api/v2026/get-workflow-execution-history)

---

[← Previous: Module 08.1: Operating a Workflow](08-1-operating-a-workflow.md) | [Course home](README.md) | [Next: Module 09.1: Capability Ownership →](09-1-capability-ownership.md)
