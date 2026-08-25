# Module 04.1: Decisions, Guards & Variables

How a running Workflow makes decisions, guards assumptions, shapes data, and repeats work deliberately.

Module 03 ended with a boundary worth keeping clear:

```text
PRE-START
Should this event qualify?
→ trigger / filter

POST-START
The event qualified.
The Workflow is running.
What should this execution do?
→ operator logic
```

That second question is ours now.

Operators are the steps that let a running Workflow reason about the data it already has. They can compare values, route execution, combine conditions, validate assumptions, shape values, and repeat logic over a collection.

They do not replace actions. We will give the Workflow things to *do* in Module 05.

For this module, stay inside the decision problem.

Priya's move gives us a useful example, but the requirement has changed slightly from Module 03.

Acme does **not** want only Finance moves to start the Workflow.

It wants one Workflow for qualifying department moves, and after each run starts it wants different paths for:

- Finance;
- Marketing;
- other departments.

That distinction is the reason operator logic belongs here.

> **Common Assumption:** “If I can test Finance with a filter, I should always do it there.”
>
> A filter is correct when nonmatching events should never start the Workflow. In this requirement, Marketing and other department moves still need to enter the Workflow because the running execution must make a routing decision. The event should start first; the operator decides what happens next.

Before naming any operator, use this sequence:

```text
1. What value am I actually testing?
2. Is that value present in the form I expect?
3. What type is it?
4. What business question am I asking?
5. What should each answer cause?
```

That is the decision-making habit for this module.

---

## 1. Ask one question: a single comparison

Start with the smallest useful decision.

Priya's Identity Attributes Changed data can include several objects in its `changes` array. Module 02 already taught you not to assume that the department change is `changes[0]`. Select by meaning, not position.

Once you have identified the department change, its `newValue` in our representative example is the string:

```text
Finance
```

Now state the business question in plain English:

> Is the new department Finance?

That is one yes-or-no question.

For a string value, the natural comparison family is **Compare Strings**.

Conceptually:

```text
actual new department
        ↓
Compare Strings
Equals "Finance"
     ↙       ↘
   true      false
```

Do not begin by browsing the operator menu and asking which feature looks useful.

Begin with the value and the question.

### Match the comparison to the actual data type

ISC currently provides native comparison families for:

- **Compare Strings**
- **Compare Numbers**
- **Compare Boolean**
- **Compare Timestamps**

The family should match the data you actually have.

Examples:

```text
"Finance"
→ string
→ Compare Strings
```

```text
7
→ integer count
→ Compare Numbers
```

```text
true
→ boolean
→ Compare Boolean
```

```text
a supported date/time value
→ timestamp
→ Compare Timestamps
```

The exact menu of comparison options can change. You do not need to memorize it.

What you should remember is:

```text
actual type
→ business question
→ appropriate comparison family
```

### Values that look alike may not be the same type

Suppose a count appears on screen as:

```text
"5"
```

with quotation marks in the JSON.

That is a string.

This is different from:

```text
5
```

which is a number.

For Core number examples in this course, we will use actual integers such as counts. Do not build logic on an assumption that ISC will silently convert a string-looking number into an integer for you.

If the type is wrong for the comparison you want, treat that as a data problem to understand, not as permission to hope for coercion.

### Do not guess string comparison behavior

Source systems are not always tidy about text.

You may encounter:

```text
"Finance"
"finance"
" Finance"
"Finance "
```

Do not assume a universal case-normalization rule that the current documentation does not guarantee.

If a string comparison behaves differently than you expect, inspect the rendered runtime values before rewriting the logic.

Ask:

- What string did the Workflow actually receive?
- Is there leading or trailing whitespace?
- Is the casing consistent?
- Am I using a comparison mode that is actually supported in this operator?

The documented `Trim` variable operation can remove leading and trailing whitespace when that is the actual problem.

It is not a general case-normalization feature.

> **Engineering Habit:** When a comparison “should match” but does not, inspect the two runtime values and their types before changing the operator.

---

## 2. Turn the answer into a branch

A comparison is useful because its answer changes what happens next.

This is what branching means in a Workflow.

You do not enable a separate branching mode.

The comparison asks a question and provides different paths for the result.

For Acme:

```text
new department == Finance?
          ↓
      true / false
       ↙       ↘
 Finance      not Finance
   path          path
```

The true path may continue through Finance-specific logic.

The false path can ask a second question:

```text
new department == Marketing?
          ↓
      true / false
       ↙       ↘
Marketing     other
  path        path
```

That is a perfectly reasonable design when the requirement is a small routing tree.

Notice the difference from Module 03.

Module 03 asked:

> Should this event start at all?

Module 04 asks:

> It started. Which path should this execution take?

Those are different design decisions even when they inspect the same business value.

### Ask one question per simple comparison

A simple comparison is easiest to understand when it expresses one business question.

Good:

> Is the new department Finance?

Also good:

> Is this integer count greater than 10?

Also good:

> Is this boolean value true?

The moment your sentence becomes:

> “Finance **and** something else…”

you have moved beyond one simple condition.

That is the next problem.

---

## 3. Combine conditions deliberately

Suppose Acme does not merely care that Priya's new department is Finance.

For a particular internal route, it wants to know whether she moved specifically:

```text
Sales
→
Finance
```

Now there are two conditions:

```text
old department == Sales

AND

new department == Finance
```

You could create a maze of separate comparisons.

For a small sequence, that can be understandable.

But when several conditions represent one business rule, **Define Comparison** gives you a more deliberate way to express the rule.

Current Define Comparison supports condition families including:

- Boolean;
- Number;
- String;
- Timestamp;
- Verify Data Type.

It can combine supported criteria with logical relationships such as AND and OR, and it can express exclusions with NOT.

For our Core example, the reasoning is enough:

```text
old department equals Sales
AND
new department equals Finance
```

If both are true, take the Sales-to-Finance route.

If either is false, take the other route.

### One condition versus one business rule

Use this heuristic:

```text
one yes/no condition
→ simple comparison

several related conditions that together mean one rule
→ consider Define Comparison
```

Do not turn that into:

> “Define Comparison contains every option from every standalone comparison.”

That is stronger than the current product contract.

Define Comparison can combine supported condition types, but individual sub-options can differ from the standalone operators.

The design lesson is the relationship between the conditions, not menu memorization.

### A little more structure when you need it

**Working Engineer**

Within Define Comparison, criteria can be grouped with AND or OR behavior. Additional groups have AND relationships, and NOT can invert a configured condition.

That gives you room for rules such as:

```text
A AND B
```

or:

```text
(A OR B) AND C
```

Do not make the grouping syntax the first thing you think about.

Write the business rule in plain language first.

If you cannot explain the condition clearly without the builder, the builder will not make it clearer for you.

---

## 4. Guard data before depending on it

So far we have assumed that the value we want to compare is present and has the expected type.

That assumption deserves its own check.

Module 02 established this distinction:

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

Module 04 adds the engineering consequence:

> If later logic depends on a data assumption, validate the assumption before building more logic on top of it.

**Verify Data Type** is one operator that helps with this.

Current documented checks include whether a selected value:

- exists;
- is Boolean;
- is Number;
- is String;
- is Timestamp;
- is Null.

Suppose your next step is Compare Strings against Priya's new department.

Before depending on that comparison, you may decide to verify that the selected value is a string.

Conceptually:

```text
selected new department
        ↓
Verify Data Type
      String?
     ↙      ↘
   yes       no
    ↓         ↓
compare     alternate path
```

Now the comparison is not quietly carrying an unstated type assumption.

### A guard proves only what it checks

This distinction matters:

```text
exists
≠
non-empty
≠
usable for my business rule
```

If an empty array exists, an existence check can still be true.

If an empty string is a string, a string-type check can still be true.

Verify Data Type is not a generic “this data is good” operator, and it is not a documented non-empty-array test.

Be precise about the fact you are validating.

If your requirement is:

> “This value must exist.”

validate existence.

If it is:

> “This value must be a string.”

validate the string type.

If it is:

> “This collection must contain at least one item.”

do not pretend a different check proves that requirement.

That separation is exactly the same engineering discipline you used in Module 02 when distinguishing missing, null, and empty values.

### Guards can be part of a larger condition

**Working Engineer**

Define Comparison can incorporate Verify Data Type conditions.

That means a more mature design can combine:

```text
value is a String
AND
value equals the expected business value
```

when the supported options fit the requirement.

You do not need to force every guard into its own separate node.

The point is still the same:

> Make the data assumption explicit before trusting it.

---

## 5. Shape data with variables

Sometimes the data is correct but not yet in the form you want for later logic.

That is where Workflow variables help.

The Variable Selector from Module 02 and Define Variable solve different problems.

```text
Variable Selector
→ reference data that is already available

Define Variable
→ create a new value by applying supported operations
```

A variable is useful when you want to prepare a value once and use the prepared result later.

### Define Variable: small operations in sequence

**Define Variable** applies operations one after another.

Think:

```text
input value
   ↓
operation
   ↓
operation
   ↓
derived value
```

You do not need the entire operation catalog in your head.

Current operations include string, date, and number shaping. When you need a specific transformation, verify the current supported operation.

For the teaching model, one safe string example is enough.

Suppose Priya's selected department value is:

```text
" Finance "
```

and Acme wants a small internal label such as:

```text
Finance move
```

A variable can conceptually do this:

```text
" Finance "
     ↓
Trim
     ↓
"Finance"
     ↓
Concatenate Strings
with static text " move"
     ↓
"Finance move"
```

Two small operations created a value that later steps can reuse.

The order matters because each operation works on the result produced by the previous one.

### Keep Concatenate Strings within its documented boundary

Current central Workflow documentation describes **Concatenate Strings** as adding a **static string** to the working value.

That is why the example above adds the static text:

```text
" move"
```

to Priya's dynamic department value.

Do not build your Core mental model around:

```text
dynamic first name
+
dynamic last name
```

as though Concatenate Strings universally guarantees dynamic-to-dynamic concatenation.

When product documentation gives you a narrow contract, teach and design to that contract.

### Update Variable changes an existing Workflow variable

**Update Variable** lets a Workflow operate on a variable that already exists.

For Core understanding, hold onto only this:

```text
Define Variable
→ create a derived Workflow value

Update Variable
→ change an existing eligible Workflow variable
```

The current documented selector scope is narrower than a generic programming-language idea of mutable state.

Outside loops, the selector exposes upstream variables defined outside loops.

Inside a loop, the selector exposes variables defined within that loop.

That is the documented selection rule.

Do not turn it into guarantees about:

- cross-iteration mutation;
- one iteration seeing another iteration's updates;
- a value updated inside Serial Loop reliably persisting after the loop.

Those behaviors are not established strongly enough to teach as a universal state model.

We will return to loop scope in the Engineering Step-Up.

### Workflow variables are not identity-attribute transforms

The language can sound similar because both concepts reshape values.

They live in different places.

```text
ISC identity-attribute transform
→ calculates/shapes identity attribute values
  as part of identity data processing

Workflow variable operation
→ shapes a value inside a running Workflow
```

Do not choose between them because the names sound similar.

Choose based on which ISC capability actually owns the requirement.

Module 09 will make that architectural choice explicit.

---
