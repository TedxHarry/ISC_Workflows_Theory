# Module 08: Operations, Limits, and Governance

Running workflows safely at scale, for years, in a system other people depend on.

Building a workflow is one skill. Operating a growing collection of them responsibly is another, and it is the one that separates a hobbyist from an engineer a company can trust. This module is about the parts nobody sees in a demo: the hard limits that constrain what a workflow may do, how to change one without breaking the process it runs, how to move and manage workflows properly, how to handle secrets, and the plain habits that keep dozens of workflows from turning into a swamp. None of this is glamorous. All of it is what keeps you out of trouble.

## The limits, in real numbers

ISC puts real ceilings on how much work workflows can do, and knowing the exact numbers changes how you design. There are two levels, one for your whole tenant and one for each single workflow.

```
Tenant, per day:   about 400,000 executions at full speed (loop iterations not counted here),
                   then everything slows to 5 executions per second until the 24-hour reset.

Single workflow:   100,000 executions (loop iterations counted) -> warning banner and an email to the owner
                   150,000 executions (loop iterations counted) -> further executions are blocked, owner notified
```

Read those carefully, because the two levels behave differently and the difference matters. At the tenant level, hitting roughly four hundred thousand executions in a day does not stop your workflows, it slows them to a crawl of five per second for the rest of the day, and the quota resets every twenty four hours. At the single-workflow level the consequence is harsher: one workflow that runs one hundred and fifty thousand times, counting every loop iteration, has its further executions blocked outright. A single runaway workflow can shut itself off.

Notice the small print that is easy to miss. The tenant-wide limit does not count loop iterations, but the per-workflow limits do. So a workflow with a loop over a large list piles up executions against its own hundred-thousand and hundred-fifty-thousand thresholds much faster than you would guess from counting how often the workflow is triggered.

This is the operational reason behind advice I have given you since Module 03. A loop over thousands of items, especially one that calls out on every pass, is not just slow, it is spending your execution budget and marching toward the per-workflow block. The item caps on loops, two hundred and fifty and one thousand, and the counsel to keep loops modest, are the platform telling you that workflows are built for event-scale automation, not for bulk data processing. If you find yourself wanting a workflow to churn through your entire employee population every night, that is a signal to rethink the approach, which is the conversation waiting in Module 09.

Trigger filters matter here too, not just for correctness but for cost. A mover workflow with no filter, in a company where attributes change all day, fires on every one of those changes and burns executions doing nothing useful. The filter from Module 02 that narrows it to the changes you actually care about is also what keeps the workflow cheap. Correctness and operability turn out to be the same discipline.

And the one you already know from Module 00: when workflows are first enabled in a tenant, it can take up to two hours for the feature to become fully functional. A normal delay, not a fault.

## Changing a workflow without breaking the process

Here is an operational fact with real consequences: a workflow must be disabled before you can edit it. That sounds like a minor UI rule, but think about what it means for a live process. While the leaver workflow is disabled so you can change it, leaver events are not being handled by it. Editing a running workflow opens a gap in the automation, however brief, so you plan the change like maintenance, at a quiet time, and you know what is not being processed while it is down.

The second hard truth is about safety nets. Do not count on a version-history-and-restore button to save you after a bad edit. The documentation does not describe one, so the reliable safety net is the one you make yourself, and it is simple: before you change anything, export the workflow as JSON and keep that copy. If your change goes wrong, you re-import the known-good version and you are back where you started. This is the same idea a developer gets from source control, and you can literally keep your exported workflow JSON in a code repository so every version is saved with a note about why it changed.

So a safe change has a shape, and it is worth making it a habit. Export a backup of the current workflow. Disable it. Make the edit. Test it the safe way from Module 07, simulating the world-changing steps or using a sandbox. Then re-enable it and watch the first real executions in the history. Export, disable, edit, test, enable, watch. Boring on purpose, because boring is what you want when the thing you are editing removes people's access.

## Moving workflows around

Remember from Module 01 that a workflow is really just a JSON document. That fact is what makes workflows portable. You can download a workflow as JSON, using the Download Script option in the Actions menu or the download icon in the builder, and you can create a workflow by starting from a JSON file and uploading one. That is your mechanism for backing up, sharing, and moving workflows between places.

Promotion between tenants, most often from a sandbox to production, is done either through the Configuration Hub, which is ISC's tool for moving configuration between tenants, or by exporting and importing the JSON by hand. Either way, there is a gotcha you must respect, and it is the same lesson that bit you in Module 07 with test input. The JSON contains tenant-specific ids, the ids of identities, sources, and other objects, and those ids do not mean the same thing in another tenant. A workflow that points at a source by its id in sandbox will point at nothing, or worse at the wrong thing, when it lands in production, until you fix those references. Moving a workflow is never quite copy and paste. Always re-check the ids after a promotion, and test in the destination before you trust it.

## Managing workflows as code

The builder is not the only way to manage workflows, and for a serious team it is not the main way. ISC exposes a Workflows API and a Triggers API, along with software development kits and a command line tool, so you can create, update, list, export, and monitor workflows programmatically. The Workflow Executions API, which we met in Module 07, is part of this same surface and is how you pull execution history older than ninety days.

Why does this matter to you, even if you build in the visual editor today. Because it is how workflows grow up. A mature team keeps its workflow definitions in source control, reviews changes the way it reviews code, and promotes them through a pipeline from sandbox to production rather than clicking through the builder in each tenant. You do not need to work that way on day one, but you should know that the door exists, because the moment you have more than a handful of important workflows, treating them as code is what keeps them trustworthy. The developer documentation is where the specific API, CLI, and SDK details live.

## Secrets and security in HTTP actions

The HTTP Request action from Module 04 often needs a credential, a token or a key, to authenticate to the system it calls. How you handle that credential is a security decision, and two verified facts about workflows tell you why you must handle it with care. First, a workflow can be downloaded as plain JSON by anyone with the right access, as we just discussed. Second, the execution history shows the rendered values of variables, as we saw in Module 07. Put those together and the danger is obvious: a secret written carelessly into a workflow can leak, either through an exported definition or through what the history records.

So the rules follow directly. Never hard-code a password or token into a workflow, because the definition is exportable and a secret inside it is a secret handed out. Use the HTTP Request action's own authentication settings rather than pasting a credential into a URL or a body. When the call is to ISC's own APIs, that usually means a personal access token, which is a client id and secret pair, or an OAuth flow. When the call is to an outside system, use that system's proper authentication, and prefer credentials that are scoped narrowly and expire, rather than an all-powerful key that lives forever. Rotate credentials on a schedule, because a token that never changes only grows more dangerous. And be careful what you place into emails, chat messages, and anything the execution history captures, so that you never echo a secret or sensitive personal detail into a notification or a log where it does not belong.

I will be honest about the edge of what I can confirm here. The official workflow documentation is light on a built-in place to store secrets, so treat the guidance above as sound security practice and confirm the current options in your own tenant rather than assuming a particular feature exists. The principle is stable even where the mechanics shift: a credential is a liability, so give it the least exposure and the shortest life you can.

## Keeping a growing collection sane

You will not have one workflow. You will have dozens, built by different people over years, and a pile of unlabeled automations that all quietly change access is a genuine risk. Four plain habits keep that from happening.

Name with a convention. Decide on a naming scheme and hold to it, so the Workflows page and the executions list stay searchable when there are fifty entries. A simple prefix by process, something like Joiner, Mover, Leaver, and Ops, means anyone can find and reason about a workflow at a glance instead of opening ten to find the right one.

Keep workflows modular. Let each workflow do one job. Recall from Module 02 that two different events want two different workflows, and the same spirit applies to scope: a small, focused workflow is easier to test, easier to change, and easier to debug, and a failure in it cannot drag down unrelated logic the way a sprawling everything-workflow can. Resist the urge to build one giant workflow that does the whole onboarding, provisioning, and notification story in one canvas.

Document the why. Use the description field and give steps clear names, because there is no rich version history to explain a decision to the person who inherits this in two years, and that person might be you. The reason a filter is shaped a certain way, or why a step waits three days, needs to live somewhere a reader will find it. Your exported JSON in a repository, with commit notes, is part of this documentation.

Monitor what you run. Automation you do not watch is automation you do not really trust. Use the execution history and filter by failed status to see what is breaking. Heed the per-workflow banners when a workflow approaches the hundred-thousand and hundred-fifty-thousand thresholds, because they are warning you before the block. And build watchdog workflows, the aggregation-failure alert pattern from Module 02 is the model, so that your automation tells a human when it is unhappy rather than failing in silence.

## Before you move on

Reason about running Priya's workflows at Acme scale. If Acme has sixty thousand employees whose attributes change all day, and a mover workflow has no trigger filter, which two limits from this module might it run into, and what single change relieves both the cost and the risk of the block? Before you edit the live leaver workflow, what are the first two things you do and why does the disable step have a consequence beyond the edit itself? When you promote a workflow you tested in sandbox up to production, what inside its JSON will quietly point at the wrong thing until you fix it? And if a workflow must call an outside system with a token, name the two verified facts about workflows that make hard-coding that token a real leak, and say what you would do instead. If those answers come readily, you can operate workflows responsibly, and you are ready for Module 09, where we step back and decide when a workflow is even the right tool at all.

---
[← Previous: Module 07 Testing, Debugging, and Execution](07-testing-debugging-and-execution.md) | [Course home](../README.md) | [Next: Module 09 When to Use Workflows, and When Not →](09-when-to-use-workflows.md)
