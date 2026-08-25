# Module 02.1: Data & Payload Shape
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
| `{ ... }` | object: named properties |
| `[ ... ]` | array: list of items |

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

---

[← Previous: Module 01: The Workflow Model](01-the-workflow-model.md) | [Course home](README.md) | [Next: Module 02.2: Variables & JSONPath →](02-2-variables-and-jsonpath.md)
