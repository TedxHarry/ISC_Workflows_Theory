# Module 03: Operators and Logic

How a workflow makes decisions and shapes its data.

If actions are the verbs of a workflow, operators are the thinking. An operator never sends an email or opens a ticket. Instead it does one of two quiet but essential jobs: it makes a decision, or it shapes a piece of data. A third kind, the loop, lets the workflow repeat a job over a list. Get comfortable with these three ideas, deciding, shaping, and repeating, and you can build logic of real depth without ever leaving the safety of the no-code builder.

We will keep following Priya, and this time her move to Finance does most of the teaching.

## Making a decision, and what "branching" really means

Back in Module 02, the mover trigger handed us a `changes` array telling us Priya's department went from Sales to Finance. Suppose Acme only wants a mover alert when someone moves into Finance specifically, not for every department change. That is a decision, and decisions are what comparison operators are for.

A comparison operator does one simple thing. It looks at two values, asks one yes-or-no question about them, and then sends the workflow down one of two paths depending on the answer. That is the whole mechanism, and it is also the answer to a question beginners always ask: how does a workflow branch? It branches right here. When you drop a comparison operator onto the canvas, it gives you two outcomes to wire up, the path to take when the answer is yes and the path to take when the answer is no. You connect a different next step to each. The path where the department equals Finance goes on to send the alert. The other path goes straight to a quiet ending. Branching is not a separate feature you turn on. It is just what a comparison operator does.

So to alert only for Finance, you use a Compare Strings operator. Value one is the new department. Value two is the text Finance. The operator is Equals. When Priya moves to Finance, the answer is yes and the workflow continues to the alert. When someone moves to Marketing, the answer is no and the workflow ends without bothering anyone.

## Comparing the right kind of value

There are four comparison operators, one for each kind of value, and choosing the one that matches your data is more important than it first appears.

Compare Strings is for text. It is the one you will use most. Beyond Equals and Does Not Equal, it offers genuinely useful tests: Contains and Does Not Contain, Starts With and Ends With, and Matches for pattern checks. So "does the job title contain the word Manager" or "does the email end with acme.com" are single-operator questions.

Compare Numbers is for numeric values, and it gives you the comparisons you expect: Equals, greater than, less than, and the "or equal to" versions of each. Use it when the value is genuinely a number, such as a count or a score.

Compare Boolean is for true and false values, and it is deliberately simple. It only offers Equals, because there is nothing else sensible to ask of a true-or-false value.

Compare Timestamps is for points in time, and it is more capable than people expect. It can compare two timestamps directly using Is Before, Is After, and their on-or-before and on-or-after variants, and it understands the ISO 8601 timestamp format that ISC uses. It can also compare against a number of days, which is where it becomes powerful. Questions like "was this account last used more than ninety days ago" are exactly what the day-based options such as Is Before X Days Ago are built for. Any time your logic involves "how long since," reach for Compare Timestamps rather than trying to do date math by hand.

Now the failure that catches everyone, and it is worth a real pause. Compare Strings Equals is exact, and exact means case matters. Real systems are inconsistent about case. One source stores a department as "Finance," another stores the same department as "finance," and SailPoint's own trigger documentation shows department values in lowercase. So if Priya's data holds "Finance" with a capital F but your comparison tests against "finance" in lowercase, the answer is no, every time, and your Finance alert silently never fires. The values look equal to a human and are not equal to the operator. When a comparison "should match but does not," suspect case and stray spaces first. This single instinct will save you more debugging time than any other in this module. It is also why the Trim operation, which we will meet in a moment, exists.

A close cousin of this bug is comparing the wrong data type. If a value arrives as the text "5" and you compare it with Compare Numbers, or a real number 5 compared as a string, the result can surprise you. Match the operator to what the data actually is, not to what it looks like on screen.

## Combining conditions with Define Comparison

One question is often not enough. Acme really wants the alert only when two things are true together: the department actually changed to Finance, and Priya is still an active identity. A single comparison cannot ask two questions. Define Comparison can.

Define Comparison lets you build a bigger condition out of several smaller ones, joined with And and Or. You add each condition, the same string, number, boolean, and timestamp comparisons you already know, and you say whether they combine with And, meaning all must be true, or Or, meaning any can be true. You can group conditions together to control how they combine, and each group relates to the others with And. There is also a Not toggle, which flips a condition, so you can express "and the state is not terminated" without hunting for an opposite operator.

For Priya, the condition becomes readable almost like a sentence: the new department equals Finance, and the lifecycle state equals active. Both true, the alert goes out. Either one false, it does not. Reading which attribute changed out of that `changes` array is its own small skill that we save for Module 06, so here just picture the combined condition and trust that the pieces snap together the way the words do.

Reach for a single comparison when you have one question. Reach for Define Comparison the moment you catch yourself saying "and also" or "unless."

## Shaping data with variables

The other half of an operator's job is shaping data. Often the values handed to you by a trigger are not in the form you want to use. Priya arrives as a first name and a last name in separate fields, but the alert reads better as "Patel, Priya." That reshaping is what Define Variable is for.

Define Variable builds a new value by running a short sequence of small operations, one after another. The operations come in three families. String operations include Concatenate to join pieces, Substring to take part of a value, Trim to strip stray spaces, Replace to swap text, and Get Index to find a position. Date operations let you Add Time, Subtract Time, and reformat a date with the Date Formatter. Number operations cover Add, Subtract, Multiply, Divide, and Modulo. You can chain up to fifty of these operations in one variable, and they run in order, each working on the result of the last, so you can go from raw fields to a polished value step by step. There is a basic editor where you drag operations together and watch a live preview, and an advanced editor for when you would rather work in JSON.

Make this concrete with Priya. To turn her separate fields into the display value "Patel, Priya," you chain three operations. Concatenate her last name with the text ", " (a comma and a space), then concatenate her first name onto the end of that, then Trim to clean up any stray spaces. Three small steps, run in order, take "Priya" and "Patel" and hand back "Patel, Priya," ready to drop into an email subject or a ticket title. That is the whole idea of Define Variable: a raw value goes in one end, a short chain of operations reshapes it, and a tidy value comes out the other.

One small but useful detail to file away: the result of a Define Variable is text, unless the very last operation is Get Index, in which case it hands back a number. Knowing that saves you a puzzling moment later when a value you expected to compare as a number behaves like a string.

Its partner, Update Variable, changes a variable you already created, using the same set of operations. Scope is the thing to remember with it. Outside a loop, it can see the variables made earlier in the workflow. Inside a loop, it sees only the variables belonging to that same loop pass. That scoping is not a quirk to fight, it is what keeps each pass of a loop from trampling another, and it will make sense the moment we get to loops next.

A quick word to prevent a common mix-up. These variable operations are sometimes called transforms, and they are small transformations, but they are not the same thing as the ISC attribute transforms we placed on the map back in Module 00. Those shape identity attributes as an identity is built. These shape a value inside a running workflow. Same spirit, different place, different tool. Module 09 draws that line sharply.

## Repeating work with loops

So far everything happens once. But real tasks often mean "do this for each of them." Imagine Acme wants to notify every member of the Finance team that Priya has joined. You are not holding one identity now, you are holding a list, and to act on a list you loop.

A loop takes an array from an earlier step and runs the same steps once for each item in it. Inside the loop, you reach the current item through a special reference, `$.loop.loopInput`, so `$.loop.loopInput.id` is the id of whichever item this pass is working on. If the loop needs some extra shared value from outside, you pass it in as context and read it at `$.loop.context`. There are two kinds of loop, and choosing between them is a real design decision, not a coin flip.

The parallel loop runs every item at the same time. All of them kick off together, in no guaranteed order, and the workflow waits for the whole set to finish before it moves on. Its best quality is resilience: if one item fails, the others still complete, and at the end you get back a tidy split of which items succeeded and which failed, in `successfulItems` and `failureItems`. A parallel loop can handle up to two hundred and fifty items. Reach for it when the items are independent of each other and you want the work done quickly and one bad item not to sink the rest. Notifying fifty Finance team members is a perfect fit, because none of those messages depends on another and order does not matter.

The serial loop runs the items one at a time, in order, each pass finishing before the next begins. It handles a larger list, up to a thousand items, and it comes in two shapes: a For loop that runs once per item in the array, and a While loop that keeps going as long as a condition you set stays true. The serial loop behaves differently on failure, and this is the key contrast: if one pass fails, the loop stops and does not process the rest. Reach for a serial loop when order matters, when each pass depends on the result of the one before it, or when a failure partway through means you genuinely should stop rather than plow ahead. If you ever need to leave a serial loop early once some condition is met, the Break Loop step is how you step out.

So the choice in one breath: parallel for independent work you want fast and fault-tolerant, serial for ordered or dependent work where stopping on failure is the safer behavior.

Loops are also where performance stops being abstract, so let me plant a flag you will see again in Modules 08 and 11. Loop iterations count toward an individual workflow's execution total. SailPoint warns the workflow owner when a workflow reaches 200,000 total executions, including loop executions, and blocks remaining executions when it reaches 300,000. The tenant-wide daily rate limit is separate: it is around 400,000 executions and does not count loop executions; after that threshold, executions continue at 5 per second for the rest of the day. A loop over a handful of people is nothing. A loop over thousands, especially one that calls another system on every pass, can drive one workflow toward its own execution limit very quickly. The item caps, two hundred and fifty and one thousand, are not just trivia. They are a strong signal that workflows are not the right tool for truly bulk processing. When a list is that big, rethink the approach, which is a conversation we have properly in Module 09. And a small testing note: when you test a serial loop, the builder runs only the first fifty iterations, so a passing test does not prove the full-size run behaves, a point we return to in Module 07.

One more loop gotcha worth seeing now. The parallel loop makes no promise about order. If you have quietly assumed the first item finishes first, and you built later logic on that assumption, it will bite you intermittently, which is the worst kind of bug because it passes most of the time. If order matters at all, that is your sign to use a serial loop instead.

## Guarding your data with Verify Data Type

Remember the empty-path problem from Module 01, where a step reads a field that is not there and quietly gets nothing. Verify Data Type is the seatbelt for exactly that. It checks a value before you rely on it, and it can confirm several things: that the value exists at all, or that it is specifically a string, a number, a boolean, a timestamp, or null. Put one in front of a step that would break on missing or wrong-shaped data, and you turn a silent, confusing failure into a clean, deliberate branch. It is a small habit that separates workflows that limp along from workflows you can trust.

## Success, Failure, and controlling the outcome

Every path through a workflow has to end, and it ends at one of two steps: Success or Failure. These are not just full stops. They are how the workflow reports what happened, and you get to decide which one a given branch lands on.

Success says this run finished the way it was meant to. It carries no special fields, it simply marks the run as good.

Failure marks the run as failed, and it lets you say why. It asks for a Failure Name and lets you add Failure Details, and both show up later in the execution history you will read in Module 07. This is more useful than it sounds, because ending a branch in Failure on purpose is how you tell the world "this outcome should be treated as a problem." If a workflow tried to open a ticket and could not, routing that branch to a Failure with a clear name turns an invisible non-event into a red flag someone can find and act on. So think of Success and Failure not as leftover plumbing but as the workflow's way of speaking, and choose the one that tells the truth about what happened.

## Before you move on

Design the Finance mover alert in your head, using only what this module gave you. What comparison operator asks whether the new department is Finance, and what is the one detail about the compared text most likely to make it silently fail? How would you extend that single question into "moved to Finance and still active" using Define Comparison? If Acme then wanted to message all fifty Finance team members, which loop would you choose and why, and which loop would you have chosen instead if each message somehow depended on the one before it? And if a run tried to notify people but the team list came back empty, which operator would you place up front to catch that cleanly, and would you end that branch in Success or in Failure? If those answers come without much strain, you can make a workflow think, and you are ready for Module 04, where we finally give it things to do.

---
[← Previous: Module 02 Triggers](02-triggers.md) | [Course home](../README.md) | [Next: Module 04 Actions →](04-actions.md)
