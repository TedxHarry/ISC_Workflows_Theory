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

> **Work It Out**
>
> Acme's onboarding workflow runs on Identity Created. It emails the new hire's manager and expects the person to already have their birthright access. In production, some runs email nothing useful because the manager attribute is empty, and on other runs the person does not yet have the access the message claims. What two assumptions is this workflow making that it should not, and how would you handle each?
>
> <details>
> <summary>Check your answer</summary>
>
> First, it assumes every configured attribute holds a usable value. The payload carries the attributes mapped in the identity profile, but an optional attribute such as manager is not guaranteed to contain a usable, non-null value, so validate the fields the message depends on and fetch or branch deliberately when one is not usable rather than sending an empty value. Second, it assumes the identity is already in the lifecycle state the process requires. Lifecycle state is configuration-dependent: it is determined by the mapped lifecycle-state attribute, which is often calculated from a hire date, so a new identity may be created directly as active or first as pre-hire. So do not assume Identity Created means the person is already active or fully provisioned. Check the lifecycle state the identity carries. If the tenant creates joiners directly as active, Identity Created can drive the active Joiner process, filtering on the lifecycle-state attribute in that event. If the tenant first assigns pre-hire and later transitions the identity to active, use Identity Lifecycle State Changed for that later transition. Which pattern applies depends on the tenant's lifecycle-state mapping and processing design.
>
> </details>

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

The moment you almost always want is Identity Lifecycle State Changed, which you will often see written in its shorter form, Lifecycle State Changed. When HR marks Priya as terminated, her identity's lifecycle state flips, for example from active to inactive, and this trigger fires. The important thing is that her identity still exists at this point and can still be looked up, which is exactly what you need while you send the offboarding notice, open the revoke-access ticket, and let her manager know. The seed carries her identity along with the state she moved from and the state she moved to, so your logic can react to the specific transition, for instance acting only when the new state is the terminated one. A representative leaver event has this shape:

```json
{
  "identity": {
    "id": "2c9180835d191a86015d28455b4b232a",
    "name": "priya.patel",
    "type": "IDENTITY"
  },
  "oldLifecycleState": "active",
  "newLifecycleState": "terminated"
}
```

The exact lifecycle-state values are whatever your tenant configures, so confirm them in the builder rather than assuming these names. Notice too that this seed carries the identity reference and the state transition, not her full attribute set, so if the offboarding notice, the ticket, or an external action needs more identity data, fetch the current identity data with Get Identity. There is a close partner, Identity Lifecycle State Change Processed, which fires after ISC has finished processing the lifecycle state change and evaluating or applying the actions configured for that state change. Reach for that one when you need to react after lifecycle processing is complete. Do not treat the trigger itself as proof that every downstream target-system access change completed successfully.

Then there is Identity Deleted, and here is the trap. It fires when the identity itself is deleted from Identity Security Cloud. That is different from an employment termination or a lifecycle-state transition, so it is not the trigger to rely on for timely offboarding. Source accounts can still exist after the ISC identity is deleted, but they are no longer correlated to that identity. Its seed looks almost the same as the joiner's:

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
> Acme wants Priya's access revoked promptly when she is terminated. An engineer builds the offboarding workflow on the Identity Deleted trigger, expecting it to fire when Priya is terminated, but it does not drive her access removal in time. What trigger should this be, and why is Identity Deleted the wrong choice?
>
> <details>
> <summary>Check your answer</summary>
>
> Identity Deleted represents deletion of the ISC identity itself, not the employment termination or the lifecycle-state transition, so it is not the right trigger for timely offboarding. After an identity is deleted, its source accounts may still exist but no longer correlate to an identity. Build timely offboarding on Identity Lifecycle State Changed, which fires when the state flips to a leaver state while the identity and its data still exist. Reach for Identity Lifecycle State Change Processed when you need to act after ISC has evaluated and applied the actions configured for that lifecycle state, remembering that Processed still is not proof that every downstream target-system change has finished.
>
> </details>

### Scheduled Trigger, the clock

Not everything reacts to an event. Sometimes the event is simply "it is Monday at nine." A Scheduled Trigger runs your workflow on a time schedule you set, once a day, every hour, weekly, and so on. There is no person and no identity in the seed, because nothing happened to anyone. The workflow starts because the clock said so, and then it goes and gathers whatever data it needs by itself.

Reach for a Scheduled Trigger for anything periodic: a weekly report, a nightly data-quality sweep, a monthly evidence pull for auditors. The mental shift from the event triggers is important. Event triggers are handed their subject. Scheduled workflows have to go find their subject. That shapes how you build them.

There is a close cousin called Scheduled Search. Instead of firing purely on time, it runs a saved search on a schedule and starts the workflow with the results. Reach for that when the periodic question is "which identities or accounts match this search right now," for example "everyone still missing a manager."

### Access Request Submitted, joining the governed approval flow

Access Request Submitted is not a generic "any access request happened" trigger. In native Workflows it participates in Adaptive Approval. It fires when an access request is submitted for an access item whose Approval Type points to that enabled Workflow. A request for an item using ordinary reviewer configuration, or an item that does not route approval through that Workflow, does not start this Workflow. This trigger also requires the Access Request service.

The current Workflow sample is detailed. The excerpt below keeps the fields most useful for day-to-day reasoning while preserving their documented names and types:

```json
{
  "requestId": "...",
  "workflowId": "...",
  "parentWorkflowExecutionId": "...",
  "workflowExecutionId": "...",
  "accessRequestId": "...",
  "accountActivityId": "...",
  "requestedItem": {
    "id": "...",
    "name": "Engineering Access",
    "description": "Engineering Access",
    "type": "ACCESS_PROFILE",
    "operation": "Add",
    "reauthRequired": true,
    "requestedAccounts": []
  },
  "requestedBy": {
    "id": "...",
    "name": "Adam Admin",
    "type": "IDENTITY"
  },
  "requestedFor": {
    "id": "...",
    "name": "annie",
    "type": "IDENTITY"
  },
  "sod": {
    "violated": "true",
    "details": {}
  },
  "requestedAt": "2009-11-10T23:00:00Z"
}
```

Read `requestedItem` closely. It is singular and represents the access item carried by this event, not a whole shopping-cart array. SailPoint also documents that items in a larger request can be processed and provisioned individually, so do not treat a multi-item Request Center submission as one atomic object. At the same time, do not turn the singular payload into an undocumented guarantee of exactly one Workflow execution per basket item. If exact fan-out matters, validate it against real tenant executions.

Notice two type and value lessons. The current Workflow sample shows `requestedItem.operation` as `"Add"`. Treat that as a sample value, not a complete enum unless current documentation defines the full set. And `sod.violated` is shown as the string `"true"`, not a JSON boolean. Inspect real execution input before writing comparisons.

There is a partner native Workflow trigger, Access Request Decision. It marks a different lifecycle boundary: the final approved or denied decision. When multiple approval decisions are required, SailPoint documents that this trigger fires after the final decision, once the final approved or denied outcome is known. A representative excerpt is:

```json
{
  "accessRequestId": "...",
  "requestedBy": {
    "id": "...",
    "name": "Adam Admin",
    "type": "IDENTITY"
  },
  "requestedFor": {
    "id": "...",
    "name": "Ed Engineer",
    "type": "IDENTITY"
  },
  "requestedItemsStatus": [
    {
      "approvalInfo": [
        {
          "approvalComment": "...",
          "approvalDecision": "APPROVED",
          "approver": {
            "id": "...",
            "name": "Stephen Austin",
            "type": "IDENTITY"
          },
          "approverName": "Stephen.Austin"
        }
      ],
      "id": "...",
      "name": "Engineering Access",
      "operation": "Add",
      "type": "ACCESS_PROFILE"
    }
  ]
}
```

Some SailPoint Developer Event Trigger pages use approval-only shorthand when describing Access Request Decision, while the current native Workflow trigger documentation defines the final outcome as approved or denied. For native Workflow design, follow the native Workflow trigger contract.

So Submitted and Decision are different boundaries. Use Access Request Submitted to begin the configured Adaptive Approval workflow. Use Approval Policy inside that workflow to conduct the governed review. Use Access Request Decision when a separate workflow needs to react to the final outcome. Do not invent an Access Request Completed Workflow trigger.

For an approved request that proceeds to fulfillment, provisioning is a later boundary again. The native Workflow trigger is Provisioning Completed, documented as firing when a provisioning action completes on a source. A representative excerpt is:

```json
{
  "trackingNumber": "...",
  "action": "IdentityRefresh",
  "requester": {
    "id": "...",
    "name": "Adam Admin",
    "type": "IDENTITY"
  },
  "recipient": {
    "id": "...",
    "name": "Ed Engineer",
    "type": "IDENTITY"
  },
  "errors": [],
  "warnings": [],
  "sources": "Corp AD",
  "accountRequests": [
    {
      "source": {
        "id": "...",
        "name": "Corporate Active Directory",
        "type": "SOURCE"
      },
      "accountId": "...",
      "accountOperation": "Modify",
      "provisioningResult": "committed",
      "provisioningTarget": "Corp AD",
      "attributeRequests": [
        {
          "operation": "Add",
          "attributeName": "memberOf",
          "attributeValue": "..."
        }
      ]
    }
  ]
}
```

Treat Provisioning Completed as evidence about ISC's provisioning stage, not as an independent readback from the target application. If the business requires proof that access is actually live and usable on the target, verify that state separately.

There is also a real documentation conflict in `provisioningResult`. The current Workflow trigger sample uses `"committed"`, while SailPoint's current Developer Provisioning Completed event-trigger page uses `"SUCCESS"` in its sample. Do not normalize that conflict into one universal literal. Inspect the payload your tenant actually produces before you filter on this field.

For request-lifecycle investigation outside Workflow executions, SailPoint Search audit events include Request Access Started, Request Access Approved, Request Access Rejected, Request Access Cancelled, Request Access Escalated, and Request Access Processed. SailPoint documents Request Access Processed as the event for actual provisioning of the requested item. These Search audit event names are observability evidence, not native Workflow trigger names. Do not turn Request Access Processed into an invented Access Request Completed Workflow trigger.

One final naming trap: SailPoint Developer Event Triggers are a separate extensibility surface from native Workflow triggers. A Developer Event Trigger can use the same or similar display name, including Access Request Submitted, while having a different payload and contract. Do not copy a Developer Event Trigger payload into a native Workflow design. Likewise, do not teach Access Request Dynamic Approval as a native Workflow trigger unless the current Workflow builder or catalog lists it.

> **Work It Out**
>
> Acme has two sensitive Finance access profiles. Finance Reporting is configured to use an enabled Workflow as its Approval Type. Finance Admin uses the normal reviewer configuration instead. Requests for Finance Reporting start the Access Request Submitted workflow, while requests for Finance Admin do not. A colleague insists the trigger should fire for both because both are access requests. What is the colleague misunderstanding?
>
> <details>
> <summary>Check your answer</summary>
>
> The colleague is treating Access Request Submitted as a generic event for every access request. It is not. In native Workflows, this trigger is part of Adaptive Approval and fires when the requested access item routes approval to that enabled Workflow. Finance Reporting is wired to the Workflow, so its request starts it. Finance Admin is not, so its request follows its configured reviewer path instead. Check the access item's Approval Type when this trigger does not start, and remember that the trigger seed is item-oriented rather than a whole-basket payload.
>
> </details>

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

The `status` is the field you build on, and it is also a place where SailPoint's own materials currently disagree, which is worth seeing now. The trigger-specific guide documents two values, `Success` and `Error`, while the current generated trigger model exposes `Success`, `Failed`, and `Terminated`, and the trigger catalog describes the event as firing after an aggregation completed, terminated, or failed. So do not hard-code one non-success value as if it were the only one. When the requirement is simply to alert on any outcome that is not a clean success, a defensive filter is:

```
$[?($.status != "Success")]
```

That expression catches whatever non-success value the event actually carries, rather than betting on a single spelling. Inspect the real event your tenant delivers and validate the filter against that payload with SailPoint's trigger-filter tooling before you rely on it.

That filter matters more than it looks, and it ties straight back to the filter lesson coming up. Because this trigger fires on every aggregation, a workflow with no filter runs on every successful aggregation too, which floods you with noise for the exact events you did not care about. The filter is what turns a firehose into a clean "only tell me when something broke."

The `stats` open a second, richer kind of automation once you are comfortable. Even on a `Success`, a sudden jump in `removed` accounts can mean a source misconfigured or a feed went wrong, so a more advanced workflow might inspect the numbers and raise a flag when they look off. Reach for Account Aggregation Completed whenever you want ISC to watch its own health and tell a human when attention is needed.

> **Work It Out**
>
> Acme builds an aggregation-failure alert on Account Aggregation Completed so the source team hears about broken aggregations. The team reports two problems: the channel is noisy with messages about healthy runs, and a run that carried warnings was not surfaced for review. What is happening, and how would you fix each?
>
> <details>
> <summary>Check your answer</summary>
>
> The noise comes from a missing or wrong filter. The trigger fires on every aggregation, including successful ones, so without a filter the workflow runs on healthy runs too. Filter for the outcomes you care about, and when the requirement is any non-success outcome, `$[?($.status != "Success")]` is a defensive choice, because SailPoint's own materials currently disagree on the exact non-success value and this catches whatever the event actually carries. Validate it against your tenant's real trigger payload first. The missing warning is a different issue. Warnings are reported in a separate `warnings` array, and SailPoint's documented sample shows that an event with `status` set to `Success` can still contain warnings, so a status-only filter does not necessarily capture every condition the team wants to review. If warnings matter, start more broadly and inspect the `warnings` array inside, or design a separate check, rather than assuming the status field captures every run worth a human's attention.
>
> </details>

### Native Change Account triggers, when the target changed first

Native Change is the pattern for target-system drift. Someone or something changes an account directly on the source, outside ISC control, and ISC discovers that difference during account aggregation by comparing what it had stored with what it just read from the source.

That timing is the first boundary to understand. Native Change is not instant target telemetry. The workflow starts after aggregation detects the out-of-band change, and only for sources where Native Change Detection is enabled, the relevant account operation is monitored, and at least one monitored attribute participates in the detected change. After you enable it on a source, you must run an aggregation before ISC can discover native changes.

The exact native Workflow trigger names are:

- Native Change Account Created
- Native Change Account Updated
- Native Change Account Deleted

Those names are close to the ordinary Account Created, Account Updated, and Account Deleted triggers, but they are not the same boundary. Ordinary account events fire when an account is created, updated, or deleted in ISC, and the Developer examples show a cause such as aggregation or provisioning. Native Change Account events are narrower: they represent account changes made outside ISC and then detected by aggregation on a source configured for Native Change Detection.

Picture Priya again. A directory administrator adds her AD account directly to a sensitive Finance group. That change bypasses request approval in ISC, so the workflow you want is not a mover workflow and not an access-request workflow. It is Native Change Account Updated, because the account already existed and the direct target change added an entitlement.

The seed is account-centered. A representative updated event looks like this:

```json
{
  "identity": {
    "id": "2c91808978eb9fab0178fb8ca6d308fb",
    "name": "priya.patel",
    "type": "IDENTITY",
    "email": "priya.patel@acme.com",
    "manager": {
      "id": "2c91808378eb9fa30178fb8caf90097f",
      "name": "Rina Shah",
      "type": "IDENTITY",
      "email": "rina.shah@acme.com"
    }
  },
  "source": {
    "id": "2c91808a78efc63e0178fb8624b248c5",
    "name": "Acme Active Directory",
    "type": "SOURCE",
    "owner": {
      "id": "2c9180867a7c46d0017a7ca099d50531",
      "name": "AD Source Owner",
      "type": "IDENTITY",
      "email": "ad.owner@acme.com"
    }
  },
  "account": {
    "id": "2c91808378eb9fa30178fb9481a30afa",
    "name": "priya.patel",
    "type": "ACCOUNT",
    "uuid": "{08ee6c6d-7d02-4978-9417-d92ba6a5ed50}",
    "correlated": true,
    "nativeIdentity": "CN=Priya Patel,OU=Users,DC=acme,DC=com"
  },
  "eventType": "ACCOUNT_UPDATED",
  "accountChangeTypes": [
    "ENTITLEMENTS_ADDED"
  ],
  "entitlementChanges": [
    {
      "attributeName": "memberOf",
      "added": [
        {
          "id": "2c91808978eb9fab0178fb9482620b71",
          "name": "Finance Privileged Operators",
          "value": "CN=Finance Privileged Operators,OU=Groups,DC=acme,DC=com",
          "owner": null
        }
      ],
      "removed": []
    }
  ],
  "singleValueAttributeChanges": [],
  "multiValueAttributeChanges": []
}
```

Read the lists instead of guessing. `accountChangeTypes` tells you what kind of change was present. `entitlementChanges` gives added and removed entitlement objects by account attribute, such as `memberOf`. `singleValueAttributeChanges` records one-value account attributes with `oldValue` and `newValue`. `multiValueAttributeChanges` records non-entitlement multi-value account attributes with `addedValues` and `removedValues`. The `account` object tells you what ISC currently knows about the account, and `nativeIdentity` is the target account identifier you will usually need in an alert.

The created, updated, and deleted events differ in useful ways:

- Native Change Account Created uses `eventType` `ACCOUNT_CREATED`. Its single-value account attributes have `oldValue` set to `null`, and entitlement changes have added values while `removed` is empty.
- Native Change Account Updated uses `eventType` `ACCOUNT_UPDATED`. It includes only the changed account attributes for the monitored configuration, and entitlement changes can include additions, removals, or both.
- Native Change Account Deleted uses `eventType` `ACCOUNT_DELETED`. Its single-value account attributes have `newValue` set to `null`, and entitlement changes have removed values while `added` is empty.

There is one identity lesson that matters a lot in incidents. Native Change events fire for correlated and uncorrelated accounts. If `account.correlated` is `false`, the `identity` in the payload is a system-generated identity, not the real human identity. SailPoint documents that this system-generated identity can still be used in API requests that require an identity ID, including entitlement revocation, but you should not message that as "Priya changed" or route it as though a human identity was proven. Your alert should say the account is uncorrelated and include the source and native identity so the source owner can investigate.

For source configuration, keep the AND relationship in your head. If Acme enables Native Change Detection for Account Updates and selects only the `memberOf` entitlement attribute, then ISC is looking for updated accounts where that monitored entitlement attribute changed. If the same administrator changes only an unmonitored telephone number, this workflow should not start. That is not a broken workflow. It is the configured scope doing what it was told to do.

Source support is part of the design too. SailPoint documents that Native Change Detection is not available for Non-Employee Lifecycle Management sources, and SAML Just-in-Time sources must be enabled through the Native Change Detection API endpoint. If the source does not expose the configuration you expect, verify the source's supported path before you blame the workflow trigger.

The safe first workflow is notify-only:

```
Native Change Account Updated
        |
        v
Check source and accountChangeTypes
        |
        v
Read entitlementChanges for sensitive additions
        |
        +---- matched     -> notify Security and the source owner
        |
        +---- not matched -> success, no action needed
```

Remediation is documented, but it is a design decision, not a reflex. SailPoint provides templates that revoke entitlement additions detected by Native Change Account Created or Updated, and those templates send a summary email to the source owner. That proves the product supports remediation workflows for native changes. It does not prove every native change should be auto-reverted. Direct target changes can be emergency fixes, break-glass access, source-owner maintenance, or real unauthorized drift. If you revoke automatically, test with dangerous steps simulated, use valid entitlement IDs, and make the action safe to repeat.

> **Work It Out**
>
> Priya's AD account is added directly to `Finance Privileged Operators`. The Native Change Account Updated event arrives with `account.correlated` set to `true`, `accountChangeTypes` containing `ENTITLEMENTS_ADDED`, and an added `memberOf` entitlement named `Finance Privileged Operators`. What does the workflow know, what does it not know, and what is the safest first response?
>
> <details>
> <summary>Check your answer</summary>
>
> It knows aggregation detected an out-of-band update to Priya's correlated account on the configured source, and the payload identifies the added entitlement, the account, the source, and the correlated identity context. It does not know that the change was malicious, and it does not prove the change came from a specific human administrator unless another system supplies that evidence. The safest first response is to alert Security and the source owner with the source, native identity, account id, changed entitlement, and correlation state. Auto-revert is a separate decision. Use it only when the business rule is clear, the entitlement id is valid, the target effect is understood, and repeat execution will not create a loop or undo an approved emergency action.
>
> </details>

## A map of the rest, grouped by the job

Here is the long tail, organized by the kind of moment each one reacts to. You do not need to memorize these. You need to know they exist and roughly where to look, so that when a task appears you can say "that sounds like an aggregation trigger" and go read the details. For the exact seed of any trigger, the builder shows you the JSON each one provides, and the official triggers documentation lists them all.

Identity lifecycle. The joiner, mover, and leaver triggers we covered above, Identity Created, Identity Attributes Changed, Lifecycle State Changed and its Processed companion, and Identity Deleted, do most identity-lifecycle work. The remaining member of the family is the Machine Identity set, Created, Updated, and Deleted, for non-human identities such as service accounts. Reach here when the subject is a machine identity rather than a person.

Accounts. Account Created, Updated, and Deleted react to account-level events on your sources. As you just saw, the Native Change Account Created, Updated, and Deleted triggers are the drift-detection version of that account family, for changes made outside ISC and discovered during aggregation. Account Inactivity Detected fires when an account has gone unused for a threshold number of days. Reach here when the subject is an account rather than the whole identity.

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
