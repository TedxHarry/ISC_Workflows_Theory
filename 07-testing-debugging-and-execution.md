# Module 07: Testing, Debugging, and Execution

How to test a workflow safely, and how to read exactly what happened when one runs.

You can now build a workflow. This module is about the two skills that separate someone who builds workflows from someone who runs them in production without fear: testing without causing harm, and reading a failure calmly enough to fix it. A confident engineer is not one whose workflows never fail. Everything fails eventually. A confident engineer is one who can prove a workflow works before trusting it, and who can look at a broken run and know where to look first.

We will start with the single most important safety lesson in the whole course, because getting it wrong causes real damage to real people.

## Testing that does not hurt anyone

Here is the sentence I most want you to remember from this module. The ordinary Test Workflow button runs enabled steps for real. It is not automatically a harmless rehearsal. When you test, enabled actions can really send emails, create campaigns, change access, or act on live identities. So before you press test, know which steps are allowed to execute and which must be simulated.

There are two safety layers you will usually combine.

The first is Simulated Testing. It lets you run the workflow using test input while controlling which steps actually execute. The Enable Step toggle on each step determines whether that step runs for real during the test. A disabled step uses simulated behavior instead of performing its real-world action. So to test Priya's offboarding safely, you can disable the Manage Access step while still exercising the surrounding logic and branches.

The second is a sandbox tenant. The safest place to test is a separate non-production tenant stocked with dummy identities, accounts, and access created for testing. Then even a step that runs for real touches nobody who matters. Best practice is to use a sandbox and still simulate the most dangerous world-changing steps when practical.

One more practical point about testing. The test panel provides sample input, but the ids and values must match objects that actually exist in your tenant if enabled steps depend on them. Real triggers hand real technical ids, so meaningful tests use input shaped like the real trigger payload and populated with values that make sense in the test tenant.

For a concrete example, a mover workflow that reacts to Priya moving into Finance can be tested with input shaped like its real trigger:

```json
{
  "identity": { "type": "IDENTITY", "id": "<SANDBOX_IDENTITY_ID>", "name": "workflow.test" },
  "changes": [
    { "attribute": "department", "oldValue": "Sales", "newValue": "Finance" }
  ]
}
```

Replace `<SANDBOX_IDENTITY_ID>` with the id of a dummy identity that actually exists in your sandbox, so any enabled step that looks the identity up finds a real test object rather than failing on an id that is not there.

## Reading what happened: the execution history

Every time a workflow runs, whether a test or a real event, it leaves an execution record. This is your black box recorder, and learning to read it is most of debugging.

Workflow execution details are available for up to 90 days. Current Workflow Executions API documentation also states that archived executions beyond that window return 404, so do not treat the API as a long-term archive. If your organization needs workflow evidence for longer than 90 days, export or retain that evidence somewhere outside the workflow execution history.

You read a run in layers, from the outside in.

The first layer is the status. Did this run complete, fail, get canceled, remain queued, or still run. When something is wrong, this immediately separates a workflow that started and then failed from one that never started at all.

The second layer is the step-by-step playback. Open a single execution and walk through the steps. The history shows the step input, step output, and the values that were actually available when the step ran. Rendered inline variables are especially useful because they show what an expression resolved to at runtime rather than only the expression you typed.

Let me make that concrete. Suppose Priya's welcome email went out looking wrong, greeting her as "Welcome to Acme, " with nothing after the comma. You open the run, find the Send Email step, and inspect its input. You might see:

```
Step Input
  recipients: priya.patel@acme.com
  subject: Welcome to Acme
  body: Welcome to Acme,
```

The body is blank exactly where the first name should be. That tells you the variable resolved to nothing. You then inspect the path and discover that you wrote `$.trigger.identity.firstname` when the field actually lives under `attributes`, so it should have been `$.trigger.attributes.firstname`. The history did not solve the bug for you, but it exposed the exact empty value that matters.

## A field guide to failures

Most workflow failures fall into a handful of shapes, and you have already met every one of them in earlier modules. Here they are gathered into a diagnostic order so that when something breaks you have a route to walk.

Start with the biggest question: did the workflow run at all? If there is no execution record for an event you expected, the workflow never started. The first suspect is often the trigger filter from Module 02. A filter that returns nothing can turn the event away without producing a workflow execution. Also check the simple causes: the workflow may be disabled, or workflows may have only recently been enabled in the tenant and still be inside the initial activation window from Module 00.

If the workflow did run but a step came up empty, you are looking at a JSONPath or missing-data problem from Modules 01 and 06. Open that step's real input and output. Check the nesting, case, and actual payload rather than guessing.

If an HTTP Request step failed, inspect the error and remember that HTTP Request has a 90 second timeout. The external system may have returned an error, exceeded that timeout, rate-limited the request, or returned data in a shape you did not plan for. Build an error path and read the error details rather than treating every HTTP failure as a workflow logic bug.

If a Manage Access step looks successful but the business outcome is incomplete, inspect `failedAccessRequests` as well as `successfulAccessRequests`. A Manage Access action can complete without automatically failing the entire workflow even when some requested access changes appear in `failedAccessRequests`. A green step is therefore not proof that every requested access item succeeded.

If a comparison sent the workflow down the wrong path, inspect the rendered values. This is often the case or type mismatch from Module 03. "Finance" and "finance" look equivalent to a person and can still compare differently.

If a step failed because of permission or authentication, the workflow tried to do something it was not allowed to do or a credential it depends on is wrong, unavailable, or expired. If an action timed out, check that specific action's documented timeout. Timeouts are action-specific: Get Identity is 1 minute, HTTP Request is 90 seconds, Manage Access is 30 minutes, and Manage Accounts is 1 hour. Do not debug with a fictional universal timeout in mind.

The method underneath all of these is the same. Read the status. Find the first step that failed or produced an unexpected value. Inspect the real input and output. Form one hypothesis. Fix one thing. Test again with dangerous steps simulated where appropriate. Debugging is not cleverness. It is disciplined observation.

> **Work It Out**
>
> A mover workflow is supposed to email Priya's new manager when she moves to Finance. The run looks successful, but the manager reports that no message arrived. Where do you look, and what is the likely cause?
>
> <details>
> <summary>Check your answer</summary>
>
> Open the execution and read the steps in order. On the step that fetches the manager, inspect its input and output to confirm it returned a manager with an email. Then open the Send Email step and inspect the rendered recipient. If that recipient rendered to nothing, the path pointed at a value that was not there, so the message had nowhere to go even though the run may look otherwise healthy. The common cause is reading the manager's email straight from the trigger, which carries only the manager's id and name, instead of fetching the manager with Get Identity and reading the email from that result. As Module 04 put it, green does not mean done, so inspect the step input and output rather than trusting the status alone.
>
> </details>

> **Work It Out**
>
> Priya's offboarding workflow ran and every step shows success, but a reviewer finds she still has access to a sensitive application the next day. Where do you look, and what are three likely explanations that a green run can hide?
>
> <details>
> <summary>Check your answer</summary>
>
> Open the execution and read the Manage Access step output, not just its status. Inspect both `successfulAccessRequests` and `failedAccessRequests`, because a Manage Access step can complete successfully while some requested removals are listed as failed, and the workflow is not automatically marked failed for that. Three common explanations behind a green run: the removal for that application is in `failedAccessRequests`; the removal request was accepted but is still awaiting an approval decision, because Manage Access continues after submitting an approval-required request rather than waiting for it; or the removal was accepted and any approval granted, but provisioning to the target had not finished when the reviewer checked. Green does not mean done, so verify the outputs and, where completion matters, confirm the target state rather than trusting the status. This is also a reason standard termination revocation is often better handled by a leaver lifecycle state that removes all access, where the removal approval is bypassed automatically.
>
> </details>

> **Work It Out**
>
> An aggregation-failure alert is supposed to message the source team when an aggregation fails. It never seems to fire, even though a source clearly failed to aggregate this morning. How do you tell whether it ran, and what are the most likely causes?
>
> <details>
> <summary>Check your answer</summary>
>
> Start with the status question: is there an execution record at all? If there is none, the workflow never started, and the first suspect is the trigger filter. A status filter that is slightly wrong, or that assumes the wrong non-success value, turns every event away in silence, and the workflow may also simply be disabled. Because SailPoint's materials currently differ on the non-success status values, a defensive filter such as `$[?($.status != "Success")]`, validated against your tenant's real payload, is less fragile than betting on one spelling. If instead there is a record but the wrong thing happened, open the run and read the trigger input, where `status` and `source.name` tell you which source failed and what status the event actually carried. Remember too that warnings are reported separately, and a `Success` event can still contain warnings, so a status-only filter may not capture a run that produced warnings the team would still want to see.
>
> </details>

> **Work It Out**
>
> A Joiner workflow fired for a new hire, and its status is green, but the onboarding email went to the team without the new hire's manager on it, and the manager's task was never created. In the execution history, where do you look, and what is the most likely cause given what an Identity Created event does and does not carry?
>
> <details>
> <summary>Check your answer</summary>
>
> Open the run and read the trigger input first. An Identity Created event carries the identity reference and the attributes mapped in the identity profile, but an optional attribute such as manager is not guaranteed to contain a usable, non-null value, for example when a usable manager relationship has not been established. Confirm in the step input whether the manager value is usable, then check whether the workflow validated it, fetched with Get Identity, or branched on the missing value. The green status only means the steps ran, not that the manager was found. The fix is to validate the manager attribute before use and take a deliberate path when it is not usable. Get Identity can retrieve the identity's current state, but it is a refresh of what ISC already knows, not a guarantee that missing source data now exists, so the workflow must still branch appropriately if manager remains null.
>
> </details>

## Debugging across the access-request boundaries

Access-request incidents become easier when you first identify which pattern created the execution. Adaptive Approval and Manage Access are related to the same request lifecycle, but they are not the same workflow pattern.

For an Adaptive Approval workflow started by Access Request Submitted:

1. Confirm the requested access item is configured to use the enabled Workflow as its Approval Type.
2. Inspect the trigger input and confirm `accessRequestId`, `requestedItem`, `requestedBy`, and `requestedFor`.
3. Inspect the Approval Policy configuration and output. This workflow is the approval process, so the approval step must reach a result before logic that branches on approved or rejected can continue.
4. Inspect the approval identifiers and result data, including `approvalId`, status, and approved or rejected information where the action documents it.
5. If the request was approved but the user still has no access, move to provisioning evidence. Approval is proven; fulfillment is not.

For a workflow that uses Manage Access to submit a new access request:

1. Inspect both `successfulAccessRequests` and `failedAccessRequests`, not just the green step status.
2. If approval is required, do not expect the final decision inside that Manage Access execution. The action submits the request and the workflow continues without waiting for approval.
3. Use a separate workflow on Access Request Decision when downstream logic needs the final approved or denied result.
4. If the incident is really "the access is still not live," inspect Provisioning Completed and provisioning or account activity, then confirm the target state itself when business certainty requires it.

The single question underneath both patterns is the same: which boundary has actually been proven, and which boundary am I only assuming? Submission, approval, provisioning completion, and access independently confirmed live on the target are different facts.

> **Work It Out**
>
> Priya requested a sensitive Finance access profile through Request Center. Its Approval Type points to an enabled Adaptive Approval workflow. The Access Request Submitted execution shows that the Approval Policy completed with an approved result, and the workflow ended successfully. A day later Priya still cannot use the Finance application. What does the green workflow prove, and where should you debug next?
>
> <details>
> <summary>Check your answer</summary>
>
> The green Adaptive Approval workflow proves that this approval workflow ran successfully and reached an approved business decision. It does not prove provisioning completed or that the Finance application reflects the access. Move to the provisioning boundary: inspect Provisioning Completed and the relevant provisioning or account activity for errors, warnings, account requests, and status. If the business needs certainty that the access is actually usable, verify the Finance target itself. Do not add Manage Access to this explanation, because the request already existed before Access Request Submitted fired and Approval Policy is the action governing that existing request.
>
> </details>

## Running it again, and the trap of the second run

Sooner or later a workflow will fail halfway through, and your instinct will be to run it again. Pause before you do, because this is where a careless fix makes things worse.

Think about what already happened before the failure. Suppose Priya's onboarding workflow created an account, opened a ticket, and then failed at the next step. If you simply run the whole workflow again, it may try to create the account a second time and open a second ticket.

The word for an operation that can safely be repeated without changing the final result after the first successful application is idempotent. Build world-changing steps with the second run in mind. Before creating something, check whether it already exists. Before granting or removing access, check the current state when the process requires that level of certainty. Before opening a ticket, consider whether you can detect an existing ticket for the same event.

And carry one honest limit with you, which Modules 04 and 05 already hinted at and Module 11 will press harder. Testing cannot prove everything. You cannot practically rehearse every long wait, every external outage, or every race between two real events. So testing and defensive design are partners, not substitutes. You test what you can, and for everything you cannot rehearse, you design so failure is visible and recovery is safe.

## Before you move on

Walk a diagnosis in your head. You test Priya's offboarding workflow and it appears to do nothing. What is the first place you look to tell whether it ran and failed or never started? If there is no execution record, what is the first thing you suspect? During that same test, which feature lets you keep Manage Access from really changing Priya's access while you exercise the logic? If the welcome email arrives with a blank name, where in the execution details do you look and what does the blank tell you? If Manage Access shows success but one requested access item did not go through, which output do you inspect? And if the workflow created a ticket and then failed, what property must those earlier steps have before a second run is safe? If those answers come without strain, you can test without fear and debug without guessing, and you are ready for Module 08.

---
[← Previous: Module 06 Data, Variables, and Expressions](06-data-variables-and-expressions.md) | [Course home](../README.md) | [Next: Module 08 Operations, Limits, and Governance →](08-operations-limits-and-governance.md)