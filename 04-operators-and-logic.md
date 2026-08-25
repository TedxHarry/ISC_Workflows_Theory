# Module 04: Operators & Logic

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
Finance
finance
 Finance
Finance 
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

## Engineering Step-Up: Loops

Everything so far can be reasoned about one value or one decision at a time.

Loops change the engineering problem.

A loop is not merely:

> “do this several times.”

The moment you repeat work over a collection, new questions appear:

- Does order matter?
- Are iterations independent?
- What data belongs to one iteration?
- Can several iterations be active at once?
- What happens when one iteration fails?
- How much work does the collection multiply into?

That is why loops are an Engineering Step-Up rather than just another operator to memorize.

---

## 6. An array does not automatically mean “use a loop”

Module 02 taught you arrays.

It also taught you predicates.

Those are related to loops, but they solve different problems.

Suppose Priya's event contains several entries in `changes`.

If your business question is only:

> Which change object represents department?

then a selection by meaning is often the better idea.

You do not need to loop over every change merely because the data is an array.

Use a loop when the requirement really is:

> Apply the same body of work to each relevant item in this collection.

That distinction prevents a lot of unnecessary complexity.

```text
Need one matching item or subset?
→ selection may be enough

Need repeated processing for each item?
→ consider a loop
```

### A simple collection example

Imagine Acme has a requirement to classify each changed attribute in Priya's `changes` collection.

Each change object should go through the same small body of logic:

```text
change item 1
→ classification logic

change item 2
→ same classification logic

change item 3
→ same classification logic
```

Now repetition is real.

The next question is not yet:

> Which loop button do I click?

Ask:

> Are those iterations independent, or does one depend on another?

That decides the design.

---

## 7. Regular Loop: parallel and unordered

The native **Loop** operator processes its items in parallel.

The stable design facts to remember are:

- iterations are processed in parallel;
- processing order is not guaranteed;
- failure of one iteration does not prevent the sibling iterations from running to completion;
- the Workflow waits for the Loop to finish before continuing after it;
- successful and failed iteration results are exposed separately.

Do not strengthen “parallel” into:

> “Every iteration starts at the exact same instant.”

That is not the contract you need.

The useful invariant is:

> The work is parallel, and order is not guaranteed.

### When regular Loop fits

Regular Loop is a natural candidate when:

- items are independent;
- order does not matter;
- one item's processing does not require the previous item's result.

If Acme's classification of one change object has no dependency on how another change object is classified, parallel processing may fit.

### Parallel does not mean “failure no longer matters”

The old module called this behavior fault-tolerant.

That is too broad.

A more accurate statement is:

> One iteration failing does not stop the other iterations from running to completion.

That still leaves you with a design question afterward:

> Did any iteration fail, and does the business process care?

A Loop boundary completing is not proof that every repeated business outcome succeeded.

That is the same discipline behind **Green Does Not Mean Done**:

> know exactly what boundary was proven.

Full failure handling belongs later, but partial-failure awareness belongs here because it affects whether the loop design makes sense.

---

## 8. Serial Loop: sequential when dependency matters

The native **Serial Loop** processes iterations sequentially.

One iteration runs, then the next.

That makes it the better fit when:

- order matters;
- an iteration depends on what happened before it;
- continuing after an iteration failure would be unsafe for the requirement.

Current documented behavior also makes the failure contrast important:

- regular Loop lets sibling iterations continue when one iteration fails;
- Serial Loop stops further iterations after an iteration fails.

That is not just a runtime detail.

It changes the business meaning of choosing one loop or the other.

Conceptually:

```text
Independent + order-insensitive
→ regular Loop may fit

Ordered or dependent
→ Serial Loop may fit
```

### For and While

**Working Engineer**

Serial Loop supports For Loop and While Loop forms.

A For-style loop is collection-oriented.

A While-style loop continues according to its configured condition.

Serial Loop also supports **Break Loop** when the design needs to exit early.

You do not need those mechanics to understand the Core choice.

First learn to recognize dependency and ordering.

---

## 9. Current item, context, and scope

A loop body needs a way to reason about the item being processed in that iteration.

The concept is simple:

```text
collection
   ↓
loop
   ↓
current item for this iteration
```

Do not make the first loop lesson a JSONPath memorization exercise.

Use the current builder, Variable Selector where applicable, and actual runtime data to identify the current-item reference.

### Regular Loop Context is not a universal loop feature

**Working Engineer**

The regular **Loop** operator has a documented **Context** mechanism for carrying additional outside data into its iterations.

Do not generalize that into:

> “All loop types have the same Context contract.”

Serial Loop does not expose the same regular-Loop Context contract.

Treat the two operators as related but distinct runtime models.

### Do not memorize an exact Serial Loop current-item path here

Current official SailPoint sources have not been perfectly consistent about the exact Serial Loop current-item JSONPath.

That makes the engineering lesson straightforward:

> Learn the current-item concept. When an exact path matters, use the current builder/documentation and inspect the actual data rather than relying on a memorized string from an older example.

For the regular Loop, current documentation is more settled.

For Serial Loop, Core Module 04 deliberately does not turn a disputed implementation detail into required memory.

### Update Variable inside loops: stay with the documented scope rule

The selector scope you learned earlier still applies.

Inside a loop, Update Variable exposes variables defined within that loop.

That tells you what the product currently allows you to select.

It does **not** prove a universal state-persistence model across iterations or after Serial Loop.

If a production design depends on mutated state surviving a loop boundary in a particular way, verify that behavior explicitly rather than deriving it from the selector.

---

## 10. Why loops change the engineering problem

The loop body can look simple while the overall design becomes much larger.

Suppose a Workflow repeats one small unit of work for every item in a collection.

The collection size multiplies the work.

Conceptually:

```text
1 unit of work
×
number of items
=
repeated Workflow work
```

That is why a loop choice should always trigger a few extra questions.

### Does order matter?

If yes, a parallel Loop is already suspicious.

### Are items independent?

If one iteration needs the previous one's result, Serial Loop is the more natural model.

### What happens if one item fails?

With regular Loop, sibling iterations continue.

With Serial Loop, later iterations stop after an iteration failure.

That difference should be part of the design, not a surprise discovered after deployment.

### How much work can this multiply into?

Loops have current product limits and execution-accounting consequences.

You do **not** need the numeric thresholds in your head for Module 04.

Remember the principle:

> **Loops multiply work. Scale is part of the design.**

Module 08 owns current operational limits and execution accounting.

### Does a Workflow still make sense at this scale?

A loop is not permission to turn Workflow into a general bulk-processing engine.

That architecture decision belongs in Module 09.

For now, keep one warning:

> If the collection is large enough that scale dominates the design, stop treating “which loop?” as the only question.

### What happens when executions overlap or repeat?

Concurrency, replay, duplicate side effects, and idempotency become especially important when repeated work can overlap.

You only need to recognize those concerns here.

Modules 08 and 11 will teach the operational and failure-mode consequences.

### How will I test it?

Loop testing has its own current product constraints.

Module 07 owns those mechanics.

Do not mix a builder test limit into the first lesson on choosing a loop.

---

## 11. A compact operator decision method

At this point, the operator menu should matter less than the reasoning.

When a Workflow has already started, walk through this order:

```text
1. Identify the value.
   What data am I actually reasoning about?

2. Validate the assumption.
   Is it present, and is the type what later logic requires?

3. State the business question.
   One condition or several?

4. Route the answer.
   What should each result cause?

5. Shape only if needed.
   Do I need a derived value for later use?

6. Ask whether repetition is real.
   Am I selecting from a collection,
   or processing every item?

7. If looping, identify dependency.
   Independent/order-insensitive → regular Loop may fit.
   Ordered/dependent → Serial Loop may fit.
```

That method will survive product-menu changes better than memorizing a list of operators.

---

## Work It Out: design the logic before naming the operator

Acme changes its mover requirement.

Every qualifying **department-change** event should start the Workflow.

After it starts:

- moves into Finance should take the Finance path;
- moves into Marketing should take the Marketing path;
- other department moves may take another path;
- the new department is expected to be a string;
- Acme wants a reusable internal label based on the new department plus the static text `" move"`;
- separately, Acme is considering a future rule that performs the same classification logic for every change object in the `changes` array.

Before looking at operator names, answer these.

1. Is the Finance decision primarily a trigger-filter decision or an in-Workflow decision?
2. What value should the first comparison test?
3. What assumption would you consider guarding before Compare Strings?
4. If Acme later wants “Sales to Finance” as one rule, is that one condition or a combined condition?
5. Can Define Variable safely create the label from a dynamic department value plus static text?
6. Does the existence of the `changes` array automatically mean the Workflow needs a loop?
7. If every change object really must be processed and the items are independent, which loop model is the natural first candidate?
8. If each iteration depends on the one before it, which model is the natural first candidate?
9. Does Verify Data Type proving a collection exists prove that it contains at least one item?

<details>
<summary>Check your reasoning</summary>

**1. In-Workflow decision.**  
All qualifying department-change events are supposed to start. Finance versus Marketing versus other is therefore a post-start routing decision.

**2. The actual new department value.**  
Use the relevant department change's `newValue`, selected by meaning rather than assuming a fixed array position.

**3. The expected type.**  
If later logic depends on a string comparison, verifying that the selected value is a string can make that assumption explicit. Depending on the requirement, existence may also matter, but existence and string type are different checks.

**4. Combined condition.**  
“Old department is Sales AND new department is Finance” contains two related conditions. Define Comparison is a natural operator to evaluate for that rule.

**5. Yes, within the current documented concatenation boundary.**  
Start from the dynamic department value and concatenate the static string `" move"`. Do not generalize that into a guarantee that two independently dynamic fields can always be concatenated by this operation.

**6. No.**  
If the requirement only needs the department change, a predicate/selection may be enough. A loop is justified when the same body of work must run for each relevant item.

**7. Regular Loop.**  
Independent, order-insensitive iterations are the natural case for parallel Loop.

**8. Serial Loop.**  
When dependency or order matters, sequential processing is the safer model.

**9. No.**

```text
exists
≠
non-empty
≠
usable
```

Verify Data Type does not document a non-empty-array check.

</details>

---

## Checkpoint

You should now be able to take a Workflow that has already started and sketch its decision logic in this order:

```text
What value am I using?
        ↓
Is the data assumption valid?
        ↓
What type is it?
        ↓
What business condition am I asking?
        ↓
Which path follows each answer?
        ↓
Do several conditions form one rule?
        ↓
Do I need to shape a value?
        ↓
Do I really need repetition?
        ↓
If I loop, does order or dependency matter?
```

You should also be able to explain:

- why a trigger filter and a post-start comparison solve different problems;
- why comparison family should follow actual runtime type;
- why you should not assume string case normalization or implicit type coercion;
- why Define Comparison is for supported combined conditions rather than an assumed copy of every standalone comparison option;
- why `exists` does not mean `non-empty` or `usable`;
- why Verify Data Type is a narrow guard, not a universal data-quality verdict;
- why Define Variable should follow the current operation contract, including static text for Concatenate Strings;
- why Update Variable selector scope does not prove a broad loop-mutation model;
- why an array does not automatically require a loop;
- why regular Loop is parallel and unordered;
- why Serial Loop is sequential and appropriate when order or dependency matters;
- why regular Loop Context should not be generalized to Serial Loop;
- why exact Serial Loop current-item syntax is something to verify when needed rather than memorize here;
- why loops introduce scale and partial-failure questions even before you learn full operations and failure handling.

The Workflow can now decide what path it wants.

Module 05 asks the next question:

> **What happens when that path needs the Workflow to act, and what should the design do when an action does not go as planned?**

That is where Actions & Error Handling begins.

---

## Official References

- [Workflow Operators - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-operators.html)
- [Managing Workflows - SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-manage.html)
- [Serial Loop rollout discussion - SailPoint Developer Community](https://developer.sailpoint.com/discuss/t/new-capability-workflows-with-1k-serial-loops/207478)

---

[← Previous: Module 03 Triggers & Filters](03-triggers.md) | [Course home](README.md) | [Next: Module 05 Actions & Error Handling →](05-actions.md)
