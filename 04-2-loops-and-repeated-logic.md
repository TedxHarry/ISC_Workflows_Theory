# Module 04.2: Loops & Repeated Logic

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

**1. In-Workflow decision.**<br>
All qualifying department-change events are supposed to start. Finance versus Marketing versus other is therefore a post-start routing decision.

**2. The actual new department value.**<br>
Use the relevant department change's `newValue`, selected by meaning rather than assuming a fixed array position.

**3. The expected type.**<br>
If later logic depends on a string comparison, verifying that the selected value is a string can make that assumption explicit. Depending on the requirement, existence may also matter, but existence and string type are different checks.

**4. Combined condition.**<br>
“Old department is Sales AND new department is Finance” contains two related conditions. Define Comparison is a natural operator to evaluate for that rule.

**5. Yes, within the current documented concatenation boundary.**<br>
Start from the dynamic department value and concatenate the static string `" move"`. Do not generalize that into a guarantee that two independently dynamic fields can always be concatenated by this operation.

**6. No.**<br>
If the requirement only needs the department change, a predicate/selection may be enough. A loop is justified when the same body of work must run for each relevant item.

**7. Regular Loop.**<br>
Independent, order-insensitive iterations are the natural case for parallel Loop.

**8. Serial Loop.**<br>
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

[← Previous: Module 03.2: Filters & Specialized Triggers](03-2-filters-and-specialized-triggers.md) | [Course home](README.md) | [Next: Module 05.1: Action Contracts & Core Actions →](05-1-action-contracts-and-core-actions.md)
