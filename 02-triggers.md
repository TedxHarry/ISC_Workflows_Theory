# Module 02: Triggers

What starts a workflow, and how to choose the right starting point.

Every workflow begins with a single question: what has to happen in the world for this automation to run? The trigger is your answer to that question. In this module we are going to do two things. First, understand triggers deeply through the few you will reach for again and again. Then, get a clear map of the rest so that when you meet a less common one, you already know where it fits and how to reason about it. I am deliberately not going to march you through twenty-five equal descriptions, because that would turn a skill into a list to memorize, and lists fall out of your head by Friday.

## What a trigger really is

Three things are true of every trigger, and they are worth stating plainly before we look at any specific one.

There is exactly one trigger per workflow. Not zero, not two. A workflow is a reaction to one kind of event, and if you find yourself wishing a workflow could start from two different events, that is a sign you actually want two workflows, or one workflow started by a broader event that you then narrow down inside.

The trigger supplies the seed data. We saw this in Module 01. Whatever the trigger knows about the event, it hands to the workflow as the starting JSON, and everything downstream reads from it. This means the choice of trigger decides what data you get for free. Pick the trigger that already carries the information you need, and your workflow gets simpler. Pick a trigger that does not carry it, and you will spend extra steps fetching what a better trigger would have handed you.

The trigger can carry a filter. A trigger fires on a whole category of events, for example every identity that gets created. Often you want only some of them. A filter is a small condition attached to the trigger that decides whether this particular event is worth running the workflow for. We will give filters their own section, because they are the source of a very common and very quiet kind of failure.

## The triggers you will actually use

Let us teach the handful that cover the large majority of real work. Learn these well and the rest of the catalog becomes easy to place.

### Identity Created, the joiner

This is Priya's first day. Her identity comes into being, and the workflow fires with the seed we already met:

```json
{
  "identity": {
    "type": "IDENTITY",
    "id": "2c91808568c529c60168cca6f90c1313",
    "name": "priya.patel"
  },
  "attributes": {
    "firstname": "Priya",
    "lastname": "Patel",
    "email": "priya.patel@acme.com",
    "department": "Sales"
  }
}
```

Reach for Identity Created whenever the trigger is "a new person now exists." Welcome emails, opening a starter ticket, notifying a manager, kicking off birthright access reviews. One caution to hold now and remember later: the payload includes identity attributes configured in the identity profile, but a field can still have a null or otherwise unusable value for the step you want to run. Do not treat presence in the payload as proof that every required value is ready for your process. Validate the fields your workflow depends on, and use a lookup when you need additional or current identity data.

### Identity Attributes Changed, the mover

Months later Priya moves from Sales to Finance. Her department attribute changes, and this trigger fires. Its seed has a shape you have not seen yet, and the shape is the whole lesson:

```json
{
  "identity": {
    "type": "IDENTITY",
    "id": "2c91808568c529c60168cca6f90c1313",
    "name": "priya.patel"
  },
  "changes": [
    {
      "attribute": "department",
      "oldValue": "Sales",
      "newValue": "Finance"
    }
  ]
}
```

Look at what you get. Not just the new value, but a `changes` array, and each change tells you the attribute name, what it was before, and what it is now. That is powerful. It means a mover workflow can say "only do something when the department actually changed, and only when it changed to Finance," because the before and after are right there in the data. This is why Identity Attributes Changed is the backbone of mover automations. Notice too that `changes` is an array. More than one attribute can change at once, so the array can hold several entries, and your logic has to look through it rather than assume the thing you care about is the first item. We will handle exactly that kind of array reading in Module 06.

Reach for Attributes Changed when the automation is about transitions: department moves, title changes, a manager reassignment, a lifecycle-relevant attribute flipping.

Priya's move also gives us the filter we will lean on later. If Acme only cares about people moving into Finance, you narrow this trigger with a filter such as `$.changes[?(@.attribute == "department" && @.newValue == "Finance")]`, so the workflow starts only for that specific transition rather than on every attribute change. Hold that expression loosely for now. The filter section later in this module explains why a small mistake in it fails in complete silence.

### Lifecycle State Changed, and Identity Deleted, the leaver

When Priya leaves Acme, there is not one single "leaver" trigger, and the choice between the options is a real piece of engineering judgment, so let us slow down here.

The moment you almost always want is Identity Lifecycle State Changed, which you will often see written in its shorter form, Lifecycle State Changed. When HR marks Priya as terminated, her identity's lifecycle state flips, for example from active to inactive, and this trigger fires. The important thing is that her identity still exists at this point, which is exactly what you need, because you still have all her data in hand while you send the offboarding notice, open the revoke-access ticket, and let her manager know. The seed carries her identity along with the state she moved from and the state she moved to, so your logic can react to the specific transition, for instance acting only when the new state is the terminated one. There is a close partner, Identity Lifecycle State Change Processed, which fires after ISC has finished processing the lifecycle state change and evaluating or applying the actions configured for that state change. Reach for that one when you need to react after lifecycle processing is complete. Do not treat the trigger itself as proof that every downstream target-system access change completed successfully.

Then there is Identity Deleted, and here is the trap. It fires when the identity record is removed from ISC entirely, which usually happens well after the person has gone, once they drop out of the authoritative source. Its seed looks almost the same as the joiner's:

```json
{
  "identity": {
    "type": "IDENTITY",
    "id": "2c91808568c529c60168cca6f90c1313",
    "name": "priya.patel"
  },
  "attributes": {
    "firstname": "Priya"
  }
}
```

Identity-related triggers identify the subject, but their event-specific data is not one shared schema. Identity Created and Identity Deleted provide attributes, Identity Attributes Changed provides a `changes` array, and lifecycle-state triggers provide their own state-specific data. That difference is exactly why you should inspect the trigger payload instead of carrying one assumed shape across the whole identity family. The timing of Identity Deleted is the other key point. If you build offboarding on Identity Deleted, you will act too late, because by then the identity and much of its context are already gone. So hold this rule of thumb: use Identity Lifecycle State Changed to drive timely offboarding, use Identity Lifecycle State Change Processed when you need to react after ISC has processed the lifecycle state change and its configured actions, and treat Identity Deleted as a signal for final housekeeping and audit, not for timely access removal.

One honest note on exact fields. The lifecycle-state fields are the kind of detail that can shift between versions, so before you write a filter against "the new state," open that trigger in the builder and read its own JSON rather than trusting your memory of the field name. That habit, checking the trigger's real seed in the builder, is worth building now and will save you across every trigger you ever use.

> **Work It Out**
>
> Acme wants Priya's access revoked promptly when she is terminated. An engineer builds the offboarding workflow on the Identity Deleted trigger. In testing against a real termination, the workflow does not run until days later, long after her access should have been removed. What trigger should this be, and why did Identity Deleted behave this way?
>
> <details>
> <summary>Check your answer</summary>
>
> Identity Deleted fires only when the identity record is removed from ISC entirely, which usually happens well after the person leaves, once they drop out of the authoritative source. That is far too late for timely access removal. Build timely offboarding on Identity Lifecycle State Changed, which fires when the state flips to terminated while the identity and its data still exist. Reach for Identity Lifecycle State Change Processed when you need to act after ISC has finished processing the state change and its configured actions, and treat Identity Deleted as a signal for final housekeeping and audit, not for revoking access.
>
> </details>

### Scheduled Trigger, the clock

Not everything reacts to an event. Sometimes the event is simply "it is Monday at nine." A Scheduled Trigger runs your workflow on a time schedule you set, once a day, every hour, weekly, and so on. There is no person and no identity in the seed, because nothing happened to anyone. The workflow starts because the clock said so, and then it goes and gathers whatever data it needs by itself.

Reach for a Scheduled Trigger for anything periodic: a weekly report, a nightly data-quality sweep, a monthly evidence pull for auditors. The mental shift from the event triggers is important. Event triggers are handed their subject. Scheduled workflows have to go find their subject. That shapes how you build them.

There is a close cousin called Scheduled Search. Instead of firing purely on time, it runs a saved search on a schedule and starts the workflow with the results. Reach for that when the periodic question is "which identities or accounts match this search right now," for example "everyone still missing a manager."

### Access Request Submitted, joining the request flow

When someone asks for access in ISC, that submission can start a workflow. The seed carries the request: who asked, for what, for whom. This is how you weave extra logic into the access request process, for example enriching a request with context, notifying an owner, or opening a record in another system when a particular kind of access is requested.

There is a partner trigger, Access Request Decision, that fires when a request is approved or denied rather than when it is submitted. Reach for Submitted to react at the start of a request, and Decision to react to the outcome. Knowing which end of the flow you care about is the whole choice.

### External Trigger, the door for other systems

Everything so far started inside ISC. The External Trigger is the way something outside ISC starts a workflow, by calling a URL that ISC gives you. Your HR system, a custom app, a script, any system that can make a web request can hand ISC a piece of JSON and set a workflow running. The seed is whatever that caller sends.

Reach for the External Trigger when the real world event lives in another system and you want ISC to react to it. It is the inbound counterpart to the HTTP Request action from Module 04, which is how a workflow reaches out. One is other systems calling you, the other is you calling them.

### Account Aggregation Completed, the operations workhorse

Not every trigger you use every day is about a person. One of the most common workflows teams build is "tell me when an aggregation breaks," and this is the trigger for it. Account Aggregation Completed fires each time an aggregation finishes, and the key detail is that it fires whether the aggregation succeeded or failed. Its seed tells you which, and gives you the numbers behind the run:

```json
{
  "source": {
    "type": "SOURCE",
    "id": "2c91808568c529c60168cca6f90c1313",
    "name": "Acme Active Directory"
  },
  "status": "Error",
  "started": "2020-06-29T22:01:50.474Z",
  "completed": "2020-06-29T22:02:04.090Z",
  "errors": ["Accounts unable to be aggregated."],
  "warnings": ["Account Skipped"],
  "stats": {
    "scanned": 200,
    "unchanged": 190,
    "changed": 6,
    "added": 4,
    "removed": 3
  }
}
```

The `status` is the field you build on. A run that connects and collects reports `Success`, and a run that fails reports `Error`, with the `errors` array carrying the detail. So the classic failure alert is a workflow on this trigger with a filter that lets it run only on failures:

```
$[?(@.status == "Error")]
```

That filter matters more than it looks, and it ties straight back to the filter lesson coming up. Because this trigger fires on every aggregation, a workflow with no filter runs on every successful aggregation too, which floods you with noise for the exact events you did not care about. The filter is what turns a firehose into a clean "only tell me when something broke."

The `stats` open a second, richer kind of automation once you are comfortable. Even on a `Success`, a sudden jump in `removed` accounts can mean a source misconfigured or a feed went wrong, so a more advanced workflow might inspect the numbers and raise a flag when they look off. Reach for Account Aggregation Completed whenever you want ISC to watch its own health and tell a human when attention is needed.

## A map of the rest, grouped by the job

Here is the long tail, organized by the kind of moment each one reacts to. You do not need to memorize these. You need to know they exist and roughly where to look, so that when a task appears you can say "that sounds like an aggregation trigger" and go read the details. For the exact seed of any trigger, the builder shows you the JSON each one provides, and the official triggers documentation lists them all.

Identity lifecycle. The joiner, mover, and leaver triggers we covered above, Identity Created, Identity Attributes Changed, Lifecycle State Changed and its Processed companion, and Identity Deleted, do most identity-lifecycle work. The remaining member of the family is the Machine Identity set, Created, Updated, and Deleted, for non-human identities such as service accounts. Reach here when the subject is a machine identity rather than a person.

Accounts and native change. Account Created, Updated, and Deleted react to account-level events on your sources. The Native Change set, Account Created, Updated, and Deleted, reacts specifically to changes made directly on the target system outside of ISC, which is the heart of detecting unauthorized change. Account Inactivity Detected fires when an account has gone unused for a threshold number of days. Reach here when the subject is an account rather than the whole identity.

Aggregation and provisioning. We covered Account Aggregation Completed above, since the failure alert is such a common build. Its neighbors are Accounts Collected for Aggregation, which fires a step earlier once accounts are gathered and ready, and Provisioning Completed, which fires when a provisioning operation finishes. Reach here to react to the plumbing of ISC itself.

Access request and certification. Alongside Access Request Submitted and Decision, the certification family includes Campaign Activated, Campaign Generated, Campaign Ended, and Certification Signed Off. Reach here to automate around reviews and requests, for example notifying reviewers when a campaign activates or filing evidence when one is signed off.

Sources and platform. Source Created, Updated, and Deleted react to changes to your sources. VA Cluster Status Change Event reacts to the health of a virtual appliance cluster. Reach here for administrative and operational awareness rather than identity events.

Interactive and form. The Form Submitted trigger starts a workflow when someone submits a form, and the interactive triggers support workflows that pause for human input. These pair with the Forms material in Module 05, so we will treat them properly there.

Licensed or feature-dependent. Some triggers only appear if your tenant has the matching capability. CAEP triggers react to shared-signal security events such as a credential change or a session revocation. CIEM triggers react to cloud infrastructure entitlement events. DAS Activity Alert reacts to data access security alerts. Outlier Detected fires when an identity's access looks anomalous. Reach here for security-driven automation, and know that if you do not see one of these in your builder, the likely reason is that the feature is not licensed in that tenant rather than that you did something wrong.

## Trigger filters, and the failure they cause

Now the section that saves you real pain. A trigger fires for a whole category of events. A filter narrows that to the ones you care about. You type a JSONPath expression into the Filter field on the trigger, and the rule is simple and strict: if the expression returns something, the workflow runs; if it returns nothing, the workflow stays asleep for that event.

The documentation gives filter examples you can rely on, such as firing only when an account has been inactive long enough:

```
$[?(@.trigger.daysInactive > 180)]
```

or firing only for events that carry a particular field:

```
$[?(@.sourceID)]
```

The exact fields you reference come from that trigger's own seed, the same JSON we keep reading. So a filter always answers the question "given the data this event handed me, is this one of the events I actually care about."

You might notice that the first example reaches through a "trigger" segment while the second does not. That is not a typo. Triggers present their data a little differently from one another, so the fields you can filter on are whatever that specific trigger puts in its own payload, not one fixed shape shared by all of them. The habit that keeps you safe is the same as always: open the trigger's own JSON in the builder and test the filter, rather than trusting how it reads on the page.

Here is where people lose an afternoon, so I want you to see it now. Filters fail silently. If you write a filter that is slightly wrong, points at a field that is not there, misspells an attribute, compares against the wrong value, the expression simply returns nothing, and the workflow does exactly what it is supposed to do when nothing matches: it does not run. No error appears. No history entry shows up, because from the platform's point of view there was nothing to do. You sit there certain the workflow is broken, when in truth the workflow never got the go-ahead to start.

So build the habit early. When a workflow "does not fire," suspect the filter first. Loosen it or remove it and test again. If the workflow suddenly runs, your filter was the gate that was quietly turning every event away. This one instinct will make you look like you have been doing this for years.

> **Work It Out**
>
> You build a mover workflow to alert on moves into Finance, with the filter `$.changes[?(@.attribute == "department" && @.newValue == "Finance")]`. Priya moves to Finance, but the workflow never runs and no execution appears. Name the first thing to suspect, and two concrete things you would check.
>
> <details>
> <summary>Check your answer</summary>
>
> Suspect the filter first, because a filter that matches nothing turns the event away with no error and no execution record. Two things to check: whether the real payload stores the department value with the exact case you wrote, since the data may hold "finance" rather than "Finance", and whether the attribute name and path match the trigger's own seed rather than your memory of it. Loosen or remove the filter and test again. If the workflow then runs, the filter was the silent gate.
>
> </details>

One more note to file away. The path language inside a trigger filter comes from a slightly different engine than the paths your steps use to read data later. They look almost the same and mostly behave the same, which is why I am only flagging it here. Module 06 explains the difference and when it bites. For now, treat "the path in a filter" as a close cousin of "the path in a step," and always test a filter rather than trusting that it reads correctly in English.

## Choosing your starting point

Most of trigger selection comes down to three questions, asked in order.

Did a specific thing happen to a specific identity, account, or request? Then you want an event trigger, and you pick the one whose seed already carries what you need. Priya being hired, Priya moving to Finance, a request being submitted. Prefer the event that hands you the most of the data you will use.

Is the automation periodic, tied to time rather than to any single event? Then you want a Scheduled Trigger, or a Scheduled Search if the periodic question is really "which things match this search right now." Remember that scheduled workflows have to go find their subject, since none is handed to them.

Does the originating event live in another system entirely? Then you want the External Trigger, so that system can call ISC and start the workflow with its own data.

And keep in mind the relationship we drew in Module 00. A workflow is the managed, no-code way to react to an ISC event. If your need is genuinely to have your own external service receive raw events and handle them in your own code, a direct event trigger subscription may fit better than a workflow. Same underlying events, different amount of control and effort. Module 09 turns this into a full decision framework.

## Before you move on

Take Priya through her three big moments and name the trigger for each. On her first day, which trigger, and what one field in its seed would you read to greet her by name? When she moves to Finance, which trigger, and which part of the seed tells you both that the department changed and what it changed from and to? When she leaves, which trigger drives a timely offboarding, and why would building that on Identity Deleted make you act too late? Then one for judgment beyond the three: if Acme's HR system wants to tell ISC the moment a resignation is filed, before anything changes inside ISC at all, which trigger fits, and why would an event trigger inside ISC not be the right choice for that one? If those answers come easily, you understand triggers well enough to move on to Module 03, where we start making decisions and shaping data with operators.

---
[← Previous: Module 01 The Workflow Model](01-the-workflow-model.md) | [Course home](../README.md) | [Next: Module 03 Operators and Logic →](03-operators-and-logic.md)
