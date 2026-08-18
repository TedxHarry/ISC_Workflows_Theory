# Module 11: Challenges and Edge Cases

The hard parts to reason about before you build.

You can now build a workflow, operate it, and choose when to use one. This module adds the layer that only experience usually teaches: the hard edges that show up at scale, under load, or when something upstream misbehaves. None of these are reasons to fear workflows. They are the things a seasoned engineer thinks about up front, so the workflow survives contact with the real world instead of breaking the first time reality does not cooperate.

One idea runs through every section, so hold it from the start. A workflow does not live in a tidy, private machine. It lives in a distributed, event-driven world it does not control, a world that is sometimes late, sometimes concurrent, and occasionally broken. The mark of a good workflow is not that this world behaves. It is that the workflow stays correct anyway.

## Loops and performance

Loops are the fastest way to turn a small workflow into an expensive one. Every pass is real work, and the costs stack in ways that are easy to underestimate. Recall the caps from Module 03, two hundred and fifty items for a parallel loop and a thousand for a serial one. Loop executions count toward the individual workflow's total execution count, which produces a warning at 100,000 and blocks remaining executions at 150,000.

Now add an external action on every loop pass and the design becomes even more sensitive to latency and timeouts. Do not assume one universal action timeout. HTTP Request is documented at 90 seconds, Get Identity at 1 minute, Manage Access at 30 minutes, and Manage Accounts at 1 hour. A loop that repeatedly calls an external or connector-backed action multiplies both the workload and the number of places a dependency can fail.

The design response is discipline about size. Filter before you loop so you iterate over the few items that matter. Keep loops modest. Treat a genuinely large list as the signal it is, the same signal from Module 09, that the job may not belong in a workflow at all. And remember from Module 03 that a parallel loop gives no promise about order.

## Throttling and execution limits

The limits from Module 08 interact in different ways. The tenant-wide daily rate limit is around 400,000 executions and does not include loop executions. After that threshold, executions continue at 5 per second for the rest of the day. The individual workflow count does include loop executions and warns at 100,000 total executions, then blocks remaining executions at 150,000.

A noisy trigger can therefore hurt you in two directions. It can contribute to tenant-wide rate limiting, and if the workflow also loops heavily it can drive that individual workflow toward its own block.

Rate limiting is not only about speed. If an important automation is delayed by a crowded execution queue, the business effect can be late notifications, late integrations, or late security actions. The defenses are the ones you already know: filter at the trigger, keep loops controlled, spread scheduled work sensibly, and act on high-execution warnings before the block is reached.

## Ordering and race conditions

This is the edge that surprises people the most. Do not design separate event-driven workflows on the assumption that related events will always be processed in the neat business order you imagined.

Picture Priya. Her identity is created, and moments later an attribute change occurs. Those workflows may run close together. Two workflows can also act on the same identity at nearly the same time, one reading state while another changes it. A mover and a leaver occurring close together can create combinations your happy-path test never pictured.

The response is to reduce dependence on timing between separate workflows. Re-read current state before making a sensitive decision when necessary. Make operations safe to repeat where possible. Keep truly sequential operations inside one controlled flow rather than relying on the relative timing of independent event handlers.

## Partial failures and retries

A workflow can complete some work and then fail later. That partial completion is often more dangerous than a clean failure at the start.

Suppose Priya's offboarding workflow removed access, opened a ticket, and then failed before the final notification. Re-running the workflow from the beginning can repeat steps that already succeeded. A duplicate ticket is easy to picture. A repeated access action may be harmless in one system and problematic in another.

So design for the second run from the beginning. Make world-changing steps idempotent where practical by checking before acting or using operations whose repeated execution has a safe result. Order steps thoughtfully so cheap validations happen before expensive or irreversible actions. Preserve enough information to tell whether a prior attempt already completed a step.

Do not assume the workflow engine will automatically repair every failed business process for you. Recovery should be part of the design: a human may re-run a process, an API-driven recovery process may invoke it again, or another scheduled control may identify unfinished work. Whatever recovery method you use, it is only safe if the earlier steps tolerate repetition.

> **Work It Out**
>
> Acme's Finance mover alert notifies the gaining team whenever someone moves into Finance. In production it occasionally sends two alerts for the same move, and once it sent none because the chat service was briefly down. What is happening in each case, and how would you make the workflow behave?
>
> <details>
> <summary>Check your answer</summary>
>
> The double alert comes from the workflow running more than once for what looks like a single move, whether from repeated events or a re-run, so the notify step is not safe to repeat. Make it idempotent where it matters, for example by recording that an alert for this move already went out and checking that before sending, so a second run skips the duplicate. The missing alert comes from an unhandled dependency failure: the chat service was down and nothing caught it. Give that step an error path, so a failed send is routed to a deliberate Failure or a backup notification rather than vanishing. A notification workflow feels low-risk, but duplicate and dropped messages are exactly the partial-failure and external-dependence problems this module is about.
>
> </details>

## Large payloads

Data has weight. A trigger that carries a big array, an HTTP response that returns a large blob, or a workflow that preserves more attributes than later steps need all make the flow harder to reason about and can increase processing cost.

The response is leanness. Pull and preserve only what you need for downstream logic. Narrow searches. Avoid passing giant arrays into loops when a filtered subset will do. When an external service supports paging or narrower queries, use them instead of swallowing a huge response and making the workflow do bulk processing.

## Error handling

Every edge in this module eventually comes down to one habit: give failure a path.

Any step that depends on another service, connector, or human can fail or return an unexpected result. An unhandled failure is bad not because failure exists, but because the workflow gives nobody a clear route to understand and recover from it.

Use error handling on steps that can break. Read the details the failed action provides. Route the workflow to a deliberate Failure when the business process truly failed, notify an operator when intervention is needed, or take a fallback path when one exists.

Also distinguish action completion from business completion. Manage Access is a good example from Module 04: a successful action result does not guarantee that every requested access item ultimately succeeded, and `failedAccessRequests` does not automatically fail the overall workflow execution. Error handling therefore includes validating important outputs, not only catching thrown errors.

## Dependence on external systems

Your workflow is only as reliable as the systems it calls. Every HTTP Request and connector-backed action ties your process to another system that can be down, slow, rate-limiting you, rejecting credentials, or returning a response shape you did not expect.

You cannot remove that dependency. You can only design around it. Know the action-specific timeout. Handle errors. Validate responses before trusting them. Decide in advance whether a failure should stop the process, notify a human, fall back, or be picked up by a later reconciliation process.

Credentials are part of that dependency too. Use the supported authentication and Parameter Storage mechanisms rather than hard-coding secrets into workflow definitions.

## The limits of testing

You cannot test your way to certainty, and accepting that is part of engineering rather than a weakness.

You cannot conveniently rehearse every long Wait, every dependency outage, every race between real production events, or every condition that appears only at high execution volume. A serial-loop test that covers only a limited number of iterations does not prove how a large production run behaves. Simulated testing protects systems from selected actions but cannot reproduce every behavior of the real target systems.

The response is not to test less. It is to pair testing with design and monitoring. Test everything you reasonably can. For paths you cannot fully rehearse, make failure safe and visible. Then monitor the real executions so rare production conditions are discovered quickly.

## Before you move on

Reason through the hard cases for Priya. Her mover and leaver workflows run close together. What state assumptions could become stale, and where would you re-check current state before acting? A leaver workflow removed access, opened a ticket, and then failed before notifying. What happens if you re-run it, and what property must the earlier steps have to make that recovery safe? A ticketing API starts responding slowly while forty leavers process. Which action-specific timeout and error-handling questions matter? A Manage Access step is green, but one access item is in `failedAccessRequests`. Why is that still a business failure you may need to handle? And finally, why can no amount of testing completely prove a production workflow? If you can reason through those without reaching for certainty you do not have, you are ready for Module 12.

---
[← Previous: Module 10 Use Case Patterns](10-use-case-patterns.md) | [Course home](../README.md) | [Next: Module 12 Readiness and Paper Design →](12-readiness-and-paper-design.md)
