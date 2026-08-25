# Module 08.1: Operating a Workflow
Module 07 taught you how to diagnose one execution:

```text
EXPECTED
→ OBSERVED
→ FIRST DIVERGENCE
```

That is the right way to investigate a Workflow when something goes wrong.

Production operation asks a different question.

Suppose Priya's mover Workflow has been running successfully for six months.

Who owns it now?

What systems and credentials does it depend on?

How much activity can it safely handle?

How would Acme know if the Workflow itself is healthy but the ticketing system behind it is not?

What happens when the engineer who built it leaves?

How do you change it without turning a working process into an incident?

Building a Workflow is one skill. Operating a growing collection of them responsibly is another.

From this point forward, treat a production Workflow as an **asset with an owner, dependencies, constraints, evidence, change history, and lifecycle**.

That gives us six operational questions:

```text
OWNER
Who is responsible for it?

        ↓

DEPENDENCIES
What must remain available and valid?

        ↓

CONSTRAINTS
What operating boundaries can it reach?

        ↓

EVIDENCE
How do we know it is healthy?

        ↓

CHANGE
How can we modify or promote it safely?

        ↓

LIFECYCLE
How is it handed off or retired?
```

You do not need to memorize every current product limit in this module.

You do need to learn how an engineer discovers the operating boundary, decides what evidence matters, and leaves the Workflow supportable for the next person.

---

## 1. Core: From one execution to a production asset

A Workflow can work perfectly today and still be poorly operated.

Imagine Acme has a Workflow that reacts when an employee moves into Finance.

It:

1. detects the department change;
2. checks the values it received;
3. notifies the Finance access owner;
4. calls an external ticketing system;
5. records the resulting process.

You already know how to investigate one execution of that Workflow.

Operations asks you to look beyond one execution.

```text
ONE EXECUTION

What happened?
Where did it diverge?
What did the action prove?

                ↓

PRODUCTION ASSET

Who owns it?
What can break around it?
How much can it handle?
What evidence shows health?
How do we change it?
Who takes responsibility next?
```

A Workflow that nobody can safely change, support, or inherit is not mature merely because today's execution is green.

That is the mindset for this module.

---

## 2. Core: The six operational questions

When I inherit a Workflow I did not build, I do not begin by reading every box on the canvas.

I first want to understand its operational shape.

### Owner

Who is accountable for this Workflow?

Who should respond when it fails?

Who takes over if the current owner leaves?

### Dependencies

What does the Workflow require in order to keep working?

That may include:

- ISC objects and references;
- source or access configuration;
- external APIs;
- credentials;
- permissions;
- human reviewers or recipients;
- schedules;
- downstream provisioning;
- another governed process.

### Constraints

What limits its operating envelope?

Volume is one constraint.

Definition and payload size are others.

Schedule cadence can become another.

### Evidence

What tells us the Workflow is behaving normally?

A completed execution is evidence.

It is not necessarily enough evidence.

### Change

How do we modify it without losing our known-good state or making assumptions about another environment?

### Lifecycle

How will ownership transfer?

What must be preserved?

When the Workflow is no longer needed, how do we remove it deliberately?

These six questions are more durable than any particular product screen.

---

## 3. Core: Who owns this Workflow?

Ownership is not just a name displayed beside a Workflow.

It has operational consequences.

When a Workflow is created, its creator becomes its initial owner. SailPoint also creates a personal access token associated with that Workflow.

Conceptually:

```text
Workflow created
        ↓
creator becomes owner
        ↓
Workflow-associated PAT exists
```

That means the owner is part of the Workflow's runtime environment.

### What happens when the owner leaves?

Suppose the administrator who built Acme's Finance mover Workflow leaves the company.

SailPoint documents that the Workflow can become **orphaned** and its associated PAT becomes invalid.

Executions **might** then fail with authorization errors.

Notice the wording.

```text
owner leaves
        ↓
Workflow may become orphaned
        ↓
PAT becomes invalid
        ↓
executions might fail with authorization errors
```

Do not turn that into a stronger claim such as:

> Every Workflow immediately stops the moment its creator leaves.

That is not the documented boundary.

The engineering lesson is simpler:

> **Ownership has to be managed before departure becomes an incident.**

Ownership can be reassigned to another `ORG_ADMIN`. The Workflow must be disabled for that reassignment, and a new Workflow PAT is generated for the new owner.

That makes succession planning part of normal Workflow operation.

### An engineering practice on top of the product behavior

SailPoint gives the Workflow an owner.

Your organization should decide more than that.

For an important production Workflow, I would want to know:

```text
Primary operational owner
Who is responsible today?

Successor
Who can inherit it?

Escalation path
Who responds if its dependencies fail?
```

That is governance practice rather than a special SailPoint feature.

The distinction matters.

---

> **Work It Out**
>
> An administrator named Alex created Acme's offboarding Workflow two years ago.
>
> Alex is leaving next Friday.
>
> The Workflow is still enabled and business-critical.
>
> Someone says:
>
> “The Workflow definition still exists, so nothing needs to be done.”
>
> What assumption are they making?
>
> They are treating ownership as descriptive metadata rather than operational state.
>
> The Workflow has an owner-associated PAT. Creator departure can orphan the Workflow, invalidate that PAT, and might lead to authorization failures.
>
> The team should address ownership deliberately before relying on the Workflow after Alex's departure.

---

## 4. Core: What does it depend on?

A production Workflow rarely stands alone.

Consider Priya's mover Workflow again.

The canvas may look self-contained:

```text
department changed
→ compare new department
→ send notification
→ create ticket
→ end
```

Operationally, it may depend on much more:

```text
identity event
        ↓
correct tenant objects
        ↓
valid references
        ↓
Workflow owner credential
        ↓
integration credential
        ↓
external ticketing API
        ↓
network/service availability
        ↓
human process after ticket creation
```

A failure anywhere in that chain can affect the business process.

### Think in dependency categories

For an important Workflow, identify at least these categories when they apply:

**ISC objects**

Sources, identities, access objects, forms, policies, or other tenant objects the Workflow references.

**External systems**

Ticketing platforms, messaging systems, APIs, or other services called by the Workflow.

**Permissions**

The Workflow or integration must still be authorized to perform the required work.

**People**

An approval, form, recipient, owner, or operational responder may be part of the process.

**Schedules**

A Scheduled Trigger introduces timing and cadence as dependencies.

**Credentials**

Credentials expire, rotate, change ownership, or stop being valid.

**Downstream processes**

A Workflow may submit work that another ISC process or external system must later complete.

### Two credential boundaries

Do not collapse every credential into one idea.

A Workflow owner PAT and an external integration credential solve different problems.

```text
WORKFLOW OWNER / RUNTIME CREDENTIAL

owner-associated Workflow PAT
→ tied to Workflow ownership
→ regenerated when ownership is reassigned


INTEGRATION CREDENTIAL

credential used by an action
→ authenticates to another service
→ has its own lifecycle
→ may use Parameter Storage where supported
```

Changing one does not imply anything about the other.

### Parameter Storage

For supported actions and parameter types, SailPoint provides **Parameter Storage** as a secure mechanism for privileged parameters.

For example, supported HTTP Request authentication can use stored parameters for mechanisms such as Basic Authentication, Custom Authorization, and OAuth 2.0 Client Credentials Grant.

That is preferable to embedding a password, client secret, or authorization value directly in a Workflow definition when a supported secure parameter mechanism is available.

The useful rule is:

> **Use Parameter Storage where the action and documented parameter type support it.**

Do not expand that into:

> Every possible Workflow secret belongs in Parameter Storage.

Supported types and availability matter.

### Secret lifecycle is still a human responsibility

Secure storage does not eliminate operational ownership.

Someone still needs to know:

- what the credential is for;
- who owns it;
- when it should rotate;
- what will be affected when it changes;
- how the replacement is established in another environment.

That is the difference between **storing a credential securely** and **operating the dependency responsibly**.

---

---

[← Previous: Module 07: Testing, Debugging & Execution](07-testing-debugging-and-execution.md) | [Course home](README.md) | [Next: Module 08.2: Limits, Change & Governance →](08-2-limits-change-and-governance.md)
