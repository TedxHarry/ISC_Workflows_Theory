# Module 12: Readiness and Paper Design

Prove the theory without a tenant.

You have reached the end of the theory. The question now is not whether you have read the modules, but whether you can use them. The honest way to check that is to design workflows on paper and reason about them the way an engineer does before touching a builder. That is what this module is for. It gives you a repeatable method for designing any workflow in your head, walks through full designs so you can see the reasoning in motion, hands you scenarios to design yourself, and ends with a readiness check that tells you whether you are ready for labs and real work.

Designing on paper is not a lesser version of building. It is the part experienced engineers do first and fastest, because catching a bad trigger choice or an unhandled failure on paper costs a minute, and catching it in production costs an incident.

## A method you can apply to anything

For any workflow you are asked to design, answer these seven questions in order. They are the course turned into a checklist.

First, the trigger and its filter. What real event starts this, and how do you narrow it to only the events you actually care about? Remember that the filter is both correctness and cost from Modules 02 and 08.

Second, the data. What does that trigger hand you for free, and what is missing that you will have to fetch with a Get step? This is the Module 06 habit of knowing your real payload.

Third, the logic. What decisions does the workflow make, what are the branches, and which operators express them? What happens on each branch, including the one where the answer is no?

Fourth, the actions. What does the workflow actually do, and in what order? Which steps change the world and which only read or notify? What does each action actually guarantee when it reports success?

Fifth, failure and limits. What can fail? Which action-specific timeouts matter? Could the tenant-wide daily rate limit or the individual workflow execution limits become relevant? Every important failure needs a deliberate path.

Sixth, re-run safety. If this runs twice, or if two related workflows run close together, does the process still land in the right place? This is the idempotency and stale-state question from Modules 07 and 11.

Seventh, the test plan. How do you test this safely, simulating world-changing steps or using a sandbox from Module 07? Which parts cannot be fully rehearsed, so they must be made safe through design and monitoring instead?

Run those seven every time and you will rarely be surprised, because the surprises will have happened on paper where they are cheap.

## A worked design, start to finish

Here is a scenario, designed out loud so you can watch the method work.

Acme hires contractors, and each contractor identity has a contract end date. When that date passes, Acme wants the contractor's accounts disabled, the sponsoring manager notified, and, if the sponsor does not confirm within three days, the matter escalated to security. Design it.

Start with the trigger, and notice immediately that there is no automatic assumption that "contract end date has passed" is the event you need. One clean approach is a Scheduled Trigger that runs each morning and finds contractors whose end date is today or earlier. Another approach fits if the end date already drives a lifecycle-state transition, in which case Identity Lifecycle State Changed may be the better event. Let us take the scheduled approach because it does not depend on lifecycle configuration you may not have.

Now the data. A schedule hands you no person, so the workflow must find its subjects. A search or Get List of Identities can find matching contractors, and the workflow can fetch each person's additional details when needed, including the sponsor information required for notification.

The logic and actions come together. You loop over the contractors found. For each one, you disable the required accounts with Manage Accounts, notify the sponsor, and then wait for confirmation. A normal Form action can assign a form to the sponsor and pause until the sponsor submits it or the deadline is reached. If the sponsor responds, continue the success path. If the deadline expires, handle the cancellation path deliberately and escalate to security.

Now failure and limits. Manage Accounts has an action-specific timeout of 1 hour, so a slow target-system operation has a different ceiling from an HTTP Request or Get Identity. The loop also matters operationally because loop executions count toward the individual workflow's total. SailPoint warns at 100,000 total workflow plus loop executions and blocks remaining executions at 150,000. The tenant-wide daily rate limit is separate: around 400,000 executions, excluding loop executions, after which executions continue at 5 per second for the rest of the day. For a daily contractor-expiration population, the count should normally be small, but you still validate that assumption rather than treating scale as somebody else's problem.

Re-run safety is the subtle part. If the scheduled workflow runs again tomorrow, will it disable accounts that are already disabled or send the same sponsor request again? Build a check before acting, or otherwise design the process so a repeated run is harmless. Scheduled sweeps can rediscover unfinished subjects, so idempotency here is not optional.

Finally the test plan. Test in a sandbox when possible. Simulate or disable the account-changing step while validating the logic. Use short test deadlines rather than trying to wait three real days. And accept that you still cannot reproduce every provisioning failure or concurrency condition, so those paths need safe error handling and monitoring.

That is a complete, defensible design, and you built it with no tenant. Notice that every one of the seven questions earned its place.

## A second, quicker design

Acme wants a message in the security channel whenever an account is changed directly on a critical system outside normal ISC control.

Start with the trigger. If the direct change is a new account, use Native Change Account Created. If it is an update to an existing account, such as a new AD group assignment, use Native Change Account Updated. If the account disappeared from the target, use Native Change Account Deleted. Do not use ordinary Account Updated unless the question is simply "ISC account data changed" rather than "the target changed outside ISC."

Then check the source configuration. Native Change Detection must be enabled, the relevant operation must be monitored, and the relevant attribute must be monitored. For an AD privileged group, that usually means monitoring Account Updates and the entitlement attribute that carries group membership. Aggregation must run after the target change before the event can be detected.

The data is enough for a good alert: source, account, native identity, correlation state, event type, account change types, and the entitlement or account attribute that changed. If the account is correlated, the payload gives identity context. If it is uncorrelated, route to the source owner and say it is uncorrelated rather than inventing a human owner. Enrichment belongs only where the alert or ticket needs more current identity, owner, or routing context.

The first version should usually be notify-only. If the business wants remediation, make that an explicit branch with extra proof: a valid entitlement id, a documented rule that says the change must be revoked, a source action that can do the revoke, and repeat-run behavior that will not create a loop. A green execution proves the workflow followed its path. It does not prove the original direct change was malicious, and it does not prove the target will stay corrected forever.

## Scenarios to design yourself

Now you. For each of these, run the seven questions and write the design in your own words.

Design a joiner welcome that emails Priya and her manager on her first day. A strong answer names Identity Created as the trigger, recognizes that the manager may require a lookup, and flags the Module 02 lesson that required fields in the Identity Created payload should be validated rather than assumed to contain usable non-null values.

Design a mover review that alerts the Finance access owner when anyone moves into Finance. A strong answer uses Identity Attributes Changed, reads the `changes` array correctly rather than assuming the first item, minds case sensitivity, and filters to the real department transition.

Design an aggregation-failure alert. A strong answer uses Account Aggregation Completed, filters on status so it speaks only on failures, and can say in one sentence why that filter is the whole point.

Design the sensitive Finance access approval workflow. A strong answer names what starts it: an Access Request Submitted trigger reached only because the access profile is configured to use an enabled Workflow as its Approval Type through Adaptive Approval. It names the data available, the item-oriented seed carrying a single `requestedItem`, `requestedBy`, `requestedFor`, and `accessRequestId`. It says clearly what the Approval Policy action owns, the governed decision and reviewer routing, and what happens on rejection, where the workflow follows its rejection branch, notifies, and ends successfully. It states what a green run actually proves, only that this execution reached and handled an approval decision, not that access was granted, provisioned, or is live. It identifies the separate event that observes the final decision, Access Request Decision, and, on an approved path where provisioning occurs, the separate event that observes the provisioning action, Provisioning Completed. And it names what still must be verified before anyone can say the access is definitely live on the target: an independent check of the Finance application itself, because neither the approval event nor the provisioning event is proof of confirmed-live access.

Design a Native Change response for Priya's AD account being added directly to `Finance Privileged Operators`. A strong answer uses Native Change Account Updated, not Identity Attributes Changed or Access Request Submitted. It names the source setup: Native Change Detection enabled, Account Updates monitored, group membership or all entitlement attributes monitored, and aggregation run after the target change. It reads `accountChangeTypes`, `entitlementChanges.added`, `source`, `account.nativeIdentity`, and `account.correlated`. It alerts Security and the source owner without claiming the change was malicious. If it proposes auto-revocation, it states the extra proof required: valid entitlement id, clear policy, supported action, exception handling, and idempotency so repeat events do not create a loop.

Design an inbound HR integration where an external HR service tells ISC that worker `W-18422` has a high-priority separation event. A strong answer uses External Trigger because the initiating event lives outside ISC. It defines a small contract such as `eventId`, `eventType`, `workerId`, and `effectiveAt`; validates that required fields exist and have the expected types; then validates allowed business values before any world-changing action. It does not assume `workerId` is an ISC identity id. It resolves that external identifier through a deliberate mapping strategy and stops or routes to investigation when the match is missing or ambiguous. It carries `eventId` as a durable idempotency key so a caller retry or operator replay does not repeat an already completed side effect. If the workflow calls another API with HTTP Request, it gives that action an error path, remembers the 90-second timeout, validates the JSON response it actually needs, and keeps credentials in supported secure parameter storage rather than in the workflow body.

Design a leaver offboarding that removes access, opens a ticket, and notifies, and survives a partial failure. A strong answer uses the lifecycle change trigger rather than Identity Deleted, orders the steps thoughtfully, validates important outputs such as `failedAccessRequests`, makes repeat execution safe, and gives external actions error paths.

Design something that should not be a workflow at all and explain why. A strong answer picks a case like formatting an attribute, granting standard birthright access, or running a nightly bulk recompute, and names the right tool instead from Module 09.

That last one matters as much as the rest. Knowing when not to build a workflow is a mark of readiness.

## Your readiness check

You are ready for the labs and real work when you can honestly say yes to each of these without a tenant in front of you.

You can explain the workflow model in your own words: one trigger, operators that decide and shape, actions that do, and a JSON data flow in which later steps read from earlier data.

You can pick the right trigger for a described event, including the judgment calls around joiner, mover, leaver, schedule, form, and external events, and you can explain what the trigger filter is buying you.

You can separate ordinary account events from Native Change account events, explain that native changes are detected during aggregation on configured sources, and design the first response without assuming the change was malicious or safe to auto-revert.

You can treat an External Trigger payload as caller-supplied data: authenticate the caller, validate the fields and allowed values, map external identifiers deliberately, and make replayed requests safe before a workflow changes access, accounts, or another system.

You can read and write JSONPath against a real payload, reach into arrays safely, and distinguish trigger-filter paths from paths used inside workflow steps.

You can choose actions and operators to build real behavior, know which steps change the world, and know that action timeout and success semantics are action-specific.

You can name what will fail, where the tenant and individual workflow execution limits sit, what each failure should do, and how to make a second run safe.

You can test without assuming the word "test" means harmless, and you know that some production behavior must be handled through defensive design and monitoring because it cannot be fully rehearsed.

And you can decide when a workflow is the wrong tool and say what to use instead.

If you can do those, you understand ISC workflows not as a list of features but as a tool you can reason about. That is what this course set out to give you.

## Where you go from here

The theory is done. You followed Priya from her first day to her last and learned to see the trigger, the data, the decision, the action, the failure, and the engineering judgment behind an automation.

Take this into the lab course next and build the things you have designed on paper. The builder will feel much less mysterious because you already understand what it is trying to represent, and debugging will feel more structured because you have been thinking about payloads, outputs, timeouts, and failure paths throughout the course.

Carry three habits with you above all. Choose the right tool rather than forcing the one you know. Design for retries, delays, partial failures, and imperfect dependencies. And make failure visible, because the workflow you can trust is not the one that never fails. It is the one whose behavior you can understand and recover safely.

---
[← Previous: Module 11 Challenges and Edge Cases](11-challenges-and-edge-cases.md) | [Course home](../README.md)
