# Module 06: Data, Variables, and Expressions

Working with the JSON payload, and pointing at any piece of it with confidence.

Every module so far has leaned on JSONPath and quietly promised that this one would explain it properly. Here we pay that off. This is the module where data handling stops being something you copy from an example and starts being something you can reason about, because reliable data handling is the real line between a workflow that works and one that fails in ways you cannot explain. We keep following Priya, because her data is the perfect teacher.

## What the workflow is really holding

Go back to the picture from Module 01. A workflow is a single JSON document that grows as it runs. The trigger drops in the first data, and every step that runs adds its own output. So at any moment, the workflow is holding one big object, and everything you reference lives somewhere inside it.

Here is the part that trips people up, and getting it straight fixes half of all JSONPath confusion. The trigger's data is not sitting at the very top of that document. It lives under a key named for the trigger step, `trigger`. Each action or operator you add lives under its own name too. So the shape of the whole thing looks like this:

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

That is why, all the way back in Module 01, Priya's email was `$.trigger.attributes.email` and not just `$.attributes.email`. The dollar sign is the very top of the whole document, `trigger` steps into the trigger's data, and from there you walk down to the field you want. Output from a later step called getManager would be `$.getManager.email`. Once you see the workflow as one growing object with each step tucked under its own name, every path you write has an obvious starting point.

And remember from Module 02 that the data under `trigger` is different for each kind of trigger. Priya's joiner carries `attributes`. Her mover carries a `changes` array. An aggregation carries `stats`. So the first thing to do for any workflow, every time, is open the trigger in the builder and read its actual JSON. Never write a path from memory of what you think a trigger provides.

## Reading a single value

The simplest path walks straight down through named keys, one dot at a time. To read Priya's login name you start at the root, step into the trigger, step into the identity object, and take the name: `$.trigger.identity.name`. To read her department: `$.trigger.attributes.department`.

The Module 01 trap is worth saying once more, because it never stops being true. Her login name is under `identity`, but her email is under `attributes`. Those are different branches of the JSON, so `$.trigger.identity.email` points at nothing, because there is no email inside the identity object. When a path returns nothing, the fix is always the same: stop guessing and read the real JSON, following the nesting key by key.

## Reading from arrays

Single values are easy. The moment your data holds a list, you need a little more, and this is exactly where Priya's mover lives. Her Identity Attributes Changed payload carries a `changes` array:

```json
{
  "changes": [
    { "attribute": "department", "oldValue": "Sales", "newValue": "Finance" }
  ]
}
```

There are three ways to reach into an array, and knowing which to use is the whole skill.

The first is by position, with an index. The first item is index zero, so `$.trigger.changes[0].newValue` reads the new value of the first change, which here is Finance. Indexing is simple, and it is also fragile, and the reason is important. More than one attribute can change at the same moment. If Priya's title and department both change, the array holds two entries, and there is no promise that department is first. So `[0]` might give you the title change on Tuesday and the department change on Wednesday, and a bug that moves around like that is the worst kind to chase. Use an index only when you truly know the array has exactly one item, or when position genuinely does not matter.

The second is the wildcard, `[*]`, which reaches every item in the array at once. You reach for this when you want to act on all of them, usually by handing the whole set to a loop.

The third is a filter, and it is the dependable answer to the fragility problem. Instead of asking for "the first change," you ask for "the change whose attribute is department," regardless of where it sits in the list. That is written with a predicate: `$.changes[?(@.attribute == "department")]`. Inside those brackets, the `@` means "the current item being tested," so this reads as "give me the items where the current item's attribute equals department." That is far safer than counting on position. Here is a real, verified example that finds a specific lifecycle change, the kind of thing a leaver workflow cares about:

```
$.changes[?(@.attribute == "cloudLifecycleState" && @.newValue == "terminated")]
```

Notice two useful things in that one. The lifecycle state attribute is really named `cloudLifecycleState`, which is exactly the sort of exact field name you confirm in the builder rather than guess. And you can combine conditions with `&&`, so you can match on both the attribute and its new value in a single expression.

## The two engines, and why the same expression can behave differently

Now the promise I made in Modules 01 and 02 comes due. I kept saying that the path in a trigger filter and the path in a step are close cousins, not identical twins. Here is why. ISC uses two different JSONPath engines in two different places.

Trigger filters use an engine called Jayway. A trigger filter runs on the raw event payload rather than on the whole workflow document, so it is rooted at the event, not under a `$.trigger` key. That is why most of the filter examples in Module 02, such as `@.status` and `$.changes[?(...)]`, reach fields that sit right at the top of the event with no `$.trigger` in front. How deeply any given field sits still varies by trigger, which is the difference Module 02 flagged, so you always confirm against that trigger's real payload rather than assuming one fixed shape.

Everything inside the workflow, the paths you use in actions and operators, uses a different engine called JSON Slice. This one runs on the whole workflow document, the big growing object, where the trigger data is under `$.trigger`. That is why step references start with `$.trigger.something`.

So the same idea gets written two different ways depending on where you are. At the trigger filter: `$.changes[?(@.attribute == "department")]`. Reading inside a step: you begin from `$.trigger.changes`. That difference in rooting is the first thing the two engines do not share.

The second difference matters more, and I want to be honest rather than tidy about it. Because they are different engines, they do not support exactly the same features, and an expression that works perfectly as a trigger filter is not guaranteed to behave the same when you paste it into a step. Predicate filters like `[?(@.attribute == "department")]` are clearly supported and documented for trigger filters. Inside a step, treat a fancy predicate as something to test, not something to trust on sight. When it does not behave, you have two clean ways out that you already know. You can filter at the trigger, so the workflow only runs for the case you care about, and then inside the workflow you no longer have to hunt through the array. Or you can loop over the array with a serial or parallel loop from Module 03 and use a comparison to find the entry you want. Both of those sidestep the question of exactly which predicates JSON Slice supports, and both tend to read more clearly anyway.

The practical rule: decide "which event do I even care about" at the trigger filter, and do your careful reading of the data inside the workflow with simple paths, indexes, and loops. That division keeps you on the well-supported parts of each engine.

## Writing paths without typing them: inline variables and the Variable Selector

You will place references in two ways. Inside a text field, such as an email body, you write an inline variable with double curly braces, a dollar sign, and a dot: `{{ $.trigger.attributes.firstname }}`. Two braces on each side, and the dollar and dot are required. If the value comes from the very same step you are configuring, you may drop the step name, so a same-step reference can be as short as `{{ $.recipientEmailList }}`.

There is one naming quirk that surprises everyone once, so let me spare you the surprise. When you name a step, ISC squishes that name into a single run-together word for use in paths, and the result can look strange. A step you called "HTTP Request" becomes `hTTPRequest`, so its body is `{{ $.hTTPRequest.Body }}`. That odd capitalization is not a typo, it is the auto-generated variable name. This is the best argument for not typing paths by hand.

Instead, use the Variable Selector. Beside a field you choose to add a variable, open the selector, pick the step whose output you want, and pick the attribute from the list. The builder writes the correct JSONPath for you, spelling the step name exactly right, weird capitalization and all. Because it reads the real data shape, it also protects you from the nesting mistakes we keep warning about. There is one rule it enforces that you should welcome: you can only select data from steps that ran earlier than the one you are working on, which is the no-forward-references rule from Module 01, now built into the tool so you cannot break it by accident.

## Missing and null data, the quiet killer

The most common workflow bug in the world is not a crash. It is a path that points at a field which is not there, quietly returning nothing, while the workflow carries on as if all is well. We met this in Module 01. Now we handle it on purpose.

Real identity data is incomplete more often than you expect. Remember from Module 02 that on a joiner some attributes may still be filling in, and plenty of identities simply lack an optional attribute. Not everyone has a manager. Not every account has an email. So you cannot assume a value is present just because it usually is.

The defenses are simple and they are the mark of a workflow you can trust. First, check before you rely. The Verify Data Type operator from Module 03 can confirm that a value exists, or that it is specifically a string or a number, before a later step depends on it. Put one in front of a step that would break on missing data, and a silent failure becomes a clean, deliberate branch you control. Second, provide a fallback. With Define Variable you can build a sensible default, so an empty field becomes "unknown" or a team address rather than a blank that quietly poisons an email. Third, branch on absence. If Priya happens to have no manager attribute, do not send a message into the void. Check for the manager first, and if it is missing, take a different path, escalate to a team, or end cleanly with a Failure that a human can see.

Picture the manager notification concretely. You want to email Priya's manager, but some identities have no manager set. The dependable design reads the manager, verifies it exists, and only then sends. If it is missing, the workflow does something sensible on purpose instead of failing by silence. That single guard is the difference between a workflow that works for the neat records and one that holds up for the messy ones, and real data is always messier than the demo.

## Before you move on

Use Priya's data to prove you can do this without a net. Given her mover `changes` array, what is the path to the new department value by position, and why would a careful engineer be nervous about relying on that position? Write the expression that finds the department change no matter where it sits in the array, and say which of the two engines that predicate form is safe in and which one you would test before trusting. If a welcome email needs Priya's first name in the body, write the inline variable exactly, braces and all. And finally, if some employees have no manager attribute, describe the two operators you would combine so the manager notification never fires into a void, and decide whether the missing-manager branch should end in Success or in Failure. If those come without strain, you can handle workflow data with real confidence, and you are ready for Module 07, where we run these workflows, watch them execute, and learn to read exactly what happened when one goes wrong.

---
[← Previous: Module 05 Forms and Interactive Workflows](05-forms-and-interactive-workflows.md) | [Course home](../README.md) | [Next: Module 07 Testing, Debugging, and Execution →](07-testing-debugging-and-execution.md)
