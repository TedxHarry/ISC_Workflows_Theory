# Module 09: When to Use Workflows and When Not

Choosing the right tool, and knowing when a workflow is the wrong one.

Every module before this taught you what workflows can do. This one teaches the harder and more valuable thing: when a workflow is the right tool, and when reaching for it is a mistake. A workflow can technically do a great many things. That is exactly the danger, because "it can" is not "it should." The engineer who forces every problem into a workflow, simply because it is the tool they know best, builds fragile, slow, hard-to-maintain automations that a better-chosen tool would have handled cleanly. So we are going to lay out the neighbors honestly, give you a way to decide, name the traps by name, and then state the real limits of workflows so you always know where the edge is.

## Meet the neighbors, honestly

Back in Module 00 you got a quick map of the tools around workflows. Now that you understand workflows deeply, you can understand the neighbors deeply too, because you can see exactly where each one starts and stops.

Transforms are for shaping the value of an attribute. They are configurable JSON, no code, and they run while ISC aggregates data from a source or provisions data to one. If the job is "this value should be calculated or formatted a certain way," a transform is the answer, and it is cheap and quiet because it runs as part of how an identity or account is built. What a transform cannot do is reach out to other systems, orchestrate a sequence of steps, or make branching decisions of any real complexity. It shapes a value and nothing more. When you catch yourself building a workflow whose real purpose is to compute one attribute, stop, because that is a transform wearing a workflow costume.

Rules are for logic that the configurable tools genuinely cannot express, and they are written in code, specifically Java BeanShell. They are the most powerful option and the heaviest, and SailPoint's own guidance is to use built-in ISC features whenever possible. Cloud rules run inside the ISC cloud in a restricted context. Connector rules run closer to the connected system through the virtual appliance. The important design lesson is that a rule is code and carries a heavier lifecycle than a no-code feature. Reach for it only when the supported configurable tools genuinely cannot express the requirement.

Provisioning is the machinery that actually creates, updates, enables, and disables accounts on connected sources. It is not usually a "workflow or provisioning" choice, because provisioning is the engine that other things set in motion. A workflow can request or coordinate a change, but provisioning is what fulfills supported account changes on the target system.

Roles, access profiles, and lifecycle states are the access model, and they deserve a place in this list because so much of what people build workflows for belongs here instead. If a person should have certain access because of who they are, their department, their job, or their lifecycle state, model that through the access model. Workflows are better suited to side effects, orchestration, exceptions, notifications, and integrations than to recreating the core "who gets what" model one person at a time.

Event trigger subscriptions are the do-it-yourself cousin of workflows. The same family of ISC events that can start workflows can also be delivered to external services through event-trigger mechanisms. A workflow is the managed no-code way to react inside ISC. A direct subscription lets your own service receive the event and handle it with your own code, libraries, infrastructure, and scaling model.

## A way to decide

When a new task lands, walk it down a short path of questions and let the first honest yes tell you the tool.

Is the task really just to shape or calculate an attribute value? If yes, use a transform rather than a workflow.

Should access be granted or removed because of who the person is or what state they are in? If yes, model it with roles, access profiles, and lifecycle configuration. A workflow may add a side effect, but it should not replace the access model.

Does an account actually need to change on a target system? That change is fulfilled through provisioning. A workflow can initiate or coordinate the request, but it does not replace the provisioning engine.

Is the task to react when something happens by orchestrating notifications, approvals, lookups, or calls, with modest volume and no custom code? This is the true home of workflows.

Does the task need your own code, a special library, heavy data processing, high throughput, or behavior that fits better in an external service? Then an event-trigger subscription or purpose-built integration may be the better tool.

Is there logic that only code can express and none of the supported configurable tools fit? Then consider a rule, accepting the maintenance and review implications that come with code.

Notice that the workflow is not the first answer. That order is the lesson. Reach for the most purpose-built supported tool first.

## Anti-patterns, named so you can avoid them

The mega-workflow tries to do everything in one enormous canvas, all of onboarding, provisioning, notification, ticketing, and cleanup at once. It is hard to test, hard to change, and one failure can drag unrelated behavior into the same incident. The fix is modularity from Module 08.

The bulk processor loops over a huge population on a schedule. Loop iterations count toward an individual workflow's total executions, which produces a warning at 100,000 and blocks remaining executions at 150,000. A large scheduled job can also contribute to the tenant-wide daily rate limit of around 400,000 non-loop executions, after which executions continue at 5 per second for the rest of the day. Bulk work belongs in a tool designed for bulk processing, not in a workflow pretending to be one.

The attribute-shaper uses Get Identity, Define Variable, and perhaps an HTTP call to compute one attribute that should be owned by a transform. It is slower, harder to reason about, and spends workflow executions to do a transform's quiet job.

The birthright-by-workflow pattern hands out standard access one identity at a time with a workflow instead of modeling it through roles and access profiles. You take on maintenance that the access model already solves better.

The poller runs a scheduled workflow that keeps checking for something an event would have told it directly. If an appropriate event trigger exists, use the event instead of burning executions on repeated polling.

The no-filter firehose fires on every event and sorts out relevance after the workflow has already started. That wastes executions and makes operations noisier. Filter at the trigger when the trigger's payload supports the condition you need.

And two you have already met: rebuilding governed approvals out of ordinary forms instead of approval tooling, and hard-coding credentials into workflow definitions instead of using supported secure parameter handling.

## The honest limits of workflows

A confident engineer knows the ceiling of every tool they use.

They are not built for bulk volume. At the tenant level, around 400,000 daily executions triggers rate limiting to 5 executions per second for the remainder of the day, and that tenant counter does not include loop executions. At the individual workflow level, loop executions do count: 100,000 total executions produces a warning and 150,000 blocks remaining executions for that workflow.

Actions have timeouts, but there is no single universal timeout. Get Identity is documented at 1 minute, HTTP Request at 90 seconds, Manage Access at 30 minutes, and Manage Accounts at 1 hour. The correct engineering habit is to check the action you are actually using rather than carrying one timeout number around in your head.

They are not a general programming environment. Complex algorithms, heavy transformations over large collections, and specialized libraries are signs that the work may belong in code outside the workflow engine.

They depend on systems you do not control. Every external API call and connector-backed action introduces another system's availability, latency, credentials, and behavior into your workflow's reliability.

They are difficult to prove completely through testing. You cannot practically reproduce every external outage, race condition, long wait, or production-scale load scenario. That is why testing, defensive design, and monitoring all matter together.

None of this makes workflows weak. It makes them specific. They are excellent at event-driven orchestration without custom code. Knowing where that strength stops is what lets you use them well.

## Before you move on

Sort a handful of Acme tasks to their right tools and say why. Format every identity's display name as "Last, First." Give all employees standard birthright access. Notify the Finance access owner and open a ticket when Priya moves to Finance. Recompute a large risk dataset for eighty thousand identities every night. Stream identity-created events into an external analytics service. Compute one value using logic the supported transforms cannot express. For each, name the tool and the reason, then answer the question this module turns on: why is "a workflow could technically do it" never enough reason on its own? If those come easily, you can choose tools like an engineer, and you are ready for Module 10.

---
[← Previous: Module 08 Operations, Limits, and Governance](08-operations-limits-and-governance.md) | [Course home](../README.md) | [Next: Module 10 Use Case Patterns →](10-use-case-patterns.md)
