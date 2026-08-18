# Module 06: Data, Variables, and Expressions

Working with the JSON payload, and pointing at any piece of it with confidence.

Every module so far has leaned on JSONPath and quietly promised that this one would explain it properly. Here we pay that off. This is the module where data handling stops being something you copy from an example and starts being something you can reason about, because reliable data handling is the real line between a workflow that works and one that fails in ways you cannot explain. We keep following Priya, because her data is the perfect teacher.

## What the workflow is really holding

Go back to the picture from Module 01. A workflow starts with JSON delivered by the trigger, and steps can add more JSON to the data flow as the workflow runs. At any point, later steps can reference data that already exists in that flow.

The trigger's data is available under the trigger step, and later actions or operators add output under their own step names. A simplified shape looks like this:

```json
{
  "trigger": {
    "identity": { "type": "IDENTITY", "id": "2c9180...", "name": "priya.patel" },
    "attributes": { "firstname": "Priya", "lastname": "Patel", "email": "priya.patel@acme.com", "department": "Sales" }
  },
  "getManager": {
    "name": "sam.jones",
    "email": "sam.jones@acme.com"
  }
}
```

That is why Priya's email can be referenced as `$.trigger.attributes.email`, while output from a later step named getManager can be referenced from that step's path. Once you see the workflow as a growing data flow with each step contributing its output, every path has an obvious starting point.

And remember from Module 02 that the data under the trigger is different for each kind of event. Priya's joiner carries identity attributes. Her mover carries a `changes` array. An aggregation carries status and statistics. So the first thing to do for any workflow is inspect the trigger's actual sample or runtime payload rather than writing paths from memory.

## Reading a single value

The simplest path walks down through named keys one level at a time. To read Priya's login name, use `$.trigger.identity.name`. To read her department, use `$.trigger.attributes.department`.

The Module 01 trap is worth saying once more because it never stops being true. Her login name is under `identity`, but her email is under `attributes`. Those are different branches of the JSON. `$.trigger.identity.email` points at nothing if there is no email field there. When a path returns nothing, stop guessing and inspect the real JSON.

## Reading from arrays

Single values are easy. The moment your data holds a list, you need to reason about the array rather than pretend it is one object. Priya's Identity Attributes Changed payload carries a `changes` array:

```json
{
  "changes": [
    { "attribute": "department", "oldValue": "Sales", "newValue": "Finance" }
  ]
}
```

One option is an index. The first item is index zero, so `$.trigger.changes[0].newValue` reads the first change's new value. Indexing is simple and can also be fragile because more than one attribute can change in the same event. If title and department both change, assuming that department is always item zero creates a bug that depends on array order.

Another option is selecting multiple array entries, such as using a wildcard or an array selection supported by the workflow JSONPath implementation, then handing that collection to later logic or a loop.

Trigger filters also support predicate expressions. For example, a filter can select a change where the attribute is department:

```
$.changes[?(@.attribute == "department")]
```

A lifecycle transition filter can be more specific:

```
$.changes[?(@.attribute == "cloudLifecycleState" && @.newValue == "terminated")]
```

The important engineering rule is not to memorize syntax in isolation. Know which JSONPath environment you are in, use expressions documented for that environment, and test them against the real payload.

> **Work It Out**
>
> Priya's move triggers an Identity Attributes Changed event whose `changes` array holds two entries, because her manager was reassigned at the same time:
>
> ```json
> {
>   "changes": [
>     { "attribute": "manager", "oldValue": { "id": "a1", "name": "sonia.reed" }, "newValue": { "id": "b2", "name": "marcus.hale" } },
>     { "attribute": "department", "oldValue": "Sales", "newValue": "Finance" }
>   ]
> }
> ```
>
> Using this payload, what does `$.trigger.changes[0].newValue` return, why is that a problem for a mover alert that cares about department, and how would you select the department change without depending on its position?
>
> <details>
> <summary>Check your answer</summary>
>
> Here `$.trigger.changes[0].newValue` returns the manager object, not the department, because the manager change happens to sit first in the array. Any logic that assumes department is item zero breaks the moment the order shifts, which is exactly the fragile indexing this section warns about. Select the department change by matching the attribute rather than the position, for example with a predicate such as `$.trigger.changes[?(@.attribute == "department")].newValue`, and test it against the real payload before relying on it.
>
> </details>

## Two JSONPath implementations

This is the distinction earlier modules kept flagging.

Trigger filters use the **Jayway** JSONPath implementation. The filter runs against the trigger event payload and determines whether the workflow should start for that event. This is why trigger-filter examples often reference fields directly from the event shape rather than from a later workflow-step wrapper.

Actions and operators use SailPoint's **JSON Slice** implementation of JSONPath, which is currently documented as supporting **RFC 9535 baseline JSONPath functionality plus SailPoint extensions**. This is the implementation used by the Variable Selector and by JSONPath expressions inside workflow steps.

The two environments are related but not identical. SailPoint explicitly documents that trigger filters use a different implementation from actions and operators. So do not assume that a filter expression can be copied unchanged into a later step, or that a function supported in a workflow step is automatically supported in a trigger filter.

The practical rule is simple: use the trigger filter to decide whether the event should start the workflow, and use the workflow-step JSONPath syntax documented for actions and operators to read data after the workflow has started.

## Writing paths without typing them: inline variables and the Variable Selector

You will place references in two ways. Inside a text field, such as an email body, you can write an inline variable with double curly braces around a JSONPath expression, for example `{{ $.trigger.attributes.firstname }}`. When the workflow runs, the expression is resolved and inserted into the text.

There is one naming quirk that surprises people. Step technical names can look different from the friendly label you typed in the builder. A step called "HTTP Request" may appear with a generated technical name such as `hTTPRequest`, and a later reference uses that technical step name. This is a good reason to use the Variable Selector rather than guessing.

The Variable Selector lets you choose a prior step and one of its available values. The builder then inserts the appropriate expression. It also reinforces the chronological rule from Module 01: a step can only reference data that is already available from earlier parts of the workflow.

## Missing and null data, the quiet killer

The most common workflow bug is often not a dramatic crash. It is a path that points at a field that is missing or empty, leaving a later step with no useful value.

Real identity data is incomplete more often than demos suggest. As Module 02 explains, an Identity Created payload can include an attribute configured in the identity profile while that particular value is null or otherwise unusable for the step you want to run. Not everyone has a manager, and an external response can also omit a field. So a workflow should validate the values it depends on rather than assuming that presence in the payload means the value is ready for use.

It helps to separate three states that look alike and behave differently. A field can be present but null, as when `manager` is in the data with a value of null. It can be present but empty, as when `department` is an empty string. Or it can be absent entirely, when the key is not in the payload at all. The Verify Data Type operator tells missing apart from null directly, but an empty string is neither missing nor null, so catching that case may still need a string comparison against the empty value. Knowing which of the three you are dealing with decides which guard you reach for.

The defenses are simple. Verify important values before you rely on them. The Verify Data Type operator from Module 03 can confirm that a value exists or is the type you expect. Branch on absence instead of letting a blank continue into an email or an action. Provide a fallback when the business process has a sensible one. If you need information that the trigger did not provide, or you need to read current identity data, fetch it deliberately rather than guessing.

Picture the manager notification. You want to email Priya's manager, but some identities have no manager. The dependable design fetches the required identity data, verifies that the manager value exists, and only then sends. If the manager is missing, take a deliberate alternate path rather than sending into a void.

## Before you move on

Use Priya's data to prove you can reason about paths rather than copy them. Given her mover `changes` array, what does `$.trigger.changes[0].newValue` mean, and why would a careful engineer be nervous about relying on item zero? Where would you use a Jayway trigger-filter predicate, and which JSONPath implementation is documented for actions and operators after the workflow starts? If a welcome email needs Priya's first name, what inline variable would you use? And if some employees have no manager attribute, which operator can help you verify the data before sending? If those come without strain, you can handle workflow data with confidence, and you are ready for Module 07.

---
[← Previous: Module 05 Forms and Interactive Workflows](05-forms-and-interactive-workflows.md) | [Course home](../README.md) | [Next: Module 07 Testing, Debugging, and Execution →](07-testing-debugging-and-execution.md)
