# Module 12: Readiness and Paper Design

Prove the theory without a tenant.

You have reached the end of the theory. The question now is not whether you have read the modules, but whether you can use them, and the honest way to check that is to design workflows on paper and reason about them the way an engineer does before touching a builder. That is what this module is for. It gives you a repeatable method for designing any workflow in your head, walks through a couple of full designs so you can see the reasoning in motion, hands you scenarios to design yourself, and ends with a readiness check that tells you plainly whether you are ready for the labs and for real work.

Designing on paper is not a lesser version of building. It is the part experienced engineers do first and fastest, because catching a bad trigger choice or an unhandled failure on paper costs a minute, and catching it in production costs an incident.

## A method you can apply to anything

For any workflow you are asked to design, answer these seven questions in order. They are just the course, turned into a checklist you can run in your head.

First, the trigger and its filter. What real event starts this, and how do you narrow it to only the events you actually care about? Remember that the filter is both correctness and cost, from Modules 02 and 08.

Second, the data. What does that trigger hand you for free, and what is missing that you will have to go and fetch with a Get step? This is the Module 06 habit of knowing your real payload.

Third, the logic. What decisions does the workflow make, what are the branches, and which operators express them? What happens on each branch, including the one where the answer is no?

Fourth, the actions. What does the workflow actually do, and in what order? Which steps change the world and which only read or notify?

Fifth, failure and limits. What can fail, where do the timeouts and execution limits from Modules 04 and 08 come into play, and what does each failure do? Every step that can break needs a path, ending in a deliberate Failure where that is the truth.

Sixth, re-run safety. If this runs twice, or if events arrive out of order, does it still land in the right place? This is the idempotency question from Modules 07 and 11, and ISC will not retry for you.

Seventh, the test plan. How do you test this safely, simulating the world-changing steps or using a sandbox from Module 07, and what parts can you not fully rehearse, so you must design for them instead?

Run those seven every time and you will rarely be surprised, because the surprises will have happened on paper where they are cheap.

## A worked design, start to finish

Here is a scenario, designed out loud so you can watch the method work.

Acme hires contractors, and each contractor identity has a contract end date. When that date passes, Acme wants the contractor's accounts disabled, the sponsoring manager notified, and, if the sponsor does not confirm within three days, the matter escalated to security. Design it.

Start with the trigger, and notice immediately that there is no "contract end date has passed" event waiting for you. This is the judgment Module 02 was preparing you for. So you reason about it. One clean approach is a Scheduled Trigger that runs each morning and, with a search or a Get List of Identities, finds the contractors whose end date is today or earlier, using a timestamp comparison from Module 03. Another approach fits if the end date already drives a lifecycle state, in which case Identity Lifecycle State Changed is your event and no schedule is needed. Either is defensible, and being able to say why you chose one is the point. Let us take the scheduled approach, because it does not depend on lifecycle configuration you may not have.

Now the data. The schedule hands you no person, so, exactly as Module 02 warned about scheduled work, the workflow must go and find its subjects. Your search returns the matching contractors, and you will likely still fetch each one's details, including the sponsor, with a Get Identity, because the sponsor is what the notification needs.

The logic and actions come together. You loop over the contractors found. For each one, you disable their accounts with Manage Accounts, you notify the sponsor with a Send Email, and then you wait for confirmation. That waiting step is a human-in-the-loop moment from Module 05, so you use a Form or an Interactive Message with a deadline, and you let workflow variables pre-fill who and what so the sponsor only has to confirm. If the sponsor confirms, the workflow ends in Success. If the deadline passes, that is the timeout failure Module 05 told you to plan for, so the timeout branch escalates to security and ends deliberately, either in a clear Failure or a notification, so the escalation is visible.

Now failure and limits, which is where a design earns its keep. Disabling accounts is a real change, and it depends on provisioning and the target systems, so it can fail or be slow, and it deserves an error branch. The loop has the caps and the per-workflow execution cost from Modules 03 and 08, so you confirm the daily contractor count is small, which it will be, and you are safe. The waiting step makes this a long-running workflow, up to three days, which Module 04 flagged as a real cost.

Re-run safety is the subtle part, and this is where a junior design breaks. If the workflow runs again tomorrow, will it try to disable accounts that are already disabled, or notify a sponsor twice? So you build in a check before you act, only disabling accounts that are still enabled, which makes a second run harmless. And because a scheduled sweep could pick the same contractor up on two consecutive days if something stalled, idempotency here is not optional.

Finally the test plan. You test with the Manage Accounts step simulated off, so your logic, your notification, and your timeout escalation all run without actually disabling a real person, precisely the safety switch from Module 07. And you accept honestly, from Module 11, that you cannot truly rehearse the three day wait or a real provisioning outage, so you make sure those paths fail safely and visibly rather than trusting a test to prove them.

That is a complete, defensible design, and you built it in your head with no tenant. Notice that every one of the seven questions earned its place, and the hardest, most valuable thinking was in the last three, the ones a beginner skips.

## A second, quicker design

Try a lighter one to see the method move fast. Acme wants a message in the security channel whenever an account is changed directly on a critical system, outside of ISC.

The trigger is a Native Change Account trigger from Module 02, filtered to the critical source so you are not paged for every system. The data the trigger carries describes the change, and you may enrich it with a Get step if the message needs more. The logic is light, perhaps a check that the change is one worth reporting. The action is a Send Slack Message. The failures to consider are the external chat dependency from Module 08 and the reminder never to spill sensitive detail into a channel. Re-run safety barely matters here, since a duplicate alert is only mildly annoying, which is itself a judgment worth stating. And you would test it with a simulated or sandbox change so you do not cry wolf in the real security channel. Two minutes, whole design, because the method gives you the questions.

## Scenarios to design yourself

Now you. For each of these, run the seven questions and write the design in your own words. After each, I have named what a strong answer covers, so you can check yourself honestly, but resist reading those until you have tried.

Design a joiner welcome that emails Priya and her manager on her first day. A strong answer names Identity Created as the trigger, recognizes the manager is likely not in the seed so a Get Identity is needed, and flags the Module 02 risk that early attributes may still be filling in.

Design a mover review that alerts the Finance access owner when anyone moves into Finance. A strong answer uses Identity Attributes Changed, reads the `changes` array correctly rather than by position, minds case sensitivity, and filters to the real department transition.

Design an aggregation-failure alert. A strong answer uses Account Aggregation Completed, filters on status so it speaks only on failures, and can say in one line why that filter is the whole point.

Design an access-request enrichment that posts context to an owner when a sensitive entitlement is requested. A strong answer uses Access Request Submitted, enriches with a lookup, stays out of the approval decision itself since that belongs to an approval policy, and handles the access request service timing out.

Design a leaver offboarding that removes access, opens a ticket, and notifies, and survives a partial failure. A strong answer uses the lifecycle change trigger not Identity Deleted, orders the steps thoughtfully, makes them idempotent because ISC will not retry, and gives the ticket step an error branch.

Design something that should not be a workflow at all, and explain why. A strong answer picks a case like formatting an attribute or granting birthright access or a nightly bulk recompute, and names the right tool instead, a transform, the access model, or an external job, from Module 09.

That last one matters as much as the rest. Knowing when not to build a workflow is a mark of readiness, not a failure to use what you learned.

## Your readiness check

You are ready for the labs and for real work when you can honestly say yes to each of these, without a tenant in front of you.

You can explain the workflow model in your own words: one trigger, operators that decide and shape, actions that do, and a single JSON document that grows as it flows, with each step reading only from what came before it.

You can pick the right trigger for a described event, including the judgment calls, joiner versus leaver, lifecycle change versus deletion, event versus schedule versus external, and you can write a filter and say why it is correctness and cost at once.

You can read and write JSONPath against a real payload, reach into an array safely rather than by position, and say which of the two engines an expression belongs to.

You can choose actions and operators to build a real behavior, and you know which steps change the world and must be tested with the safety on.

You can name what will fail, where the limits and timeouts sit, and what each failure should do, and you design for re-runs and out-of-order events because you know ISC will not retry for you and does not promise order.

And you can decide when a workflow is the wrong tool, and say what to use instead.

If you can do those, you understand ISC workflows, not as a list of features, but as a tool you can reason about. That is what this course set out to give you.

## Where you go from here

The theory is done, and you built real understanding, from the anatomy of a single workflow all the way to the hard edges of running many of them in a world that does not always cooperate. You followed Priya from her first day to her last, and along the way you learned to see the trigger, the data, the decision, the action, the failure, and the judgment behind every automation.

Take this into the lab course next, and build the things you have designed on paper. You will find that the builder feels familiar, because you already understand what it is doing underneath, and that when something breaks, you know how to read it, because you have been thinking about failure since Module 01.

Carry three habits with you above all. Choose the right tool rather than forcing the one you know. Design for a world that is late, out of order, doubled, and occasionally broken, so your workflows stay correct when it is. And make failure visible, always, because the workflow you can trust is not the one that never fails, it is the one that tells you when it does. That mindset, more than any single feature, is what makes you an engineer people can rely on.

---
[← Previous: Module 11 Challenges and Edge Cases](11-challenges-and-edge-cases.md) | [Course home](../README.md)
