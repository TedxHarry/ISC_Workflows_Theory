# Module 02: Data, Payloads, Variables & JSONPath

How to inspect Workflow data, understand its shape, and reference the value you actually have instead of the value you hoped was there.

Module 01 gave you two questions to carry through every Workflow:

```text
CONTROL FLOW
What runs next?

DATA FLOW
What information is available here?
```

This module takes the second question further.

Knowing that data is available is not enough. You need to be able to look at it and answer:

> **What shape is this data, where did this value come from, and how do I reference it without guessing?**

That is the skill we are building.

You are going to see JSONPath later in this module, but JSONPath is not the starting point. A path only makes sense after you understand the structure it is walking through.

So we start one level lower: the data itself.

## A quick terminology boundary

Before we read JSON, I want to keep a few terms separate.

A **trigger payload** or **trigger input** is data supplied by a trigger or event.

A **step input** is the information available to a particular step when that step executes.

A **step output** or **result** is information produced by a step.

**Workflow runtime data** or **data flow** is the broader information made available as an execution progresses.

You will sometimes hear people use *payload* loosely for almost any JSON they are looking at. That is understandable, but it can hide where the data actually came from.

In this course, we will try to name the boundary when it matters.

The engineering question is not only:

> "What field do I need?"

It is also:

> **"Who produced this data?"**

That becomes important as soon as a Workflow has more than one step.

---

## Start with JSON values

A large JSON document is built from a small set of ideas.

For Workflow data, the basic values you will see include strings, numbers, booleans, and `null`.

```json
"Finance"
```

That is a **string**.

```json
42
```

That is a **number**.

```json
true
```

That is a **boolean**.

```json
null
```

That is an explicit **null value**.

A small distinction already matters:

```json
true
```

and

```json
"true"
```

are not the same JSON value.

The first is a boolean. The second is a string containing four characters.

You do not need a programming-language lesson here. Just build the habit of noticing the value you actually received rather than reading everything as text.

---

## Objects: named values

An **object** groups values under named properties.

```json
{
  "department": "Finance",
  "active": true
}
```

This object has two properties:

- `department` → `"Finance"`
- `active` → `true`

The braces `{ }` tell you that you are looking at an object.

When you read an object, think:

> **Which named property contains the value I want?**

That question will later become part of a JSONPath.

For now, stay with the structure.

---

## Nested objects: data inside data

Objects can contain other objects.

```json
{
  "identity": {
    "name": "Priya Patel",
    "attributes": {
      "department": "Finance",
      "email": "priya.patel@acme.com"
    }
  }
}
```

Read it one level at a time.

At the outer level, there is a property named `identity`.

Its value is another object.

Inside `identity`, there is:

- `name`
- `attributes`

And `attributes` is another object containing:

- `department`
- `email`

If I asked where the email lives, the useful answer is not just:

> "under email."

It is:

```text
identity
  → attributes
    → email
```

That is the structure.

Later, JSONPath will simply give us a compact way to write that route.

### Engineering Habit

When you are tempted to write a reference from memory, stop and inspect the real data first.

Do not decide that an email address *should* live under `identity.email`.

Look at what the data actually contains.

If the real nesting is:

```text
identity
  → attributes
    → email
```

then that is the route you must follow.

The JSON wins. Your expectation does not.

---

## Arrays: lists are different from objects

Now look at this:

```json
[
  "Sales",
  "Finance",
  "Engineering"
]
```

The brackets `[ ]` tell you this is an **array**.

An object asks you to choose a named property.

An array asks you to deal with one or more items in a list.

Those are different structures, and that difference changes how you reference them.

JSON array positions are zero-based:

```text
index 0 → "Sales"
index 1 → "Finance"
index 2 → "Engineering"
```

So the first item is index `0`, not index `1`.

That is worth remembering.

What you should **not** assume is that a business concept automatically owns a particular position.

An array may have a first item. That does not mean "the first item is always department" or "the second item is always manager."

Position and meaning are different things.

### Object or array?

| Shape | Meaning |
|---|---|
| `{ ... }` | object — named properties |
| `[ ... ]` | array — list of items |

When you are lost in a payload, identifying which of those two shapes you are looking at is often the fastest way forward.

---

## Arrays of objects: Priya's mover data

Arrays become more interesting when each item is itself an object.

When identity attributes change, a representative **Identity Attributes Changed** event can contain a `changes` array.

Priya moves from Sales to Finance at the same time her manager changes:

```json
{
  "identity": {
    "id": "2c9180...",
    "name": "Priya Patel",
    "type": "IDENTITY"
  },
  "changes": [
    {
      "attribute": "manager",
      "oldValue": {
        "id": "a1",
        "name": "Sonia Reed",
        "type": "IDENTITY"
      },
      "newValue": {
        "id": "b2",
        "name": "Marcus Hale",
        "type": "IDENTITY"
      }
    },
    {
      "attribute": "department",
      "oldValue": "Sales",
      "newValue": "Finance"
    }
  ]
}
```

There are several layers here.

`changes` is an **array**.

Each item inside `changes` is an **object**.

Each change object has properties such as:

- `attribute`
- `oldValue`
- `newValue`

And notice something else: `oldValue` and `newValue` do not have one universal type.

For the department change, they are strings.

For the manager change, they are identity-reference objects.

That is exactly why inspecting real data matters.

A field name alone does not tell you its entire shape.

> **For now, treat this only as a data example.** Module 03 will teach what the Identity Attributes Changed trigger represents and when you would choose it.

### Work It Out: Read the structure first

Before we write any JSONPath, answer these from the sample above.

1. Is `identity` an object or an array?
2. Is `changes` an object or an array?
3. What is the first item inside `changes`?
4. Is the manager `newValue` a string or an object?
5. Is the department `newValue` a string or an object?

<details>
<summary>Check your answer</summary>

1. `identity` is an object.
2. `changes` is an array.
3. The first item is an object describing the manager change.
4. The manager `newValue` is an object.
5. The department `newValue` is a string.

If those answers are clear, you have enough structure in your head to begin writing paths.

</details>

---

## Workflow data becomes available step by step

Now connect this back to Module 01.

You already know that a Workflow step can use data made available by the trigger and by previously executed steps.

Think of that as an **availability timeline**, not as a promise that every Workflow is stored as one universal giant JSON object.

```text
Workflow starts
│
├─ Trigger makes starting data available
│
▼
Step A executes
│
├─ Step A may make output available
│
▼
Step B executes
│
├─ Step B may use:
│    - trigger data
│    - available output from Step A
│
▼
Later processing
```

That gives you two dimensions to reason about:

```text
SHAPE
What kind of JSON is this?
Object? Array? Value?

TIME
Has the step that produces it actually executed yet?
```

A perfectly written path still cannot reference future data that does not exist yet.

And a value exposed by a prior step does not magically exist on a runtime path where that producing step never executed.

The Module 01 rule still applies:

> **Think in execution order, not just visual position.**

---

## JSONPath: turn the structure into a route

Now we can introduce JSONPath.

JSONPath is a way to describe a route through JSON data.

The dollar sign `$` represents the root of the JSONPath evaluation context.

Then you follow properties and array selections from there.

Take this simple object:

```json
{
  "identity": {
    "attributes": {
      "email": "priya.patel@acme.com"
    }
  }
}
```

In plain English, the route is:

```text
root
→ identity
→ attributes
→ email
```

Written as a JSONPath:

```text
$.identity.attributes.email
```

Nothing mysterious happened.

The path simply wrote down the nesting you had already identified.

That is why I did not want to start this module with `$`.

If you can read the structure, the path becomes much easier.

---

## Referencing trigger data from a Workflow step

Inside an ordinary running Workflow-step reference, SailPoint documents trigger data under the `trigger` root.

Suppose the trigger input available to the Workflow contains:

```json
{
  "identity": {
    "name": "Priya Patel"
  },
  "attributes": {
    "firstname": "Priya",
    "email": "priya.patel@acme.com"
  }
}
```

A later Workflow step can reference the email with:

```text
$.trigger.attributes.email
```

And the identity reference's `name` with:

```text
$.trigger.identity.name
```

Notice the extra `trigger` segment.

That is part of the **running Workflow reference context**.

The underlying event data contains `identity` and `attributes`.

The later Workflow step reaches that trigger data through the Workflow's `trigger` reference root.

If a previously executed Workflow step produces data for later use, later references can likewise start from that step's **technical step name**.

Conceptually:

```text
$.<technicalStepName>.<field>
```

You do not need to memorize or guess technical step names. We will come back to that when we introduce the Variable Selector.

---

## Array indexes: correct syntax can still be bad reasoning

Now return to Priya's `changes` array.

Inside a running Workflow, this path:

```text
$.trigger.changes[0].newValue
```

means:

```text
trigger data
→ changes array
→ first item
→ newValue
```

Against our example, the first item is the manager change.

So the selected `newValue` is the manager-reference object:

```json
{
  "id": "b2",
  "name": "Marcus Hale",
  "type": "IDENTITY"
}
```

That JSONPath is syntactically meaningful.

It is also wrong if your business requirement was:

> "Give me Priya's new department."

The problem is not JSONPath syntax.

The problem is the assumption.

`changes[0]` means:

> **the first change**

It does not mean:

> **the department change**

SailPoint can provide multiple change objects in one event. If your requirement cares about which attribute changed, position is not the business meaning you should depend on.

This is an important engineering distinction:

```text
index
= select by position

predicate
= select by meaning
```

---

## Select by meaning, not position

A JSONPath predicate can select array items whose properties match a condition.

For Priya's change data, a Workflow-step JSONPath can select change objects whose `attribute` is `department`:

```text
$.trigger.changes[?(@.attribute == "department")]
```

Read that in plain English:

```text
Look in trigger.changes
and select the change object or objects
whose attribute property equals "department".
```

That is different reasoning from `[0]`.

You are no longer asking:

> "What is first?"

You are asking:

> "Which change means department?"

If you continue to:

```text
$.trigger.changes[?(@.attribute == "department")].newValue
```

you are selecting the `newValue` node or nodes belonging to the matching change objects.

Notice the wording: **node or nodes**.

A predicate is a selection. Depending on the data, it may match:

- zero items;
- one item;
- multiple items.

Do not silently turn "my example has one department change" into "this expression is guaranteed to produce one scalar string."

If later design logic requires exactly one value, that is another assumption to validate.

Module 02 only needs you to recognize the selection correctly.

### Work It Out: Position versus meaning

Using Priya's two-change example:

1. What does `$.trigger.changes[0].attribute` select?
2. Why would `$.trigger.changes[0].newValue` be a weak design for a department notification?
3. What does `$.trigger.changes[?(@.attribute == "department")]` ask for?
4. What assumption would you be making if you treated that predicate as guaranteed to return exactly one result?

<details>
<summary>Check your answer</summary>

1. It selects the `attribute` property of the first change object — `manager` in this example.
2. It selects by position, not by the meaning of the change. The first item is not a contract that says "department."
3. It asks for change object or objects whose `attribute` equals `department`.
4. You would be assuming the data always contains exactly one matching change object. The predicate itself does not make that guarantee.

</details>

---

## Missing, null, empty, and usable are different

Now look at this generic JSON:

```json
{
  "manager": null,
  "department": "",
  "groups": [],
  "preferences": {}
}
```

Several different states are represented.

### Present with `null`

```json
"manager": null
```

The `manager` property exists.

Its value is explicitly JSON `null`.

### Present but empty string

```json
"department": ""
```

The `department` property exists.

Its value is a string containing no characters.

### Present but empty array

```json
"groups": []
```

The `groups` property exists.

Its value is an array containing no items.

### Present but empty object

```json
"preferences": {}
```

The `preferences` property exists.

Its value is an object containing no properties.

### Missing

Now imagine trying to reference:

```text
title
```

There is no `title` property in this JSON at all.

That is **missing**, not `null`.

Keep these states separate:

```text
missing
≠
null
≠
empty string
≠
empty array
≠
empty object
≠
usable value
```

And be careful with the last distinction.

"Empty" does not automatically mean "invalid" in every business process. An empty list could be perfectly legitimate.

The point is that these are different data conditions, and your design should know which condition it actually has.

### What happens when a path is missing?

This is where I do **not** want you memorizing an invented universal rule.

A JSONPath selection that finds no matching node is different from selecting a node whose explicit JSON value is `null`.

How a particular Workflow field, action, or operator behaves when given an unresolved or unusable reference can depend on that context.

So the safe engineering statement is:

> **A missing reference did not identify the usable value the step expected. Inspect the actual data and the behavior of the specific field that consumes it.**

Later modules will teach how to validate and respond to these conditions.

For now, your job is to identify them correctly.

---

## Variable Selector: use the helper after you understand the data

You will not always need to type JSONPath manually.

The Workflow Builder provides the **Variable Selector**.

It lets you choose a previous Workflow step and then choose an attribute that step provides. SailPoint generates the corresponding JSONPath expression for you.

That is useful for two reasons:

1. it reduces manual path-writing mistakes;
2. it keeps future steps out of the selection list.

But do not let the tool replace the mental model.

The Variable Selector can help construct a reference. It does not make execution-order rules disappear.

If data came from a branch that did not execute, merely having a reference to that producer does not make its runtime output exist.

So use the Variable Selector with the question you learned in Module 01:

> **Did the step that produces this value actually execute before I need the value?**

And use the question from this module:

> **What shape did that step actually produce?**

### Variable Selector is not Define Variable

One terminology point matters because this module's title contains the word *Variables*.

The **Variable Selector** helps you reference data that is already available.

Later, Module 04 will introduce operators that can define or update variables.

Those are different concepts.

Do not confuse:

```text
select/reference an existing value
```

with:

```text
define or update a Workflow variable
```

### Working Engineer: inline variables and technical step names

SailPoint also supports inline references in text fields using double curly braces around a JSONPath expression.

For example:

```text
Welcome to Acme, {{ $.trigger.attributes.firstname }}
```

Spaces around the expression are optional.

When you write references manually, a previous step may be referenced by its technical step name, which can differ from the friendly label you see on the canvas.

Do not guess those identifiers.

Use the Variable Selector where it is available, and inspect the technical name when manual referencing actually requires it.

You need to recognize this behavior, not memorize naming quirks.

---

## Two JSONPath contexts

You now know enough JSONPath to see an important SailPoint distinction.

A JSONPath expression used **inside a running Workflow step** and a JSONPath expression used **as a trigger filter** do not operate in the same context.

Use Priya's mover data again.

### Context 1: Workflow-step reference

After the Workflow has started, a step referencing the trigger's `changes` data uses the Workflow runtime trigger root:

```text
$.trigger.changes[?(@.attribute == "department")]
```

The `trigger` segment is part of the Workflow-step reference context.

### Context 2: trigger filter

A trigger filter evaluates the event data directly before the Workflow begins for that event.

The corresponding trigger-filter expression is:

```text
$.changes[?(@.attribute == "department")]
```

There is no `$.trigger` wrapper in that filter expression because the filter is evaluating the event payload itself.

That difference is small on the screen and large in practice.

Do not memorize one path and paste it everywhere.

Ask first:

> **Which JSONPath context am I in?**

### A filter decides whether the event matches

There is another subtle distinction worth getting right now.

This filter:

```text
$.changes[?(@.attribute == "department")]
```

uses a selection to decide whether the event matches the filter condition.

Do not assume that it rewrites the event payload so the resulting Workflow receives only the department change object.

A trigger filter is deciding whether the event qualifies to start the Workflow.

Filtering the event and transforming the event into a smaller payload are different ideas.

Module 03 will build directly on this distinction.

---

## Working Engineer: Jayway and JSON Slice

You do not need implementation names to understand the Core lesson.

The Core lesson is:

```text
trigger-filter context
≠
Workflow-step reference context
```

When you work more deeply with SailPoint, the implementation names become useful.

Current SailPoint documentation describes:

- **trigger filters** as using **Jayway JSONPath**;
- normal Workflow action/operator references and the **Variable Selector** as using SailPoint's **JSON Slice** implementation, with RFC 9535 baseline functionality plus SailPoint extensions.

That means a valid-looking expression should not be assumed portable between the two environments.

A function or extension supported in one context may not behave the same way in the other.

There are also special trigger types with additional documented reference constraints.

So do not turn the implementation names into a universal slogan.

The engineering habit is simpler:

> **Know which context you are in and verify syntax against the documentation for that context when the expression becomes more than basic property/index/filter navigation.**

You do not need an implementation-function catalog in your head.

---

## The engineering method: inspect, classify, trace, reference

At this point, you have enough pieces to use a repeatable method.

When you need a value in a Workflow, work through this sequence.

### 1. Identify the producer

Ask:

> **Where did this data come from?**

Was it supplied by the trigger?

Was it produced by a previously executed step?

That establishes the reference boundary.

### 2. Inspect the actual data

Do not reconstruct the payload from memory.

Look at the real trigger input, step output, sample data, or rendered execution data available for the context you are working with.

### 3. Classify the shape

Ask:

```text
Value?
Object?
Array?
Array of objects?
```

Do not write the path until that is clear.

### 4. Follow the real nesting

Walk down the actual properties one level at a time.

If the structure is:

```text
identity
→ attributes
→ email
```

do not invent:

```text
identity
→ email
```

because it sounds reasonable in English.

### 5. If an array is involved, ask what you mean

Do you really want:

> **the first item**

or do you want:

> **the item whose property has a particular meaning**

Use position only when position is actually the requirement.

### 6. Check the data state

Is the value:

- present and usable;
- explicit `null`;
- empty;
- absent?

Do not collapse those into one condition.

### 7. Identify the JSONPath context

Are you writing:

- a Workflow-step reference;
- a trigger filter?

That determines the root/context and implementation rules.

### 8. Then write or select the reference

Only now do you turn the structure into JSONPath or use the Variable Selector to generate the reference.

That order matters.

> **Engineering Habit:** Inspect the actual data instead of guessing its structure.

If you carry one sentence from this module into production work, carry that one.

---

## Work It Out: Read before you reference

Use this representative trigger data:

```json
{
  "identity": {
    "id": "2c9180...",
    "name": "Priya Patel",
    "type": "IDENTITY"
  },
  "changes": [
    {
      "attribute": "manager",
      "oldValue": {
        "id": "a1",
        "name": "Sonia Reed",
        "type": "IDENTITY"
      },
      "newValue": {
        "id": "b2",
        "name": "Marcus Hale",
        "type": "IDENTITY"
      }
    },
    {
      "attribute": "department",
      "oldValue": "Sales",
      "newValue": "Finance"
    }
  ],
  "note": null,
  "tags": []
}
```

### 1. Structure

Which top-level property is an array?

Which value is explicitly `null`?

Which value is an empty array?

<details>
<summary>Check your answer</summary>

- `changes` is an array.
- `note` is explicitly `null`.
- `tags` is an empty array.

</details>

### 2. Workflow-step reference

Inside a running Workflow step, what does this mean?

```text
$.trigger.changes[0].newValue
```

<details>
<summary>Check your answer</summary>

It means:

```text
trigger data
→ changes
→ first item
→ newValue
```

In this sample, that selects the manager-reference object.

It does not mean "new department."

</details>

### 3. Select by meaning

What Workflow-step JSONPath selects the change object or objects whose `attribute` is `department`?

<details>
<summary>Check your answer</summary>

```text
$.trigger.changes[?(@.attribute == "department")]
```

That selection may match zero, one, or multiple objects. The expression itself does not guarantee exactly one.

</details>

### 4. Same event, different context

What would the corresponding trigger-filter path look like?

<details>
<summary>Check your answer</summary>

```text
$.changes[?(@.attribute == "department")]
```

The trigger filter evaluates the event payload directly, so it does not use the running Workflow's `$.trigger` reference root.

</details>

### 5. Missing versus null

If the JSON contains:

```json
"note": null
```

but contains no `title` property at all, are `note` and `title` in the same state?

<details>
<summary>Check your answer</summary>

No.

`note` exists and its value is explicit JSON `null`.

`title` is missing from the sample entirely.

Those are different conditions.

</details>

### 6. Variable Selector reasoning

A Variable Selector allows you to choose a value from an earlier Workflow step.

What two questions should you still ask before trusting the reference?

<details>
<summary>Check your answer</summary>

1. **Did the producing step actually execute on the runtime path that reached this point?**
2. **What data shape did that step actually produce?**

The selector helps build the reference. It does not replace those checks.

</details>

---

## Checkpoint

You should now be able to inspect representative Workflow data and answer:

- Is this a value, object, array, or array of objects?
- What is nested inside what?
- Which step or trigger produced the data?
- Has that producer executed before the value is needed?
- What does a simple JSONPath mean one segment at a time?
- What does `[0]` actually ask for?
- Why can selecting by array position be fragile when your requirement is about meaning?
- What does a simple predicate select?
- Could that predicate match zero, one, or multiple nodes?
- Is the value missing, `null`, empty, or usable?
- What does the Variable Selector help with, and what does it not guarantee?
- Am I writing a Workflow-step reference or a trigger filter?

Most importantly, you should know what to do when a field is not where you expected:

> **Inspect the actual data. Do not guess.**

That is the prerequisite for Module 03.

Now that you can read what a trigger gives you, the next question becomes much more useful:

> **Which trigger represents the business event I actually care about, and what data boundary does that trigger provide?**

That is where Triggers & Filters begins.

---

## Official References

- [Building Workflows — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-build.html)
- [Workflow Triggers — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-triggers.html)
- [Filtering Events — SailPoint Developer Documentation](https://developer.sailpoint.com/docs/extensibility/event-triggers/filtering-events/)

---

[← Previous: Module 01 The Workflow Model](01-the-workflow-model.md) | [Course home](../README.md) | [Next: Module 03 Triggers & Filters →](02-triggers.md)
