# Module 07: Testing, Debugging, and Execution

How to test a workflow safely, and how to read exactly what happened when one runs.

You can now build a workflow. This module is about the two skills that separate someone who builds workflows from someone who runs them in production without fear: testing without causing harm, and reading a failure calmly enough to fix it. A confident engineer is not one whose workflows never fail. Everything fails eventually. A confident engineer is one who can prove a workflow works before trusting it, and who can look at a broken run and know where to look first.

We will start with the single most important safety lesson in the whole course, because getting it wrong causes real damage to real people.

## Testing that does not hurt anyone

Here is the sentence I most want you to remember from this module. The ordinary Test Workflow button runs the workflow for real. It is not a rehearsal. When you test, the emails actually send, the accounts actually get created, the certification campaigns actually start, and the access actually changes, on live identities. SailPoint says this plainly, and warns you to use caution to avoid adding, changing, or removing access from live identities while testing.

Read that twice, because it is the opposite of what most people assume. Almost everyone expects a "test" to be a safe sandbox that pretends. In ISC, the plain test does the real thing. This is exactly how a well-meaning engineer emails five hundred people, or strips access from a real employee, while "just trying it out." So before you ever press test, you need to know how to make it safe.

There are two ways, and you will usually use both.

The first is Simulated Testing. This is the safety switch I promised you back in Module 04. Simulated testing lets you run the workflow using mock data so that the steps you choose do not actually execute. It works through an Enable Step toggle on each step. When a step is toggled on, it runs for real during the test. When it is toggled off, it uses mock data and does not actually do anything. So to test Priya's offboarding safely, you toggle the Manage Access step off, and the workflow runs through all its logic, its comparisons, its branches, its notifications, without ever really touching Priya's access. You get to watch the thinking happen while the dangerous hands stay still. This is the everyday tool for testing any workflow that changes the world.

The second is a sandbox tenant. The safest place to test is a separate, non-production tenant stocked with dummy identities, accounts, and roles created only for testing. Then even a step that runs for real touches nobody who matters. Best practice is to test in a sandbox, and to simulate the world-changing steps on top of that. Two layers of safety, because the cost of a mistake here is measured in real people.

One more practical point about testing. When you open the test panel, there is a Test Input field, and it comes pre-filled with sample data. That sample will not actually work, because its identity ids, source ids, and names do not match anything in your tenant. Real triggers hand real ids, so to test properly you replace the sample values with real ids from your own tenant, which you find with Search or the APIs. This is a small nuisance with a useful lesson buried in it: a workflow runs on ids, not on the friendly names you see on screen, and a test only means something when the input looks like what the trigger will really deliver.

## Reading what happened: the execution history

Every time a workflow runs, whether a test or a real event, it leaves a record in the execution history. This is your black box recorder, and learning to read it is most of debugging. The history is available to admins, it covers the last ninety days, and if you need to look further back than that you pull it through the Workflow Executions API.

You read a run in layers, from the outside in.

The first layer is the status. Did this run end in success or in failure. Remember from Module 03 that every path through a workflow ends at a Success or a Failure step, and that outcome is what shows here. The executions list lets you filter by status, so you can pull up just the failures across a workflow and see how often and when it is breaking. When something is wrong, this is the first thing you look at, and often it immediately tells you whether the workflow ran and failed, or never ran at all, which are two very different problems we will separate in a moment.

The second layer is the step-by-step playback. Open a single execution and you can walk through its steps one at a time. For each step, the history shows you its Step Input, its Step Output, and the configuration of the step exactly as it was when it ran. Even better, it shows the rendered value of your inline variables, meaning it shows what `{{ $.trigger.attributes.firstname }}` actually turned into when the step ran, not just the expression you wrote. This is the moment all those silent failures from earlier modules become visible. The empty JSONPath that quietly returned nothing in Module 01 is right there in front of you now, because the Step Input shows a blank where you expected a value.

Let me make that concrete. Suppose Priya's welcome email went out looking wrong, greeting her as "Welcome to Acme, " with nothing after the comma. You open the run, find the Send Email step, and look at its input. You might see something like this:

```
Step Input
  recipients: priya.patel@acme.com
  subject: Welcome to Acme
  body: Welcome to Acme, 
```

The body is cut off exactly where the first name should be. That blank is the whole diagnosis. Your path to the first name resolved to nothing, so now you go check it, and you find you wrote `$.trigger.identity.firstname` when the first name lives under attributes, so it should have been `$.trigger.attributes.firstname`. The history did not tell you the answer, but it pointed at the exact step and the exact empty value, which is most of the work.

## A field guide to failures

Most workflow failures fall into a handful of shapes, and you have already met every one of them in earlier modules as a warning. Here they are gathered into a diagnostic order, so that when something breaks you have a route to walk rather than a panic.

Start by asking the biggest question first: did the workflow run at all. If there is no execution record for an event you expected to fire, the workflow never started, and the usual culprit is the trigger filter from Module 02. A filter that returns nothing turns the event away silently, with no error and no history, because from the platform's view there was nothing to do. So when a workflow "does nothing," suspect the filter first, loosen or remove it, and test again. Also remember the plainer reasons a workflow might not fire: it may be disabled, or it may be a brand new tenant still inside the roughly two hour window before workflows become active, which we met in Module 00.

If the workflow did run but a step came up empty, you are looking at a JSONPath or missing-data problem from Modules 01 and 06. Open the failing step's input in the history and look at what actually arrived. Check the nesting, check the case, and remember the two engines, that a path is rooted differently in a trigger filter than in a step. The history shows you the real data, so you can stop guessing.

If an HTTP Request step failed, the outside system did not cooperate, which Module 04 warned you to expect. It may have returned an error, or timed out, or answered in a shape you did not plan for. When you build an error branch on that step, the failure gives you data to read, including a workflowErrorMessage and a workflowStatusCode, which tell you what went wrong on the other side. Read those rather than guessing.

If a comparison sent the workflow down the wrong path, look at the rendered values in the history, because this is almost always the case-or-type mismatch from Module 03. The history shows what the two values really were when the operator compared them, and "Finance" against "finance" will be obvious once you see them side by side.

If a step failed with a permission or access error, the workflow tried to do something it is not allowed to do, or a credential it depends on is wrong or expired. And if an action timed out, recall the ninety second ceiling on actions from Module 04, which bites most often when many calls are stacked inside a loop.

The method underneath all of these is the same, and it is worth saying as a method. Read the status. Find the first step that failed or came up empty. Look at that step's real input and output in the history. Form one hypothesis about why. Fix that one thing. Test again with the dangerous steps simulated off. Debugging is not cleverness, it is this loop done patiently.

## Running it again, and the trap of the second run

Sooner or later a workflow will fail halfway through, and your instinct will be to run it again. Pause before you do, because this is where a careless fix makes things worse.

Think about what already happened before the failure. Suppose Priya's onboarding workflow created an account, opened a ticket, and then failed at the next step. If you simply run the whole thing again from the top, it may try to create the account a second time and open a second ticket. The word for a step that is safe to run more than once, landing in the same place each time, is idempotent. Sending a welcome email twice is idempotent enough, a little annoying and no real harm. Creating an account twice, or granting the same access twice, may not be, and can leave a genuine mess.

So build with the second run in mind. For any step that changes the world, ask what happens if this runs twice, and if the answer is troubling, guard it. Check before you act. Before creating the account, check whether it already exists. Before granting access, check whether the person already has it. This is one more reason the get-and-verify habit from Modules 04 and 06 matters, because a check in front of a change is what makes a workflow safe to re-run.

And carry one honest limit with you, which Modules 04 and 05 already hinted at and Module 11 will press harder. Testing cannot prove everything. You cannot practically test a three day Wait, and you cannot summon a real external outage on demand to see how your error branch behaves. So testing and defensive design are partners, not substitutes. You test what you can, and for everything you cannot rehearse, you design so that the failure is handled rather than fatal.

## Before you move on

Walk a real diagnosis in your head. You test Priya's offboarding workflow and it appears to do nothing at all. What is the very first place you look to tell whether it ran and failed or never ran in the first place, and if there is no execution record at all, what is the first thing you suspect? During that same test, which single feature would you use so that the Manage Access step does not really remove Priya's access while you check the rest of the logic, and exactly which control turns it off? If the welcome email arrives greeting her by a blank instead of her name, where in the history do you look, and what will an empty Step Input value be telling you? And if the workflow created a ticket and then failed before finishing, what must you check before you dare run it again, and what is the name for the property that makes a step safe to repeat? If those answers come without strain, you can test without fear and debug without guessing, and you are ready for Module 08, where we take these workflows into real operation, with its limits, its governance, and its scale.

---
[← Previous: Module 06 Data, Variables, and Expressions](06-data-variables-and-expressions.md) | [Course home](../README.md) | [Next: Module 08 Operations, Limits, and Governance →](08-operations-limits-and-governance.md)
