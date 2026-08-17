# Module 11: Challenges and Edge Cases

The hard parts to reason about before you build.

You can now build a workflow, operate it, and choose when to use one. This module adds the layer that only experience usually teaches: the hard edges that show up at scale, under load, or when something upstream misbehaves. None of these are reasons to fear workflows. They are the things a seasoned engineer thinks about up front, so the workflow survives contact with the real world instead of breaking the first time reality does not cooperate.

One idea runs through every section, so hold it from the start. A workflow does not live in a tidy, private machine. It lives in a distributed, event-driven world it does not control, a world that is sometimes late, sometimes out of order, sometimes doubled, and occasionally just broken. The mark of a good workflow is not that this world behaves. It is that the workflow stays correct anyway.

## Loops and performance

Loops are the fastest way to turn a small workflow into an expensive one. Every pass is real work, and the costs stack in ways that are easy to underestimate. Recall the caps from Module 03, two hundred and fifty items for a parallel loop and a thousand for a serial one, and the fact from Module 08 that loop iterations count against a single workflow's own execution limits, marching it toward the block at a hundred and fifty thousand. Now add a loop that makes an external call on every pass, each one exposed to the ninety second action timeout from Module 04, and you have a workflow that is slow, costly, and fragile all at once.

The design response is discipline about size. Filter before you loop so you iterate over the few items that matter, not the many that do not. Keep loops modest. And treat a genuinely large list as the signal it is, the same signal from Module 09, that the job may not belong in a workflow at all. One more edge to carry from Module 03: a parallel loop gives no promise about order, so never build later logic that assumes the first item finished first.

## Throttling and the execution limit

The limits from Module 08 are not just numbers to memorize, they interact, and the interaction is where they bite. A noisy trigger with no filter, feeding a loop, can quietly push your tenant toward the point where everything slows to five executions per second, or push a single workflow toward its own block. And here is the part people miss: when workflows are throttled, they do not fail, they run late. A leaver deprovisioning that should have happened in seconds now happens hours later, and late security automation is a security problem, not a performance footnote.

So throttling is not only about speed, it is about correctness under load. The defenses are the ones you already know, now with higher stakes: filter at the trigger so you spend executions only on events that matter, keep loops small, spread scheduled work rather than stacking it, and watch the per-workflow warning banners so you act before the block, not after.

## Ordering and race conditions

This is the edge that surprises people the most, so I want to be honest and precise about it. The documentation does not promise that events arrive in the order they happened, nor that each event arrives exactly once. That absence is the lesson. A careful engineer does not assume ordering and does not assume single delivery, because nothing guarantees them.

Picture Priya. Her identity is created, and moments later an attribute change fires. Those two events could reach their workflows close together, and you cannot safely assume the created event is fully processed before the change is handled. Worse, two workflows can act on the same identity at the same moment and collide, one reading a value while another is changing it. A mover and a leaver that happen within the same minute can interleave in ways your happy-path design never pictured.

The response is to design as if order is not guaranteed, because it is not. Do not build logic that only works if event A lands before event B. Make steps safe to run in any order and more than once, which is the idempotency idea we keep returning to. Where an operation truly must be sequential, keep it inside a single serial loop where you do control the order, rather than spread across separate events you do not. And be wary of two workflows racing on the same object, because that is a bug that passes every calm test and fails only under real, concurrent load.

## Partial failures and retries

Here is a fact worth sitting with, because it shapes how you must build. ISC does not automatically retry a failed workflow execution. If a workflow fails, it stays failed until a human or a script does something about it, and the ways to recover are manual: re-invoke the workflow through the API with the original input, use the test endpoint which only works while the workflow is disabled, or simulate the event to run it again on the original data.

Now combine that with partial completion. Suppose Priya's offboarding workflow removed her access, opened a ticket, and then failed before the final notification. The work is half done. If you simply run it again from the top, it may remove access that is already gone and open a second duplicate ticket, because re-running repeats the steps that already succeeded.

So you design for the second run from the beginning. Make world-changing steps idempotent by checking before acting, as Module 07 taught, so a repeat does not double-apply. Where you can, order steps so the riskiest and least reversible ones come last, after everything that could fail cheaply has already succeeded. The goal is a workflow where a partial failure followed by a re-run lands in the right place, rather than one where recovery creates a fresh mess.

## Large payloads

Data has weight. A trigger that carries a big array, an HTTP response that returns a large blob, an identity dragged around with every attribute it owns, all of this costs time and pushes steps toward their timeouts, and a big array can run straight into the loop caps. The workflow does not thank you for carrying more data than the job needs.

The response is leanness. Pull only what you actually use. The Get Identity action from Module 04 lets you select the output you need rather than hauling everything. Narrow your searches. Do not pass a huge object from step to step when a couple of fields would do. When an external call could return a large result, ask for less, or page through it, rather than swallowing it whole. A lean payload is a fast, cheap, reliable workflow, and a bloated one is slow and brittle for no benefit.

## Error handling

Every edge in this module eventually comes down to one habit: giving failure a path. Any step that reaches outside the workflow can fail, and the question is never whether one will, but what happens when it does. An unhandled failure is the worst outcome, not because it failed, but because it can fail silently, and a silent failure is one nobody fixes.

So handle it. Put an error branch on the steps that can break, and read what the failure tells you. An error branch gives you the detail to act on, for example:

```
workflowStatusCode: 503
workflowErrorMessage: Service Unavailable
```

which tells you plainly that the far system was down rather than that your logic was wrong. From there you can do something deliberate: end the branch in a Failure with a clear name so it shows up in the history from Module 07, notify a human, or route to a fallback. The point is that the failure becomes visible and intentional instead of vanishing. Design so that when something breaks, a person finds out.

## Dependence on external systems

Your workflow is only as reliable as the systems it calls, and that ceiling is permanent. Every HTTP Request and every connector action ties your fate to another system that can be down, slow, rate-limiting you, or quietly returning a different shape than it did last week. You cannot make those systems reliable. You can only refuse to be surprised by them.

That means timeouts and error branches on every outbound step, and defensive reading of every response, because a response that is missing a field or shaped differently is exactly the null-handling problem from Module 06. It also means deciding, in advance, what should happen when the other side is simply unavailable. Should the work wait and be retried later by a scheduled sweep, should it queue, should it alert a human. Choosing that on purpose is the difference between a workflow that degrades gracefully and one that falls over the first time a dependency has a bad day.

## The limits of testing

The honest capstone of this whole module is that you cannot test your way to certainty, and it is important to accept this rather than pretend otherwise. You cannot practically rehearse a three day Wait. You cannot summon a real outage on command to watch your error branch behave. You cannot easily reproduce two events racing, or the moment the tenant hits its throttle, and the serial-loop test only runs the first fifty iterations anyway, from Module 07. So testing proves the happy path and some of the failures, and leaves a set of paths you will never fully rehearse.

The response is not to test less, it is to pair testing with design and monitoring. Test everything you reasonably can. For everything you cannot rehearse, design so that the untested path fails safely and visibly, through idempotency, error branches, and lean, order-independent steps. Then monitor, so that when one of those rare paths finally happens in production, and it will, you find out early. That combination, test what you can and design so the rest cannot hurt you quietly, is what production-grade actually means.

## Before you move on

Reason through the hard cases for Priya, out loud, the way you would defend a design. Her mover and leaver events arrive within the same minute, and you cannot be sure which is processed first, so what could go wrong, and what property must your steps have for it not to matter? A leaver workflow removed access, opened a ticket, and then failed before notifying, and now you re-run it: what breaks on the second run, and what must the earlier steps be for the re-run to be safe, given that ISC will not retry it for you? When the ticket system is down while forty leavers process at once, what should each workflow do instead of failing in silence, and which two features make that possible? And finally, say plainly why no amount of testing can fully prove that leaver workflow, and what you do about that gap. If you can reason through those without reaching for certainty you do not have, you are thinking like an engineer who is ready for production, and you are ready for Module 12, where you prove it by designing workflows on paper.

---
[← Previous: Module 10 Use-Case Patterns](10-use-case-patterns.md) | [Course home](../README.md) | [Next: Module 12 Readiness and Paper Design →](12-readiness-and-paper-design.md)
