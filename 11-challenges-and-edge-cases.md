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

> **Work It Out**
>
> Acme's Joiner workflow sends a welcome email and opens a starter ticket. The workflow successfully opens the ticket but later fails, so an engineer runs the onboarding process again. Meanwhile, some new hires arrive with manager or department information that is not usable for the notification. What problems can this create, and how should the design handle both?
>
> <details>
> <summary>Check your answer</summary>
>
> A re-run can repeat business side effects that already succeeded, such as creating another starter ticket or sending another welcome. Make those operations idempotent where required by checking durable state or the target system before repeating them, for example confirming whether a starter ticket for this new hire already exists. Separately, validate the identity data the process requires. If manager or department is not usable, retrieve the current identity state with Get Identity and branch rather than assuming the value exists. If the business action truly requires data that becomes available later, choose a later event or lifecycle transition that corresponds to that requirement rather than acting on first creation.
>
> </details>

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
> The double alert comes from the workflow running more than once for what looks like a single move, whether from repeated events or a re-run, so the notify step is not safe to repeat. Make it idempotent where it matters. If duplicate suppression is a business requirement, keep a durable marker or idempotency key in a system that persists across separate workflow executions, and check that state before sending again, so a repeat skips the duplicate. Do not rely on the workflow remembering on its own that it already sent the alert, because separate executions do not share memory. The missing alert comes from an unhandled dependency failure: the chat service was down and nothing caught it. Give that step an error path, so a failed send is routed to a deliberate Failure or a backup notification rather than vanishing. A notification workflow feels low-risk, but duplicate and dropped messages are exactly the partial-failure and external-dependence problems this module is about.
>
> </details>

> **Work It Out**
>
> Priya's offboarding workflow removed her access, disabled her account, and opened a ServiceNow ticket, then failed before the final confirmation step. You re-run it from the start. What can go wrong, and how should the workflow have been designed so the re-run is safe?
>
> <details>
> <summary>Check your answer</summary>
>
> A re-run from the start can repeat the steps that already succeeded, opening a second duplicate ticket and re-issuing access and account changes that were already applied. Design each world-changing step to be safe to repeat. Before opening a ticket, check whether a ticket for this offboarding already exists. Before removing access or disabling an account, check the current state so a repeat is a no-op rather than a fresh action. Order cheap checks before expensive or irreversible actions, and keep enough durable state to recognize that an earlier attempt already completed a step, so recovery does not multiply side effects.
>
> </details>

> **Work It Out**
>
> Acme's aggregation-failure alert works, but one source starts failing every hour and the alert fires on every cycle, flooding the channel until people mute it. The next week a different source fails and no one notices, because the channel is muted. How should the workflow have handled the repeated failure, and what should it do if the alert channel itself is unavailable when it tries to send?
>
> <details>
> <summary>Check your answer</summary>
>
> Treat a continuing failure as one condition, not one alert per run. Suppress repeated alerts for the same ongoing failure, for example by recording that this source is already in a failed-and-notified state in durable storage that persists across executions, and only alerting again when the state changes or after a deliberate reminder interval, so an hourly failure does not train people to ignore the channel. For the alerting dependency itself, do not assume the send always succeeds. If the chat or email service is unavailable, route that failure to a deliberate path, such as a backup channel or a Failure that is itself monitored, rather than letting the notification vanish silently. A monitoring workflow that goes quiet when its own channel is down is the worst time to lose the signal.
>
> </details>

## Native change is a signal, not a verdict

Native Change Detection is built for drift, and drift is a real security concern. But the workflow must be careful with language and action. The event tells you ISC detected an out-of-band account create, update, or delete during aggregation on a configured source. It does not, by itself, prove the change was malicious, who made it, or whether the business intended it through an emergency path outside ISC.

That matters because native-change response workflows sit close to real access. A notify-only workflow can still create noise or leak sensitive data into the wrong channel. A remediation workflow can change access. If the workflow automatically revokes every direct entitlement addition, it can undo a valid emergency grant. If it disables an account created directly on the source, it can interrupt a legitimate break-glass or service account process unless the business rule says that is exactly what should happen.

The safer architecture is staged:

```
detect  ->  classify  ->  notify or ticket  ->  remediate only when the rule is clear
```

Classify from fields the payload actually gives you: source, account, correlation state, event type, account change types, entitlement additions or removals, and account attribute changes. Enrich only when you need data the seed does not carry, for example current identity details or ownership routing. If the account is uncorrelated, do not invent a human owner. Treat it as an account investigation and route to the source owner.

Auto-remediation adds two more edge cases. First, revocation needs a valid entitlement id. SailPoint's Native Change Detection workflow template documentation says those templates skip entitlements with null IDs because revocation requests require a valid Entitlement ID. Second, remediation can create follow-on events. Removing an entitlement changes the account, and a later aggregation can observe that changed state. If your workflow alerts on every observed change without suppression, or if a source admin keeps re-adding the same group and the workflow keeps removing it, you have an incident loop, not a clean control.

Make the repeated path explicit. For alerts, record a durable incident key such as source id, account id, entitlement id, event type, and a time window, then suppress duplicates or update the existing ticket. For remediation, re-read current state before acting when the action is risky, and skip if the entitlement is already gone. That is idempotency applied to drift response.

The unsupported-source edge case is ordinary, not exotic. If no event arrives, do not start by rewriting JSONPath. Confirm Native Change Detection is available and enabled for that source, the monitored operation and attributes match the direct change, and aggregation has run. SailPoint also documents that Native Change Detection is not available for Non-Employee Lifecycle Management sources, while SAML Just-in-Time sources require the API endpoint for enablement.

> **Work It Out**
>
> Acme builds auto-revocation for direct AD additions to `Finance Privileged Operators`. During an outage, the AD team adds Priya to that group for a documented emergency. The workflow revokes it on the next aggregation, sends a green execution record, and Security later asks why the workflow "fixed the unauthorized change." What is wrong with that interpretation, and how would you redesign the response?
>
> <details>
> <summary>Check your answer</summary>
>
> The green execution proves the workflow followed its path, not that the original change was unauthorized or that revocation was the right business action. Native Change Detection proves out-of-band drift was detected during aggregation. It does not prove malicious intent or emergency status. Redesign the response so high-risk entitlement additions are classified first, with a notify or ticket path by default and auto-remediation only for changes covered by a clear policy. Add an exception path for documented emergency access, include source owner review, and make repeated events safe by using a durable incident key or by checking current state before revoking again.
>
> </details>

## Access requests across separate boundaries and executions

Access requests stretch across several boundaries that are handled at different times, and most access-request edge cases come from forgetting that. Hold the approved and denied paths apart:

```
submitted  ->  final decision
                 |-> approved  ->  provisioning  ->  provisioning result recorded by ISC  ->  target independently observed
                 |-> rejected  ->  no access grant from this request
```

A request waiting on approval is normal after Manage Access. If the requested item requires approval, Manage Access submits the request and the workflow continues without waiting for the final decision. A green Manage Access step therefore does not prove approval happened.

Adaptive Approval is different. A workflow started by Access Request Submitted uses Approval Policy as the approval process itself. Logic after that Approval Policy can branch on the result once the configured approval criteria are met and the action completes. That workflow can still end before provisioning finishes, but do not describe it as though the approval decision is still pending after the workflow has already branched on the Approval Policy result.

A final rejection is also a normal, handled outcome. When a request is denied, the correct workflow behavior is to follow its rejection path and end, and that execution can be a success even though no access was granted. This is the green does not mean approved lesson from Module 10: a green execution can mean a correctly handled rejection, so never read overall status as evidence of the business decision.

A partial Manage Access failure is the multi-item version of the same trap. A single Manage Access step can return a nonempty `failedAccessRequests` alongside `successfulAccessRequests` and still complete green, as Module 04 showed. If every requested item must succeed, inspect both arrays and branch, rather than trusting the step status.

Provisioning is a separate boundary on the approved path. An approved decision does not mean provisioning finished, and Provisioning Completed firing does not by itself prove the access is confirmed live on the target. A denied request does not proceed to an access grant from that request. Where certainty matters on an approved path, treat the target-system check as its own step.

Re-runs and duplicate requests need real caution here, because submitting an access request is a world-changing operation. Do not assume Manage Access is idempotent; its Workflow documentation does not promise that property. Separately, SailPoint's Access Requests API documents asynchronous submission and warns that duplicate requests submitted in quick succession may not return an error. That API behavior does not prove which internal endpoint Manage Access uses, but it supports the defensive design lesson: before replaying a workflow that submits access, check whether equivalent work is already pending or whether the access is already held instead of blindly repeating the request.

These lifecycle signals can appear in separate workflow executions, so do not design a dependency on cross-workflow timing or ordering unless SailPoint explicitly documents that guarantee. Treat each execution as its own event context. If a later workflow needs authoritative status, re-read current state or use the data carried by the event that represents that boundary rather than assuming another execution already finished.

Finally, be careful with multi-item requests and fan-out. A person can submit a basket of several items in the Request Center, but do not treat that basket as one atomic unit, and do not invent exact fan-out mechanics that SailPoint does not document. What is safe to rely on is that access-request items can be processed and provisioned individually, and that the Adaptive Approval Workflow seed for Access Request Submitted carries a singular `requestedItem`, so your workflow reasons about the item represented by that event. Do not turn that into an undocumented guarantee of exactly one workflow execution per basket item. If the precise fan-out behavior matters to your design, validate it against your tenant's real executions rather than assuming.

> **Work It Out**
>
> Acme's workflow runs on Access Request Submitted for a sensitive access profile, makes the decision with an Approval Policy, and notifies on both branches. Two incidents come in. First, a manager says a request was "approved by the workflow" but the person still has no access two hours later. Second, an auditor flags that a run for a denied request is marked successful and asks whether the denial was actually enforced. Explain both.
>
> <details>
> <summary>Check your answer</summary>
>
> Both come from confusing the workflow's boundary with the whole chain. In the first incident, the workflow owns the approval decision, not provisioning. An approved decision inside this execution does not mean provisioning has finished or that the access is live on the target, so the two-hour gap does not prove the approval workflow failed. Check the provisioning stage through Provisioning Completed and provisioning or account activity, and if certainty is required, verify the target itself. In the second incident, a successful execution for a denied request is correct, not a defect. The workflow's job on a denial is to follow its rejection branch and end, so green means the denial path was handled successfully, which is exactly green does not mean approved. Confirm the business decision from the request's final denied outcome, not from the workflow's overall status. If the separate question is whether the person already had equivalent access for some other reason, inspect current access or the target state rather than looking for a provisioning record from this denied request.
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
