# Module 01: The Workflow Model

How a Workflow is organized, how execution moves through it, and why data can only be used after it becomes available.

Module 00 ended with a question:

> **If Workflow really is the right capability, what does one actually look like?**

That is our job now.

We are not going to begin with syntax or a catalog of product features. First I want you to watch one small Workflow from beginning to end. Once you have the whole process in your head, the terminology has somewhere useful to attach.

## One whole Priya Workflow, start to finish

Acme wants a simple process for new identities.

After ISC detects and creates Priya's identity through the relevant authoritative-source processing, the **Identity Created** event can start a Workflow.

Acme wants that Workflow to send Priya a welcome email.

Nothing more.

Keeping this small is deliberate. Right now you are learning the model, not trying to design a production joiner process.

Conceptually, the Workflow looks like this:

```text
Identity Created
     ↓
starting context/data
     ↓
Send Welcome Email
     ↓
Success
```

The trigger establishes the starting context for this execution. For an event such as Identity Created, that includes structured information about the identity and its configured identity attributes.

At Acme, assume Priya's available identity data includes the email address needed by the Send Email step.

The Send Email action uses that available value rather than having Priya's address typed permanently into the Workflow.

Then execution reaches the Success end step.

That is enough to understand one complete Workflow:

- something started it;
- data was available;
- a step performed work using that data;
- execution reached an end.

Hold that picture for a moment. Now we can name the pieces.

## The building blocks

SailPoint groups Workflow steps into three categories:

- **triggers**
- **actions**
- **operators**

A completed Workflow has exactly one trigger, at least one action, and one or more end steps. Other operators appear when the process needs them.

### Trigger: what starts the Workflow

The **trigger** establishes when the Workflow begins.

There is exactly one trigger per Workflow.

In Priya's example, the trigger is **Identity Created**.

For now, think of the trigger as doing two jobs:

1. establishing the starting boundary for execution;
2. providing the starting context or input that the Workflow can use.

Different triggers have different kinds of starting context. We will study those distinctions properly later.

You do not need the trigger catalog yet.

### Action: work the Workflow performs

An **action** performs a task.

Send Email is an action.

Other actions can retrieve information, send notifications, call services, or change data or state depending on what that particular action is designed to do.

The useful beginner shorthand is:

> **action = do some work**

Do not turn that into “every action changes an external system.” Some actions retrieve or process information rather than creating an external side effect.

Module 05 will examine action families and what their results actually guarantee.

### Operator: control or shape execution and data

An **operator** helps control the Workflow or work with its data.

Some operators compare values and choose a path. Others support loops, variables, validation, or ending the Workflow.

For our mental model, a decision is the easiest operator example.

Suppose Acme changed the welcome process:

> Send one message to Finance hires and another message to everyone else.

Now the Workflow needs to evaluate information and choose a path.

Conceptually:

```text
Identity Created
       ↓
   Check department
      ↙       ↘
 Finance     Other
    ↓          ↓
 Send A      Send B
      ↘      ↙
       Success
```

You are not learning how to configure that branch yet.

Just recognize the role:

> **an operator can influence how execution proceeds or how Workflow data is handled.**

Detailed comparison and branching logic belongs in Module 04.

## Two things move through a Workflow

This distinction will save you a lot of confusion later.

When I look at a Workflow, I mentally separate **control flow** from **data flow**.

### Control flow: what runs next?

Control flow is the route execution takes through the configured Workflow.

In the simple welcome Workflow:

```text
Identity Created
       ↓
Send Welcome Email
       ↓
Success
```

The question is:

> **Which configured step or path executes next?**

A simple Workflow may look like a straight line.

A larger Workflow may contain decisions, loops, error paths, or branches. You do not need those mechanics yet. The useful idea is that execution follows the connections and paths defined by the Workflow until it reaches an end step.

### Data flow: what information is available here?

Data flow asks a different question:

> **What information can this executing step use?**

The Workflow begins with starting context supplied by its trigger.

As execution continues, previously executed steps can make additional data available to later steps.

So at any point in the Workflow, I want you to ask two separate questions:

1. **Where can execution go next?**
2. **What data is available at this point?**

Those questions are related, but they are not the same.

That distinction becomes especially useful once Workflows begin branching.

## Why order creates data dependencies

Consider a slightly different Workflow:

```text
Trigger
   ↓
Get Information
   ↓
Make Decision
   ↓
Send Message
   ↓
Success
```

Suppose **Get Information** produces a value that **Make Decision** needs.

That works because Get Information executed first and made the value available before Make Decision needed it.

Now reverse the dependency.

Suppose Get Information somehow needs a value that will only be produced later by Send Message.

That cannot work.

When Get Information executes, Send Message has not executed yet. Its future output does not exist yet for the earlier step to use.

That gives us a foundational rule:

> **A step can use data made available by the trigger or by steps that executed before it. It cannot depend on output that has not been produced yet.**

Notice that I said **executed before it**, not simply “appears above it on the canvas.”

That wording matters.

As Workflows become more complicated, a step can exist somewhere in the definition without having executed on the path the current run followed.

For now, keep the simpler habit:

> **Think in execution order, not just visual position.**

### Engineering Habit

Before configuring a step to use another step's output, ask:

> **Will that value actually exist by the time this step runs?**

That question is more useful than memorizing syntax.

Module 02 will teach you how to inspect and reference the actual value once you know it should exist.

## Start, connected processing, and end

Once the trigger starts an execution, the Workflow has a configured starting step.

From there, control follows the Workflow's configured connections and paths.

A simple version looks like:

```text
Trigger
   ↓
Start step
   ↓
More processing
   ↓
End step
```

Not every Workflow is a single straight chain. Decisions and other operators can create multiple possible paths.

The general model still holds:

```text
trigger
   ↓
starting context
   ↓
connected processing
   ↓
one of the configured paths
   ↓
end
```

Workflows use **Success** and **Failure** as end operators.

These steps stop execution and mark the Workflow execution's status.

Keep that statement narrow for now.

A Success end tells you that the **Workflow execution** ended in Success. Module 05 and Module 07 will later teach you why execution status and the final business outcome are not automatically the same fact.

At this stage, you only need to recognize that every execution path eventually needs an ending.

## Workflow definition and Workflow data are different things

There are two concepts that both eventually involve structured data, and beginners often blend them together.

I want you to separate them now.

### Workflow definition

The **Workflow definition** describes how the Workflow is configured.

Conceptually, it describes things such as:

- its trigger;
- its executable steps;
- where execution begins;
- how those steps and paths are connected.

The visual Workflow Builder gives you a canvas for working with that structure.

There is also a structured JSON representation behind Workflow configuration and APIs.

You do **not** need to memorize its exact object hierarchy here.

In fact, you should not.

The exact representation can depend on which SailPoint interface or object model you are looking at, and that detail is not what Module 01 is trying to teach.

What matters today is simply:

> **The canvas represents a structured Workflow definition.**

### Runtime Workflow data

Runtime data is different.

It is the information available while one particular Workflow execution is running.

For Priya's execution, that might include starting identity information and data later steps make available.

For another person's execution, the Workflow definition may be identical while the runtime values are different.

Think of it this way:

```text
Workflow definition
= the process that was designed

Workflow runtime data
= the information that particular execution is working with
```

The definition tells ISC **what process exists**.

Runtime data gives that execution **values to work with**.

Do not worry about JSON syntax yet. Module 02 exists specifically to make that data comfortable to read.

### Working Engineer preview

Later, you will care about the formal Workflow representation because definitions can be inspected and managed outside the visual canvas.

That matters for engineering and operations.

It does not need to occupy space in your memory yet.

For now, understanding that the structured definition exists is enough.

## Put the model together

You can now expand the simple picture from Module 00.

There, Workflow looked like:

```text
something happens
        ↓
coordinated processing follows
```

Now you can see inside it:

```text
Trigger
  ↓
starting context/data
  ↓
Action
  ↓
Decision or other processing
  ↓
more actions / paths
  ↓
End
```

And you can ask two questions all the way through:

```text
CONTROL FLOW
What runs next?

DATA FLOW
What information is available here?
```

That is the Workflow model I want you carrying into the rest of the course.

Not JSONPath.

Not a memorized object schema.

Not a catalog of every trigger or action.

The model.

## Work It Out: Read the Workflow

Consider this conceptual Acme Workflow:

```text
Identity event
      ↓
Get Manager Information
      ↓
Check Department
    ↙            ↘
Finance          Other
   ↓               ↓
Send Finance     Send Standard
Message          Message
    ↘             ↙
        Success
```

Before reading the answers, reason through these five questions.

### 1. What starts the process?

The **trigger** represented by the identity event.

You do not need to know which exact identity trigger is appropriate from this diagram alone. Trigger selection comes later.

### 2. Which steps are performing work, and which one is controlling a decision?

**Get Manager Information** and the two Send steps are actions performing tasks.

**Check Department** represents an operator evaluating information and influencing the path.

### 3. Can Check Department use information produced by Get Manager Information?

Yes, assuming Get Manager Information executed first and made that information available.

The dependency points backward to something that already happened.

### 4. Can Get Manager Information depend on output that will only be produced by Send Finance Message?

No.

At the time Get Manager Information executes, that later Send step has not executed and has not produced that output.

### 5. What is the difference between control flow and data flow in this diagram?

**Control flow** tells you which path execution follows, such as Finance versus Other.

**Data flow** tells you what information is available to each executing step along that path.

If you can explain that difference without writing a single JSONPath expression, you have the right foundation.

## Checkpoint

You should now be able to look at a simple Workflow and explain:

- what starts it;
- what actions do;
- what operators broadly contribute;
- how control moves through connected processing;
- what data is available as execution progresses;
- why previously executed-step data can be used later;
- why future output cannot be used before it exists;
- the difference between the Workflow definition and one execution's runtime data;
- where execution eventually ends.

You do **not** need to know how to write a path to that data yet.

That is the next problem.

Module 02 starts with the data itself: values, objects, nested structures, and arrays. Once you can confidently see the shape of the information, we will teach you how a Workflow points to the exact value it needs.

---

[← Previous: Module 00 Orientation](00-orientation.md) | [Course home](README.md) | [Next: Module 02 Data, Payloads, Variables & JSONPath →](02-data-variables-and-expressions.md)
