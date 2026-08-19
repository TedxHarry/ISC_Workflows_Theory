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

## Debugging Native Change executions

Native Change problems start with a different first question: did aggregation detect the change at all?

If there is no workflow execution for the direct account change you expected, check the source before you debug the workflow canvas. Native Change Detection must be enabled on that source. The operation must be monitored, for example Account Updates for a group added to an existing AD account. The attribute must be monitored, for example the entitlement attribute that represents group membership. The source must have aggregated after the direct target change. And remember the AND relationship from Module 02: the operation and monitored attribute both have to line up with the change.

Then check whether the source can use the feature in the way you configured it. SailPoint documents that Native Change Detection is not available for Non-Employee Lifecycle Management sources, and that SAML Just-in-Time sources require the Native Change Detection API endpoint to enable it. If the UI does not show the expected source option, do not treat that as a filter bug until you have confirmed the source's supported configuration path.

For platform-level evidence, Search gives you a second check. SailPoint documents three exact Native Change audit-event names: `Create Native Change Detected`, `Update Native Change Detected`, and `Delete Native Change Detected`. These are audit events, not additional Workflow triggers. Use them to confirm that ISC recorded the native-change detection at the expected operation boundary before spending time on downstream workflow logic.

If the workflow did run, inspect the trigger input before every other step. Native Change is account-centered. For a sensitive group addition, look at `source.id`, `account.id`, `account.nativeIdentity`, `account.correlated`, `accountChangeTypes`, and `entitlementChanges`. If `account.correlated` is `false`, the identity object is system-generated rather than a proven human identity, so an alert that names a person as the owner of the change is overclaiming. Route it to the source owner with the source and native account identity.

For an update event, do not assume the first entitlement change is the one you care about. Read through `entitlementChanges`, then through each `added` and `removed` list. For account attributes, separate `singleValueAttributeChanges` from `multiValueAttributeChanges`; they are different shapes. If a filter or choice expects the sensitive group under `singleValueAttributeChanges`, it will never match a real entitlement addition.

If a remediation step reports success but the sensitive access still appears on the next aggregation, apply green does not mean done. The workflow status proves the step completed from the workflow engine's point of view. It does not prove the target account stayed corrected after the fact. Check the remediation action output, the next aggregation result, the Native Change audit event, and the target system state. Also check whether a human or another process re-added the same access after your workflow removed it.

> **Work It Out**
>
> A Native Change Account Updated workflow should alert when `Finance Privileged Operators` is added to an AD account. The group was added directly in AD, but no workflow execution appears. Name the first checks, in order.
>
> <details>
> <summary>Check your answer</summary>
>
> First check whether the AD source has Native Change Detection enabled. Then check whether Account Updates are monitored and whether the entitlement attribute that carries group membership is monitored. Confirm an aggregation ran after the direct AD change, because native changes are detected on aggregation. If those are correct, remove or loosen the trigger filter and test against the real event shape. If the source does not expose the expected Native Change Detection option, verify the source's supported configuration path before treating the workflow as broken.
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

## Debugging certification campaign workflows

Certification incidents are easier when you follow one campaign id across its lifecycle instead of treating every green workflow execution as the same kind of success.

Start with the workflow that creates the campaign. If Acme's Finance mover should create a targeted review, inspect the Identity Attributes Changed trigger input first and prove that the `changes` array contains the department transition the workflow was designed to handle. Then inspect Create Certification Campaign. Confirm the reviewer type, certification type, `Identities to Certify`, campaign duration, undecided-item setting, and **Start Campaign when Created** value that actually rendered at runtime. The identity value must be the intended ISC identity id.

Next, inspect the Create action output and preserve its campaign id as the correlation value for later evidence. Create Certification Campaign has a documented 36-hour timeout, so a timeout here is not the same failure boundary as Get Certification Campaign, which times out after 1 minute, or Activate Certification Campaign, which times out after 2 hours.

If the design deliberately stages campaigns before activation, do not expect the original mover execution to receive a later Campaign Generated trigger. One workflow has one trigger, and separate event-driven workflows have separate execution contexts. The Campaign Generated execution should carry the generated campaign under `campaign`, including its id and the documented sample status `STAGED`. If another workflow is responsible for activation, inspect that execution and prove that Activate Certification Campaign received the same campaign id. A `Campaign Activated` event later represents the active boundary and its documented sample status is `ACTIVE`.

After activation, split reviewer evidence from campaign evidence. Certification Signed Off is about a certification reviewed by a reviewer. Its seed includes a `certification` object with fields such as `id`, `campaignRef`, `completed`, `hasErrors`, `decisionsMade`, `decisionsTotal`, `signed`, and reviewer information. It is not the Campaign End event. Campaign Ended is the campaign-level event and its documented sample status is `COMPLETED`.

That distinction matters when the incident is "the reviewer revoked access, but the user still has it." SailPoint documents that signed-off revoke decisions initiate remediation, but remediation can be automatic or manual depending on the source. Do not stop at Certification Signed Off or Campaign Ended. Inspect the campaign remediation evidence, provisioning or account activity where applicable, and the target state when the business requires confirmation.

Replay is a debugging concern too. If Create Certification Campaign returned an ambiguous result or an operator is considering a rerun, first determine whether a campaign already exists for that business event. The action documentation does not promise idempotent creation. Replaying blindly can create a duplicate campaign and duplicate reviewer work. Use the durable correlation record or reconciliation mechanism defined by the production design before deciding to create again.

> **Work It Out**
>
> The Finance mover execution is green and its Create Certification Campaign output contains campaign id `C-1042`. A separate Campaign Generated execution exists for `C-1042`, but no Campaign Activated execution exists. An engineer proposes rerunning the mover workflow. What should you inspect first, and why is rerunning the wrong first move?
>
> <details>
> <summary>Check your answer</summary>
>
> The existing campaign already crossed the creation and generation boundaries, so recreating it does not address the missing activation. Open the Campaign Generated execution, confirm it is the expected campaign and inspect its `campaign.id` and status. Then inspect the workflow that should activate staged campaigns. Confirm its filter or correlation check accepted `C-1042`, and confirm Activate Certification Campaign received that exact campaign id. If the activation action failed, inspect its error rather than creating another campaign. Rerunning the mover workflow first risks a duplicate certification because Create Certification Campaign is not documented as idempotent.
>
> </details>

## Debugging External Trigger and HTTP integrations

An external integration has two systems to inspect, so start at the boundary between them instead of starting in the middle of the workflow.

For an inbound External Trigger, first inspect what the caller received from the external workflow execution API. Current Developer documentation lists `200`, `400`, `401`, `403`, `429`, and `500` outcomes, and the success response model can include a `workflowExecutionId` plus a `message` when an error occurred. Do not stop at the HTTP status. Read the response body too. A bad request points toward the request shape. `401` or `403` points toward authentication or authorization. `429` is rate limiting. A server error belongs on a retry or operator path defined by the calling integration rather than being guessed at inside ISC.

Then ask whether an execution exists. If none exists, verify the caller used the External Trigger invocation details generated for the correct enabled workflow and that its configured authorization method is current. Product documentation teaches a trigger-generated OAuth client path, while current v2025 Developer API documentation also advertises Personal Access Token and Client Credentials authorization with scope `sp:workflow-execute:external`. Debug the method that the integration actually uses. If that caller uses the trigger-generated credential and a new External Trigger access token was generated, the previous token is overwritten, so an upstream service still using the old credential can fail after rotation.

If an execution does exist, inspect the trigger input before later steps. External Trigger data is dynamic, so SailPoint does not expose its caller-defined fields through the normal variable selector. Confirm the real payload and the JSONPath you wrote, for example `$.trigger.eventId` or `$.trigger.workerId`. Then inspect the validation steps. Verify Data Type can confirm existence and basic types, but a correctly typed value can still be an unknown event type, an unmapped external identifier, or a replay of an event already processed.

SailPoint also exposes a dedicated External Trigger test endpoint whose purpose is to validate that a workflow can receive the supplied input intact. Use that boundary test when you need to prove the caller-to-trigger payload shape. Do not confuse it with the ordinary Test Workflow operation. The ordinary workflow test can execute enabled actions for real, so continue to simulate dangerous actions or use a safe sandbox when testing the workflow itself.

For an outbound HTTP Request, open the action and read the error branch data. Workflow error handling exposes `workflowErrorMessage` and `workflowStatusCode` for the failed action. Check authentication, request URL, headers, rendered body, and the external response. Remember the documented 90-second timeout. Also remember that an external response must be JSON for this action. If a later step expects a field such as `caseId`, inspect the actual HTTP Request output and prove that field exists before debugging the later JSONPath.

Rate limiting is another specific clue. HTTP Request documents handling for common rate-limit response headers, including `Retry-After` and several reset-header variants. Do not invent a retry count or assume every remote error is retried. Read the actual error and the remote API's contract.

> **Work It Out**
>
> Acme's HR service says it called the separation workflow successfully, but no security case was opened. The HR logs show an External Trigger API response, and ISC has a workflow execution. What do you check, in order?
>
> <details>
> <summary>Check your answer</summary>
>
> Start with the caller response and confirm the workflow execution id and any message. Because an ISC execution exists, open it and inspect the trigger input next. Confirm `eventId`, `eventType`, and `workerId` arrived in the shape the workflow expects. Then inspect the validation and identifier-mapping steps before the HTTP call. If those passed, inspect the HTTP Request input, rendered body, and output or error branch. Check `workflowStatusCode` and `workflowErrorMessage` on an error path, remember the 90-second timeout, and confirm the external system returned the JSON field the downstream logic expects. Do not jump straight to the case system until you know which boundary failed.
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
