# Module 08: Operations, Limits, and Governance

Running workflows safely at scale, for years, in a system other people depend on.

Building a workflow is one skill. Operating a growing collection of them responsibly is another, and it is the one that separates a hobbyist from an engineer a company can trust. This module is about the parts nobody sees in a demo: the hard limits that constrain what a workflow may do, how to change one without breaking the process it runs, how to move and manage workflows properly, how to handle secrets, and the plain habits that keep dozens of workflows from turning into a swamp.

## The limits, in real numbers

ISC applies limits at two different levels, and the distinction matters.

```
Tenant, per day:
  around 400,000 executions at the normal rate
  loop executions are not counted toward this tenant threshold
  after the threshold, executions continue at 5 per second for the rest of the day

Individual workflow:
  100,000 total executions, including loop executions -> warning and owner notification
  150,000 total executions, including loop executions -> remaining executions are blocked
```

Read those carefully because the two levels behave differently. At the tenant level, crossing the daily threshold does not stop workflows. It rate-limits remaining executions to 5 per second for the rest of the day. At the individual workflow level, loop executions count toward the workflow's total, and crossing 150,000 blocks that workflow's remaining executions.

This is the operational reason behind advice I have given you since Module 03. A loop over a large list can drive one workflow toward its own execution limit much faster than the number of trigger events suggests. At the same time, those loop iterations do not count toward the tenant-wide daily threshold. The two counters measure different things, so always ask which limit you are talking about.

Trigger filters matter here too, not just for correctness but for cost. A mover workflow with no filter can fire on every matching event and spend executions doing work you did not need. A good trigger filter is both a correctness control and an operational control.

And remember the one from Module 00: when workflows are first enabled in a tenant, it can take up to two hours for the feature to become fully functional. A normal delay, not a fault.

## Changing a workflow without breaking the process

A workflow must be disabled before you can edit it. That sounds like a minor UI rule, but think about what it means for a live process. While the leaver workflow is disabled so you can change it, events that would have depended on that enabled workflow are not being processed by it. Treat the change as maintenance, not as casual editing.

Do not count on a rich built-in version-history-and-restore experience to save you after a bad edit. Before you change an important workflow, download its JSON and keep that known-good copy. If the change goes wrong, you have a clean definition to restore or compare against.

A safe change therefore has a repeatable shape: export a backup, disable the workflow, make the change, test it safely, re-enable it, and watch the first real executions. Boring on purpose, because boring is what you want when the automation changes access or accounts.

## Moving workflows around

Remember from Module 01 that a workflow is a JSON definition underneath the builder. You can download workflow metadata or JSON from the workflow interface and use JSON definitions to back up, share, or reproduce workflows.

Promotion between tenants may be handled with configuration-management tooling or by moving JSON definitions, depending on the organization's process. The important engineering point is tenant-specific references. Ids for identities, sources, access items, and other objects are not portable assumptions. A value that is correct in a sandbox may point at nothing or at the wrong object in production unless you re-resolve it.

So every promotion gets a destination check: confirm the ids and environment-specific values, then test in the destination before enabling the workflow for real traffic.

## Managing workflows as code

The visual builder is not the only management surface. SailPoint exposes workflow APIs and related SDK tooling so teams can list, create, update, inspect, and monitor workflows programmatically.

Why does that matter even if you build in the visual editor today? Because definitions stored in source control give you reviewable history outside the product UI. A mature team can keep workflow JSON beside its other configuration, review changes, and use a controlled promotion process instead of relying entirely on memory and manual clicks.

Execution history is a separate retention concern. Workflow executions are available for up to 90 days. Current Workflow Executions API documentation also states that archived executions beyond that window return 404. If audit or operational evidence must live longer than 90 days, export or retain the evidence in another system rather than assuming the workflow API is a permanent archive.

## Secrets and Parameter Storage

HTTP Request and privileged actions often need credentials, tokens, endpoints, or authorization information. Those values should not be scattered through workflow definitions.

ISC provides Parameter Storage, a SailPoint-managed secure repository for supported authentication, connection, and authorization parameters. Supported parameter types include credentials, Entra ID client credentials, HTTP custom authorization, OAuth 2.0 client credentials, connection information, and OAuth scopes. Availability depends on the AWS region and the capabilities supported there.

The HTTP Request action can use stored authentication parameters for Basic Authentication, Custom Authorization, and OAuth 2.0 client credentials. That is preferable to hard-coding a password, client secret, or authorization header into a workflow body or URL.

The rule is simple: keep secrets in the supported secure parameter mechanism, scope them as narrowly as practical, rotate them according to your organization's policy, and avoid echoing sensitive values into email, chat, or workflow-visible output.

## Keeping a growing collection sane

You will not have one workflow. You will have dozens, built by different people over years, and a pile of unlabeled automations that quietly change access is a genuine risk. Four plain habits keep that from happening.

Name with a convention. Decide on a naming scheme and hold to it so the Workflows page and execution views stay searchable. A prefix by process, such as Joiner, Mover, Leaver, and Ops, lets someone understand purpose before opening the workflow.

Keep workflows modular. Let each workflow do one job. Recall from Module 02 that two different initiating events usually want two different workflows, and the same spirit applies to scope. A small focused workflow is easier to test, change, and debug than one giant canvas that owns every side effect of a business process.

Document the why. Use the description field and give steps clear names. The reason a filter is shaped a certain way, or why a step waits three days, should be discoverable by the person who inherits the workflow later. Source-controlled JSON and change notes can carry the history the runtime UI is not designed to preserve forever.

Monitor what you run. Use execution history to see failures while those records are available. Watch the high-execution warnings at 100,000 total executions for an individual workflow and act before the 150,000 block. Watch tenant execution usage so a noisy design does not push the tenant into the 5-per-second rate-limited state. And use operational workflows, such as an aggregation-failure alert, so automation tells a human when something important breaks.

## Before you move on

Reason about running Priya's workflows at Acme scale. If Acme has sixty thousand employees whose attributes change all day and a mover workflow has no trigger filter, which tenant and individual-workflow limits could become relevant, and what single design change reduces unnecessary executions? Before you edit the live leaver workflow, what are the first two things you do and why does disabling it matter operationally? When you promote a workflow from sandbox to production, what values inside its definition require special attention? If a workflow must call an outside system with credentials, where should supported credentials live rather than being hard-coded? And if an auditor wants execution evidence from a year ago, why should you not assume the Workflow Executions API will still have it? If those answers come readily, you can operate workflows responsibly, and you are ready for Module 09.

---
[← Previous: Module 07 Testing, Debugging, and Execution](07-testing-debugging-and-execution.md) | [Course home](../README.md) | [Next: Module 09 When to Use Workflows and When Not →](09-when-to-use-workflows.md)
