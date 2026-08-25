# Module 00: Orientation

Where Workflows fit in Identity Security Cloud, what you need before starting, and how this course will teach you to think about Workflow engineering.

Before we open a Workflow, I want you to have one picture in your head:

**Workflow is a tool for coordinating processing. It is not the answer to every automation problem in ISC.**

That distinction matters from the beginning. Learning where Workflow fits will save you from becoming very good at building the wrong thing.

This course is going to teach you both sides of that problem: how Workflows work, and how an engineer decides whether Workflow should own a requirement at all.

## Meet Acme and Priya

Throughout the course we will keep returning to one company and one person.

The company is **Acme**. The person is **Priya**.

Priya joins Acme. ISC eventually has an identity representing her, with attributes and accounts associated with that identity. A few months later she moves from Sales to Finance, so some of that identity data changes. Later she leaves the company, and Acme has to deal with her access and accounts appropriately.

Joiner. Mover. Leaver.

We will use those moments because they give us something concrete to reason about. When you later see a phrase such as “identity attributes changed,” I would rather you picture Priya moving to Finance than try to memorize an abstract definition.

Priya is our learning thread, though, not the boundary of what Workflows can do. Real Workflow scenarios also involve access requests, provisioning events, aggregations, forms, scheduled processing, integrations, governance events, and other situations we will meet later.

For now, Priya gives us a person to follow while the engineering ideas are still new.

## What a Workflow is for

Identity Security Cloud already does a lot of work around identities and access. It loads account information from sources, maintains identity information, supports access requests and certifications, and drives provisioning processes.

A Workflow sits alongside those capabilities.

At a high level, a Workflow lets ISC coordinate a sequence of processing when its configured starting condition occurs.

Keep the mental model simple for now:

```text
something happens
        ↓
coordinated processing follows
```

Module 01 will open that box and show you what the pieces are. You do not need trigger catalogs, actions, operators, payloads, or JSONPath yet.

Think instead about the business problem.

Suppose Acme has a process around a new employee. After ISC detects the relevant identity event, Acme may want to notify someone, gather additional information, call another service, or coordinate several related steps.

Without orchestration, those activities may depend on people noticing an event and manually coordinating the next steps.

A Workflow can automate some or all of that coordination.

Notice the wording: **coordination**.

A Workflow does not mean humans can never be involved. Some Workflow designs can be initiated by a person or deliberately wait for human input. The useful idea is that the overall process no longer has to depend on somebody remembering and manually driving every transition.

There is another distinction I want you to keep from the start.

When you hear:

> “When X happens, we need Y to happen.”

do **not** immediately translate that into:

> “We need a Workflow.”

What you have identified is an automation or orchestration requirement.

Your next question is:

> **Which ISC capability should own it?**

That question will become much more important as the course progresses.

> **Engineering Habit:** Do not begin with “How do I build this in Workflow?” Begin with “What kind of problem is this, and which capability should own it?”

## Workflow is one tool in ISC

This is where engineers begin separating similar-sounding requirements.

Imagine four different problems at Acme.

### Calculate or shape a value

Priya's source provides a department code such as `fin`, but Acme wants an identity attribute derived or formatted differently.

That is the kind of problem **Transforms** are designed around.

Transforms calculate, select, format, derive, and otherwise shape attribute values. Some transform operations can also use conditional or fallback logic.

That does not make a Transform a general-purpose process orchestrator.

If the main question is:

> “What should this value be?”

a Transform is one of the first capabilities I would consider.

### Determine or govern access

ISC also has native access-model and governance capabilities for deciding, requesting, reviewing, and governing access.

You do not need that architecture yet.

For now, recognize the boundary: if the requirement is fundamentally about **who should receive access or how that access should be governed**, do not assume a Workflow should replace the ISC capability designed to own that decision.

We will make this distinction much sharper later in the course.

### Carry out an account or access change

Suppose Priya leaves and an account needs to be disabled.

That moves us into **provisioning**.

Provisioning is the ISC process responsible for carrying account and access changes toward the applicable source or fulfillment mechanism. Depending on the source and configuration, fulfillment may be automatic or may require manual work.

One subtle point matters even at this early stage:

**provisioning activity is not automatically the same thing as independently proving the final target state.**

You do not need the full engineering consequences of that distinction yet. We will return to it when we study actions, execution, and production behavior.

### Coordinate a process

Now suppose an ISC event should cause Acme to notify a team, evaluate information, call another service, wait for something, and continue processing.

That sounds much more like **Workflow orchestration**.

The question is no longer just:

> “What should this value be?”

or:

> “Which account change needs fulfillment?”

There is a process to coordinate.

That is where Workflow becomes a natural candidate.

The habit I want you to develop is not memorizing four definitions. It is learning to identify the **kind of problem** in front of you.

### Working Engineer preview: other extension options

You will eventually encounter requirements that do not fit neatly into those first three categories.

**Rules** provide supported custom logic at particular ISC extension points. Different Rule types have different execution and deployment models, and they bring additional support and maintenance considerations. For now, just recognize that Rules exist and that native ISC capabilities are preferable when they already solve the requirement.

ISC also supports **external Event Trigger subscriptions**. Some event types overlap with events that can start Workflows, allowing an external service to react outside the Workflow runtime. The two mechanisms are related, but their trigger catalogs and execution models are not one-to-one.

That is enough for Module 00.

You do not need to choose among all of these mechanisms confidently yet. Later modules will give you the technical knowledge to make that judgment.

## What you need before starting

I am going to assume that you know a few basic ISC ideas.

You should be comfortable with the idea that an identity represents an access-holding entity such as Priya, that identities have attributes, and that identities can be associated with accounts on sources.

That level is enough to begin.

Some JSON familiarity will help, but **JSON is not an entrance exam for this course**.

Workflow data flow and step input/output are generally represented as structured JSON, so reading data confidently will matter. The course will teach that deliberately. Module 01 lets you see Workflow data in context, and Module 02 slows down and builds the data model properly.

If JSON still looks unfamiliar today, keep going.

Basic awareness of REST and APIs will also help later when we reach external integrations. You do not need to understand HTTP integration design before beginning the course.

And you do not need an ISC tenant for this theory course.

The goal here is to build the mental model first. Hands-on implementation belongs in the separate practical material.

## How this course develops you

The course moves through four stages:

**Understand → Build → Operate → Engineer**

### Understand

First, you learn what a Workflow is, how its data behaves, and how to recognize the events that start processing.

At this stage I will guide you closely and tell you what can safely wait.

### Build

Then you learn the building blocks: conditions, logic, actions, error paths, forms, approvals, and human interaction.

You will start answering more of the questions yourself instead of receiving the answer immediately.

### Operate

A Workflow that looks sensible on a diagram still has to survive execution.

You will learn how to investigate what actually happened, understand failures, respect limits, and treat Workflows as production assets rather than diagrams that happen to run.

### Engineer

By the later modules, the question changes.

Instead of:

> “Which block do I add?”

you will increasingly ask:

> “Would I accept this design in production, and why?”

You will compare designs, find hidden assumptions, question success boundaries, think about repeated execution, and sometimes conclude that Workflow is not the right capability.

That progression is intentional. I will do more of the guiding at the beginning. By Module 12, you should be doing much more of the reasoning.

## How to read the difficulty labels

Not everything in this course deserves equal space in your memory.

You will see four labels used when they help control the learning load.

**Core** means I expect you to understand the idea on your first serious pass through the course.

**Working Engineer** means the material becomes important when you are designing or supporting real Workflows, but you do not need every detail before continuing.

**Advanced** means you should recognize the design problem and know that it exists. You can return when your work actually requires that depth.

**Reference** is material you normally look up rather than memorize, especially changing product details such as particular limits, timeouts, or operational behavior.

If you encounter an Advanced or Reference section later and think, “I understand why this matters, but I would need to look up the details,” that is often exactly the right outcome.

An engineer who knows **what to verify** is more useful than one who memorized an old number.

## Seven questions you will grow into

By the end of this course, I want you to be able to look at a Workflow requirement and work through seven questions:

1. **What actually starts this process?**
2. **What data do I have, and what is missing?**
3. **What decisions need to be made?**
4. **What actions belong here?**
5. **What can fail?**
6. **What happens if this runs twice or concurrently?**
7. **What evidence proves the intended business outcome?**

Do not try to answer all seven today.

Some of them probably sound obvious. Others may not mean much yet.

That is intentional.

Each part of the course will give those questions more meaning. We will bring them together properly in Module 12, when you design Workflows on paper and defend the reasoning behind them.

For Module 00, I only want you to notice the pattern:

**Workflow engineering is bigger than connecting steps.**

The engineer has to understand the event, the data, the decisions, the actions, the failure boundaries, repeated execution, and the evidence of success.

One piece at a time.

## Work It Out: Which capability owns the problem?

Consider three Acme requirements.

### Scenario 1

When ISC processes the event representing a new Acme identity, Acme wants to notify the hiring manager and coordinate several follow-up activities.

What kind of problem is this?

This is primarily **orchestration**, so Workflow is a natural capability to evaluate.

The reason matters more than the label: an event starts a process involving subsequent coordinated work.

### Scenario 2

Acme receives Priya's name from an authoritative source and wants a display-name attribute calculated as:

```text
Patel, Priya
```

What kind of problem is this?

This is primarily **value calculation and shaping**, so a Transform is the natural place to look first.

There is no need to build a process simply to calculate a value.

### Scenario 3

Priya leaves Acme and her target account needs to be disabled through the applicable fulfillment process.

What kind of problem is this?

That is primarily a **provisioning** concern.

A Workflow might participate in a larger leaver process, but the account change itself belongs to the provisioning mechanism that owns fulfillment for that source.

Now look back at the three answers.

The useful skill is not saying:

> Workflow. Transform. Provisioning.

The useful skill is explaining:

> orchestration. value calculation. account-change fulfillment.

Once you understand the problem category, choosing the product capability becomes much easier.

## Checkpoint

You should now be able to hear a simple ISC requirement and ask:

> **What kind of problem is this, and which capability should own it?**

You should recognize Workflow as a strong candidate for orchestration without treating it as the automatic answer to every automation requirement.

You should also understand where this course is taking you: from understanding the model, to building with it, to operating it, and eventually to defending engineering decisions independently.

The next question is the natural one:

> **If Workflow really is the right capability, what does one actually look like?**

That is where Module 01 begins.

## Official References

- [Workflows - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/index.html)
- [Building Workflows - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-build.html)

---

[Course home](README.md) | [Next: Module 01: The Workflow Model →](01-the-workflow-model.md)
