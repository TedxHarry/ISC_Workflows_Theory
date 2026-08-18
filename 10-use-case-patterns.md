# Module 10: Use Case Patterns

The workflows people actually build, described so you can adapt them.

This module is a pattern library. Each entry is a real automation that teams build every day, described the same way you now think about all workflows: what starts it, how it thinks, what it does, and the one thing that bites it in production. It is also a review in disguise, because you will watch every trigger, operator, and action from earlier modules do real work. None of these are recipes to copy blindly. They are shapes to understand and bend to your own situation. Priya walks through many of them, because her joiner, mover, and leaver story touches most of what workflows are for.

A note before we start. A pattern is a starting point, not a finished build. The real skill this module is checking is whether you can look at a pattern, see why each piece is there, and spot the gotcha before it spots you.

## The joiner, mover, leaver family

**Joiner and leaver notifications.** The most common workflow of all simply tells the right people when someone arrives or departs. The trigger is Identity Created for a joiner or Identity Lifecycle State Changed for a leaver. The logic is light, often just a filter to the population you care about, and the action is a Send Email or Send Slack Message to the manager, the team, or an onboarding queue. The gotcha is data readiness and trigger choice. On a joiner, remember from Module 02 that an Identity Created payload can include a configured attribute whose value is null or otherwise unusable for the step you want to run. Validate the fields your message depends on, and fetch additional or current identity data when the trigger payload does not give you a usable value. On a leaver, use Lifecycle State Changed, not Identity Deleted, because as Module 02 warned, Deleted fires far too late for a timely notice.

To make the joiner side work-ready, decide what the workflow should and should not own. Routing and communication are a good fit: read the new hire's manager or department, fetching with Get Identity when the seed does not carry a usable value, and send the welcome and the manager or team notification, or open an onboarding task or ticket for the human steps. Core birthright access is a different matter. As Module 04 and Module 09 stress, roles, access profiles, and lifecycle states own standard access and account enablement for a new hire, so a joiner workflow should orchestrate and inform around that, and reserve any direct access change for a deliberate exception rather than rebuilding birthright provisioning one identity at a time. And remember the data-readiness gotcha from Module 02: validate the attributes the message depends on, because an optional attribute is not guaranteed to contain a usable, non-null value.

**Leaver ticketing.** When Priya leaves, the offboarding often needs a work item in another system, so the facilities, IT, or security team has a task to close out. The trigger is again the leaver lifecycle change. The logic gathers what the ticket needs, frequently a Get Identity to pull her full details, and the action is a Manage ServiceNow Ticket, or an HTTP Request to whatever ticketing system Acme runs. The gotcha is external dependence and repeat runs. The ticket system can be down or slow, so wrap that step in an error branch as Module 04 urged, and make the workflow safe to re-run as Module 07 stressed, so a second attempt after a partial failure does not open a second duplicate ticket.

To make the offboarding concrete, a leaver workflow often does several things in sequence: fetch Priya's details with Get Identity, remove access with Manage Access, disable her source accounts with Manage Accounts, and open a ticket so a human closes out the rest. Before building that, though, ask an architecture question. ISC lifecycle states can natively remove all access and enable, disable, or delete configured source accounts when an identity enters a leaver state, and for a lifecycle state that removes all access the removal approval is bypassed automatically. So do not duplicate those controls in a workflow unless the workflow is intentionally handling an exception, supplemental access, or a source or process the lifecycle-state configuration does not cover. Where the workflow does manage access and accounts deliberately, two lessons from earlier modules matter most. Keep green does not mean done from Module 04 in mind. For Manage Access, a successful submission does not mean the target access change is complete, so inspect the request results and account for approval or provisioning still being in progress. For Manage Accounts, inspect its account result and error outputs. And make the whole sequence safe to re-run as Module 07 stressed, so a second attempt after a partial failure does not repeat a change or open a duplicate ticket, which usually means checking whether each step's work already exists before doing it again.

**Mover alerts.** When Priya moves to Finance, sensitive teams often want to know, so they can review what access should change. The trigger is Identity Attributes Changed, and the logic is the real teaching from Module 03 and Module 06: read the `changes` array, confirm the attribute that changed is the one you care about, and mind casing differences and that more than one attribute can change at once. The action is a notification to the gaining team or the access owner. The gotcha is precision. A sloppy filter or a position-based read of the array sends alerts on the wrong changes or misses the right one, so match the department change deliberately rather than trusting that it sits first in the list.

To make that concrete, a Finance mover alert filters the trigger down to the department moving to Finance, then decides who to tell. If the message goes to the moving person's new manager, remember from Module 04 that the event carries the manager's id but not the manager's email, so you fetch the manager with Get Identity and read the email from that result. And keep green does not mean done in mind for the final step. If the expected notification is not received, inspect the Send Email input, output, and rendered recipient rather than assuming the status alone proves the intended person was notified.

## Data hygiene

**Data-quality remediation.** Every tenant accumulates messy identities, a missing manager here, a blank department there. A workflow can help you find and chase these. The trigger is usually a Scheduled Trigger or a Scheduled Search that runs a saved search for the bad records, and the logic loops over the results and checks each one. Here is the honest boundary, and it matters. A workflow is well suited to flagging the problem, notifying an owner, or opening a ticket to get it fixed, and it can push a correction into an authoritative source through an HTTP or connector action. What it should not pretend to do is directly edit a calculated identity attribute, because that shaping belongs to transforms and the source data, as Module 09 laid out. The gotcha is scale. A sweep over a large population runs headlong into the execution limits from Module 08, so scope the search tightly and do not try to boil the ocean nightly.

**Aggregation-failure alerts.** One of the most valuable operational workflows watches ISC's own health. The trigger is Account Aggregation Completed, the logic is a filter on the status, and the action tells a human when something broke. You saw the whole shape in Module 02: filter so the workflow only speaks up on non-success outcomes, using a defensive expression such as `$[?($.status != "Success")]` because SailPoint's materials currently differ on the exact non-success value, and validating it against your tenant's real payload. The gotcha is exactly that filter. Because the trigger fires on every aggregation including the successful ones, a version without the status filter floods your channel with noise about healthy runs, which trains people to ignore it right when it finally matters.

To make it work-ready, add two decisions to that shape. First, identify and route: read `source.name` from the event so the alert names the failing source and reaches the team that owns it, rather than a generic channel everyone ignores. Second, decide alert versus remediate. Aggregation failures can involve collection, connectivity, credentials, or source-system conditions, so unless the cause is known and the corrective action is safe and deterministic, notifying an operator is generally safer than attempting automatic remediation. And if the same source fails on every cycle, a workflow that alerts on each run becomes its own kind of noise, so suppress repeated alerts for an ongoing failure rather than paging the team every hour, a point we press on in Module 11.

## Access governance

**Sensitive access approval with Adaptive Approval.** This is the canonical governed-access pattern, and it is worth understanding in full because it exercises every boundary the course has been building toward. Priya requests a sensitive Finance access profile through the ISC Request Center. Because that access profile is configured to use an enabled Workflow as its Approval Type, the request is routed into your workflow through Adaptive Approval, and the Access Request Submitted trigger fires. From Module 02, remember the seed is item-oriented: it carries a single `requestedItem` with its `operation`, along with `requestedBy`, `requestedFor`, and `accessRequestId`, so the workflow knows exactly who asked, for whom, and for which item.

The logic reads that seed and then makes the governed decision with an Approval Policy action, routing the approval to the reviewers the business requires, for example the recipient's manager and then a security governance group. The workflow branches on the outcome:

```
Access Request Submitted
        |
        v
Read requestedItem / requestedFor / requestedBy
        |
        v
Approval Policy  (manager, then security governance group)
        |
        +---- APPROVED  ->  notify that the request was approved
        |
        +---- REJECTED  ->  notify that the request was rejected
        |
        v
Workflow can still end successfully
```

Here is the part that trips people up, and it is one of the sharpest lessons in the course. A rejected request is a legitimate, handled business outcome. If the workflow correctly follows its rejection branch, notifies the right people, and ends, that execution is a success. A green run does not mean the access was granted. It means the workflow did its job, which in this case may well have been to record a rejection. This is green does not mean approved, and it is the strongest version of green does not mean done you will meet.

Notice also what this workflow does not do. It does not itself provision the requested access. ISC's native access-request and provisioning processes own what happens after the decision. So even on the approved branch, the workflow reaching its end does not prove the access is live on the Finance application. It proves an approval decision was reached inside this execution, and nothing more.

To observe the boundaries that come after, use separate events rather than stretching this one execution across all of them:

```
Access Request Submitted
        ↓
approval process
        ↓
Access Request Decision
        |
        +---- APPROVED  ->  provisioning  ->  Provisioning Completed
        |                                      ↓
        |                              possible target verification
        |
        +---- DENIED    ->  no access grant from this request
```

Access Request Decision is a separate event that fires on the final approved or denied decision, so a distinct workflow can react to the outcome, for example to record it or to start downstream steps. On an approved path, provisioning can follow and Provisioning Completed can represent that later provisioning boundary. On a denied path, the request does not proceed to an access grant. Even Provisioning Completed is not independent proof that the access is confirmed live on the target. If the business needs that final certainty, target-specific verification is a separate step beyond these workflow events.

The gotcha, then, is boundary confusion. The most common production mistake with this pattern is treating one green execution as proof of the whole chain: submitted, approved, provisioned, and live. Those are four separate facts on four separate boundaries, and this workflow, by design, owns only the approval decision. Keep the workflow in its lane, let native governance and provisioning own theirs, and use the later events to observe the rest.

Enrichment can still belong inside this Adaptive Approval workflow, but it does not replace the governed decision. For example, fetch identity context with Get Identity or call a system of record before the Approval Policy so reviewers have better information, then let Approval Policy resolve the access request. Do not configure a workflow as an access item's Approval Type and teach it as an enrichment-only path that never reaches the approval mechanism. The safe pattern is enrich where useful, govern with Approval Policy, and let ISC's native access-request and provisioning processes own the rest.

**Certification kickoff.** A workflow can start an access review in response to an event, for example launching a targeted certification when a sensitive change happens. The trigger might be a mover change or a scheduled cadence, the logic decides whether a review is warranted, and the actions are Create Certification Campaign and Activate Certification Campaign from Module 04. The gotcha is weight. A certification is a heavy, human-intensive process, so you do not want to fire one on every small event. Gate it carefully, and be sure the thing you are reviewing genuinely needs a full campaign rather than a lighter notification.

## Security response

**Native-change response.** When a change is made directly on a target system, outside of ISC, that can be exactly the kind of unauthorized change you want to catch. The trigger is one of the Native Change Account triggers from Module 02, the logic examines what changed, and the action alerts a security reviewer, or in stronger designs pushes a correction back. The gotcha is judgment about automation. A native change is not always bad, so decide deliberately between detect-and-alert and automatic revert. If you choose to revert, you are changing real access, so test it with simulation on as Module 07 insisted, because an over-eager auto-revert can undo legitimate work.

**Outlier response.** ISC can flag an identity whose access looks anomalous, and a workflow can react. The trigger is Outlier Detected, which as Module 02 noted is a licensed capability, so it only appears if your tenant has it. The logic decides how serious the signal is, and the action routes it to a reviewer or opens a case. The gotcha is treating a signal as a verdict. An outlier is a hint, not proof, so the safe pattern is to notify and prompt a review rather than to automatically strip access, because false positives on automatic removal punish innocent people.

## Integration

**Chat and webhook integration.** Workflows are a natural bridge to the tools your people already live in. The trigger is whatever event matters, the logic shapes a message, and the action is a Send Slack Message or an HTTP Request to a webhook. Interactive Message belongs to an Interactive Process launched through the Launchpad, as Module 05 explains. The gotcha is security and dependence, straight from Module 08. Do not hard-code credentials into the HTTP call, and be careful never to spill sensitive personal data into a chat channel or a log, because a convenient notification is also a convenient leak.

**Inbound automation from an external system.** Sometimes the event that should drive ISC lives entirely in another system, such as an HR platform announcing a new hire before anything exists in ISC. The External Trigger lets that system call in and start a workflow with its own data. The logic then acts on that payload, and the actions do whatever the inbound event calls for. The gotcha is trust and identity. The payload is whatever the caller sends, so validate it with Verify Data Type before you rely on it, as Modules 03 and 06 taught, and remember from Modules 07 and 08 that ids from another system may not line up with ISC ids, so you often must look up the real identity rather than assume the incoming id matches.

## Evidence

**Scheduled evidence.** Auditors ask for proof that a control ran, and a workflow can gather and file that evidence on a schedule. The trigger is a Scheduled Trigger, and because nothing happened to any one person, the logic must go and find its subject, using Get List of Identities or a search, exactly the shift Module 02 described for scheduled work. The actions assemble the findings and send them to an external system of record. The gotcha is retention and scope. Workflow execution records are available for up to 90 days, so evidence that must live longer needs to be retained somewhere outside the workflow execution history. A broad scheduled gather also has to respect the execution limits from Module 08.

## Before you move on

Take one pattern and prove you own it rather than just recognize it. Pick the leaver ticketing pattern and name its trigger, the one lookup its logic most likely needs, its main action, and the two production gotchas it shares with the wider course, one about the system it depends on and one about running it twice. Then do something harder: sketch how you would combine two patterns into one sensible workflow for Priya's departure, a notification and a ticket, and decide what each branch does if the ticket system is unreachable at that moment. And finally, look back at the aggregation-failure pattern and say, in one sentence, why the filter is not a detail but the whole point. If you can do that, these stop being recipes you follow and become patterns you command, and you are ready for Module 11, where we press on the hard edges and the failures these patterns have to survive.

---
[← Previous: Module 09 When to Use Workflows and When Not](09-when-to-use-workflows.md) | [Course home](../README.md) | [Next: Module 11 Challenges and Edge Cases →](11-challenges-and-edge-cases.md)