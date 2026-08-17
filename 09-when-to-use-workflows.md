# Module 09: When to Use Workflows, and When Not

Choosing the right tool, and knowing when a workflow is the wrong one.

Every module before this taught you what workflows can do. This one teaches the harder and more valuable thing: when a workflow is the right tool, and when reaching for it is a mistake. A workflow can technically do a great many things. That is exactly the danger, because "it can" is not "it should." The engineer who forces every problem into a workflow, simply because it is the tool they know best, builds fragile, slow, hard-to-maintain automations that a better-chosen tool would have handled cleanly. So we are going to lay out the neighbors honestly, give you a way to decide, name the traps by name, and then state the real limits of workflows so you always know where the edge is.

## Meet the neighbors, honestly

Back in Module 00 you got a quick map of the tools around workflows. Now that you understand workflows deeply, you can understand the neighbors deeply too, because you can see exactly where each one starts and stops.

Transforms are for shaping the value of an attribute. They are configurable JSON, no code, and they run while ISC aggregates data from a source or provisions data to one. If the job is "this value should be calculated or formatted a certain way," a transform is the answer, and it is cheap and quiet because it runs as part of how an identity or account is built. What a transform cannot do is reach out to other systems, orchestrate a sequence of steps, or make branching decisions of any real complexity. It shapes a value and nothing more. When you catch yourself building a workflow whose real purpose is to compute one attribute, stop, because that is a transform wearing a workflow costume.

Rules are for logic that the configurable tools genuinely cannot express, and they are written in code, specifically Java BeanShell. They are the most powerful option and the heaviest, and SailPoint's own guidance is blunt about it: treat rule usage as a last resort and use built-in ISC features whenever you can. There are two families. Cloud rules run inside the ISC cloud in a restricted context, typically to calculate an attribute value, and they can read the ISC data model but cannot commit changes to it. Connector rules run on the virtual appliance out at the connection to an end system, and they do not have access to the ISC data model at all. The fact that decides everything about rules in practice is this: SailPoint requires every rule to be reviewed before it is deployed, with a stated turnaround of about one business day. So a rule is not something you tweak on a whim over lunch. It is code, it is reviewed, it is slow to change, and you reach for it only when nothing lighter will do.

Provisioning is the machinery that actually creates, updates, enables, and disables accounts on your connected sources. It is not usually a "workflow or provisioning" choice, because provisioning is the engine that other things set in motion. When Priya gets a role, or her lifecycle state changes, ISC provisions the resulting account changes to the real systems. A workflow can start provisioning, but it does not replace it. If your goal is that an account genuinely changes on a target system, that is provisioning's job, most often driven by the access model, and a workflow that tries to micromanage account changes by hand is usually reinventing an engine that already exists.

Roles, access profiles, and lifecycle states are the access model, and they deserve a place in this list because so much of what people build workflows for belongs here instead. If a person should have certain access because of who they are, their department, their job, their lifecycle state, that is birthright access, and you model it with roles and access profiles and let the access model grant it automatically. You do not write a workflow that hands out standard employee access one person at a time. The access model does that better, consistently, and with proper certification and audit behind it. Workflows are for the side effects and the exceptions, not for the core "who gets what."

Event trigger subscriptions are the do-it-yourself cousin of workflows, and understanding them sharpens what workflows are for. The same ISC events that start a workflow can instead be delivered straight to your own external service, as an HTTP webhook or through Amazon EventBridge, so that your own code handles the event in whatever language and with whatever horsepower you like. There is a further distinction worth knowing: some triggers are fire-and-forget, a one-way notification that can have many subscribers, and some are response-required, an interactive kind that expects your service to send a decision back, with time limits on the answer. A workflow is the no-code, managed way to react to an event inside ISC. A direct subscription is the way to react to the same event in your own system when you need to. Same events, two very different amounts of control and effort.

## A way to decide

When a new task lands, walk it down a short path of questions and let the first honest yes tell you the tool.

Is the task really just to shape or calculate an attribute value. If yes, it is a transform, not a workflow.

Should the access be granted or removed because of who the person is or what state they are in. If yes, model it with roles, access profiles, and lifecycle states, and let the access model do it. A workflow at most notices and adds a side effect.

Does the account actually need to change on a target system. That change is provisioning, set in motion by the access model or a lifecycle change. A workflow can trigger it, but the fulfillment is provisioning's.

Is the task to react when something happens by orchestrating a sequence of notifications, approvals, lookups, or calls, with no code, at a modest volume. This is the true home of the workflow. Say yes here with confidence.

Does the task need your own code, a specific language or library, heavy or high-volume processing, or a request-response exchange that returns data to ISC. If yes, this points at a direct event trigger subscription to your own service, or a purpose-built integration, rather than a workflow.

Is there logic that only code can express and none of the above fits. Then, and only then, a rule, accepting that it must be reviewed and is slow to change.

Notice that the workflow is the fourth question, not the first. That order is the whole lesson. Reach for the lighter, more purpose-built tools first, and let the workflow own what it is genuinely best at, which is event-driven orchestration that ties several actions together without code.

## Anti-patterns, named so you can avoid them

Some misuses are common enough to have a shape. Learn to see them.

The mega-workflow tries to do everything in one enormous canvas, all of onboarding and provisioning and notification at once. It is hard to test, hard to change, and one failure takes down the lot. The fix is the modularity from Module 08: small, focused workflows, each doing one job.

The bulk processor loops a workflow over your whole population on a schedule, night after night. It will pile up executions against the per-workflow block and the tenant throttle from Module 08, and it is simply not what workflows are for. Bulk work belongs in search, certifications, or an external job built for volume.

The attribute-shaper uses Get Identity, Define Variable, and maybe an HTTP call to compute a value that a transform should own. It is slower, more fragile, and burns executions to do a transform's quiet job. Move it to a transform.

The birthright-by-workflow hands out standard access one identity at a time with a workflow, instead of modeling it as a role and letting the access model grant it. You lose consistency and clean audit, and you take on maintenance you did not need. Model the access, and let the workflow handle only the extras, the welcome note, the ticket.

The poller runs a scheduled workflow that keeps checking for something an event would have told it instantly. If an event trigger exists for the thing you are polling for, use the event and delete the poll.

The no-filter firehose fires on every event and sorts out the ones it cares about inside the workflow, which wastes executions and, as Module 07 showed, makes failures harder to reason about. Filter at the trigger.

And two you have already been warned about: rebuilding approvals out of plain forms instead of approval policies, from Module 05, and hiding a secret inside a workflow definition, from Module 08. Both have proper tools. Use them.

## The honest limits of workflows

A confident engineer knows the ceiling of every tool they use. Here is where workflows genuinely end, stated plainly so you never mistake the edge for a personal failing.

They are not built for volume. The roughly four hundred thousand daily executions and the drop to five per second, and the per-workflow block at a hundred and fifty thousand, all say the same thing: workflows are for event-scale automation, not for grinding through large data sets.

They have timeouts. Actions cap out around ninety seconds, so a slow external call or a long operation will fail, and stacking many calls in a loop makes this worse.

They are not a general programming environment. Complex algorithms, heavy data manipulation, and tight processing over large collections are painful or impossible to express well in the builder, and that pain is a signal to move the work to code that lives outside a workflow.

They depend on systems you do not control. Every HTTP Request and every connector action ties your workflow's fate to another system's availability and behavior, which is a permanent source of failure you manage rather than remove.

They are hard to change safely and to fully test. There is no rich built-in version history, editing means disabling and opening a gap, and, as Modules 07 and 11 stress, you cannot rehearse a multi-day wait or a real outage. So workflows lean on discipline and defensive design in a way a self-contained program does not.

None of this makes workflows weak. It makes them specific. They are superb at one thing, reacting to an event by orchestrating a set of actions without code, and knowing exactly where that strength stops is what lets you use them with real confidence and reach for something else without hesitation when the task calls for it.

## Before you move on

Sort a handful of Acme tasks to their right tools, and say why in a sentence each. Format every identity's display name as "Last, First." When Priya is hired, give her the standard employee access every Acme staffer gets. When Priya moves to Finance, notify the Finance access owner and open a ticket. Every night, recompute a risk score for all eighty thousand identities and write it back. Stream ISC identity-created events into Acme's HR data lake for analytics. And compute one attribute using a lookup that a transform genuinely cannot express. For each, name the tool and the reason, and then answer the question that this whole module turns on: why is "a workflow could technically do it" never a good enough reason on its own to use one? If those come easily, you can choose tools like an engineer, and you are ready for Module 10, where we walk through the real use-case patterns a workflow is exactly right for.

---
[← Previous: Module 08 Operations, Limits, and Governance](08-operations-limits-and-governance.md) | [Course home](../README.md) | [Next: Module 10 Use-Case Patterns →](10-use-case-patterns.md)
