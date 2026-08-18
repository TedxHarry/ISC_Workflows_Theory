# Module 04: Actions

Everything a workflow can actually do.

If operators are the thinking of a workflow, actions are the hands. An action is any step that reaches out and affects something: it sends a message, it fetches data, it changes access, it calls another system, it pauses. Every time a workflow touches the world, an action is doing the touching. That also makes actions the place where most real failures happen, because reaching outside your workflow means depending on things you do not fully control. So we will teach the actions you use constantly in real depth, learn where they break, and then map the rest by family so you can place any action you meet.

There is a clean way to hold the whole set in your head. Almost everything a workflow does is one of five verbs: notify, fetch, change, integrate, and pause. Learn one action for each verb and you can build most of what Acme needs. Priya will walk us through them.

## Send Email: notify

We met this one informally in Module 01. Now let us look at it properly. Send Email needs three things: recipients, a subject, and a body. You rarely type real values into these. You point at data, exactly as you learned, so the recipient is a JSONPath to an email address and the body weaves in variables like the first name. Written once, it works for every new hire.

There is one small quirk worth knowing before it puzzles you. The body can contain formatting, but the characters that mean "start of a tag" and "end of a tag," the less-than and greater-than signs, have to be surrounded by spaces to be treated as plain text. If you paste in tightly packed markup and the email comes out looking broken, this spacing rule is the usual reason. It is a tiny thing, and it is exactly the kind of tiny thing that eats an afternoon if you do not know it.

Reach for Send Email whenever a human needs to be told something. If your organization lives in chat instead, there is a Send Slack Message action that plays the same notification role. Interactive Message is different: it displays progress information inside an Interactive Process, which we will cover in Module 05.

## Get Identity: fetch what the trigger did not hand you

Here is a problem you will hit early, and it teaches an important habit. Back in Module 02 we saw that a trigger hands you only some of the data about a person. Priya's joiner seed carried her name, email, and department, but not, say, her manager or her full attribute set. Suppose the welcome email needs to also notify her manager. The manager is not in the seed. So where do you get it?

You fetch it. Get Identity takes an identity id and returns identity data as JSON, including default and custom attributes. You feed it the id you already have, typically `$.trigger.identity.id`, and in the steps that follow you read from its output with JSONPath the same way you read the trigger. This is the tool that turns "the trigger only gave me a little" into "now I have the identity data I need."

Get Identity matters even more for scheduled workflows. Remember that a scheduled workflow starts with no person attached, because nothing happened to anyone. It has to go and find its subjects, and Get Identity, along with its plural cousin Get List of Identities, is how it does that.

You will meet this exact shape again when Priya *moves*. In Module 02 we saw that an Identity Attributes Changed event carries only what changed, so when her department flips to Finance the event hands you her new manager's id but not that manager's email address. To notify the manager you do precisely what you did here: Get Identity on the manager's id, then read the email from the result. Whenever the trigger gives you a reference but not the field you actually need, fetching is the move. The flip side is a small discipline worth building now: when the value is already sitting in the payload, reaching for Get Identity anyway just spends an execution and adds another step that can fail.

One operational fact to carry: action timeouts are defined per action, not by one universal workflow timeout. Get Identity times out after 1 minute. That is normally plenty for a single lookup, but the general lesson matters: before relying on a long-running action, check that action's documented timeout rather than assuming every step has the same ceiling.

## Manage Access: change access

Notifying and fetching are gentle. Manage Access is where a workflow changes real things about real people, so it deserves respect. It does exactly what its name says: it adds access to identities or removes access from them. You give it three things: who, the identity or identities to act on; what, the access items, which can be roles, access profiles, or entitlements; and which direction, add or remove.

For Priya this can be both a joiner and a leaver tool. On day one you might add access that is appropriate for a workflow-driven exception. On her last day you might remove specific access as part of an offboarding process. Remember from Module 09 that standard birthright access is better modeled through roles, access profiles, and lifecycle configuration rather than handed out one person at a time by a workflow.

Manage Access has a 30 minute timeout. More importantly, understand what "success" means here. The action submits access requests and continues based on that submission. If approval is required, the workflow does not wait for the approval decision. If approval is not required, the workflow still does not wait for confirmation that the target source has finished updating the account.

There is also an important result-handling trap. A Manage Access step can complete successfully while some requested access changes are represented in `failedAccessRequests`. The workflow execution itself is not automatically marked failed just because that output contains failed requests. If your process requires every requested change to succeed, inspect `successfulAccessRequests` and `failedAccessRequests` and branch deliberately instead of treating a green Manage Access step as proof that every access change completed.

Because this action changes access, it is precisely the kind of step you do not want to fire by accident while testing. Module 07 covers simulated testing so you can exercise the workflow logic without allowing selected world-changing steps to execute. Build the instinct now: when a step changes the world, test it with the safety on.

This action is also a small lesson in how the platform evolves, and it is worth teaching directly. Manage Access replaced two older actions, Create Request for Access and Request Access Removal. Those are deprecated now. Adding access is Manage Access with Add selected, and removing access is Manage Access with Remove selected. You may still open an older workflow someone built years ago and find those deprecated steps inside. When you do, you now know what they were and what to use instead. A good habit across all of ISC: when a step looks unfamiliar or is marked deprecated, check the current documentation rather than copying the old pattern forward.

If your task is about accounts rather than access, there is a parallel action called Manage Accounts, which can delete, disable, enable, or unlock source accounts. Manage Accounts has its own timeout of 1 hour. Access and accounts are different layers, and the two Manage actions match that split.

## Green does not mean done

The Manage Access trap above is one instance of a bigger idea, and it is worth naming because you will meet it everywhere in ISC. A green step tells you the action satisfied *its own* success contract. It does not, by itself, tell you the business result actually happened. Hold these three as genuinely different states:

```
Workflow step succeeded   ≠   Request approved   ≠   Change live on the target system
```

Manage Access shows the full distance between them. The step goes green the moment ISC accepts the request, but from there the outcome can still be unfinished at every stage:

```
Manage Access accepted the request
        ↓
Approval may still be pending
        ↓
Provisioning may still be running
        ↓
The target account may not yet reflect the change
```

The same gap can hide inside gentler actions too. An HTTP Request can return a successful response whose body does not contain the field you assumed. And a notification can leave a run looking healthy while the intended person was never actually reached. So when the outcome matters, do not stop at the status. Inspect the step's input and output, including the rendered recipient of a Send Email, rather than assuming a green run proves the message reached the right person. The idea has a name now, and it comes back when we read execution history in Module 07, build patterns in Module 10, and design for failure in Module 11.

> **Work It Out**
>
> A workflow reacts to Priya's move to Finance and should email her new manager. The build points the Send Email recipient at the manager's change entry, `$.trigger.changes[?(@.attribute == "manager")].newValue.email`. The test run looks successful, but no email ever arrives. What went wrong, and how would you fix it?
>
> <details>
> <summary>Check your answer</summary>
>
> The manager value inside the `changes` array is an identity *reference*: it holds the id, name, and type, but not an email address. The path resolves to nothing, so the recipient is empty and no message reaches the manager, even though the run may look otherwise healthy. This is *green does not mean done* in miniature. The fix is to Get Identity on the manager's id (`...newValue.id`), then read the manager's email from that lookup's output and send to that.
>
> </details>

## HTTP Request: integrate with anything

Sooner or later you will need a workflow to talk to a system ISC has no built-in action for. HTTP Request is the universal answer, and it is one of the most powerful actions in the toolbox because it lets a workflow reach almost anywhere.

You configure it like any web call: a URL to hit, a method such as GET to read or POST to send, headers, a body, and authentication so the far system trusts the request. When the call comes back, the response is placed into the workflow's data flow as JSON, and you read it in later steps with JSONPath, just like everything else. So HTTP Request is both a way to push information out and a way to pull information in.

Picture it with Priya. Suppose Acme calls an internal directory service to find her desk, and the call comes back with:

```json
{
  "employeeId": "priya.patel",
  "building": "HQ-2",
  "deskId": "2-141"
}
```

If you named the step getDeskInfo, a later step reads the values straight out of that response with JSONPath, for example `$.getDeskInfo.building` and `$.getDeskInfo.deskId`, and drops them into the welcome email. The important part is that the shape of this response is decided by the system you called, not by ISC. That is exactly why the caution coming next matters so much.

Notice the symmetry with Module 02. The External Trigger was how an outside system reaches into ISC to start a workflow. HTTP Request is how a workflow reaches out to an outside system. One is inbound, one is outbound, and together they let ISC sit in the middle of your wider environment.

HTTP Request times out after 90 seconds. The moment you call another system, you have taken on a dependency you do not control. It can be slow. It can be down. It can return an error, or return success but in a shape you did not expect. A workflow that assumes the call always works and always returns the same thing is a workflow that will fail in ways your testing never showed you. So treat HTTP Request with care: plan for the response to be missing or malformed, use error handling so a failed call takes a deliberate path, and never hard-code a password or token into the request. Use the authentication parameters provided by ISC, including Parameter Storage where supported, which we cover in Module 08.

## Wait: pause

Not every step does something. Sometimes the right move is to do nothing, on purpose, for a while. The Wait action can pause the workflow for a duration or until a specific future date and time.

For Wait For, the configured duration must be at least 60 seconds and can be up to 30 days. Wait Until can target a date up to 180 days in the future. The Wait step itself times out if it takes longer than 182 days to complete.

This is useful when another process needs time to catch up, when you want a delayed reminder, or when you deliberately need to stagger work. Wait is how a workflow spans time rather than finishing in one burst.

It comes with its own kind of caution. A workflow with a Wait in it is a long-running workflow. It is alive for hours or days, holding its place, which has consequences for how you think about testing and recovery. You cannot practically sit and watch a three day wait during a normal test, so a Wait is one of the places where testing cannot prove the whole production path, a limit we take seriously in Modules 07 and 11.

## A map of the rest, grouped by family

Those five verbs cover the majority of real work. Here is the rest of the catalog, grouped so you can find the right tool by the kind of job, without memorizing a list. As always, the builder shows each action's exact inputs and the JSON it adds, and the official actions documentation is the full reference.

Notifications. Alongside Send Email you have Send Slack Message for direct Slack notifications. Interactive Message belongs to the Interactive Process family and displays a progress message to the user who launched that process. Reach here to tell a human something, but choose the action that matches where that human is interacting.

Get data. Beyond Get Identity, there is Get List of Identities for many at once, Get Accounts for account records, Get Access to read access items, and Get Identity History to see how an identity changed over time. Reach here when you need more information than your trigger handed you. These lookup actions commonly have short, action-specific timeouts, so check the current action documentation when the exact limit matters.

Manage data. Manage Access changes access, and Manage Accounts changes the accounts themselves. Reach here when the workflow must change something rather than just read it.

Access request. This family lets a workflow take part in the request and approval process: Approve Access Request and Deny Access Request to act on a request, Get Pending Access Requests to see what is waiting, Get Access Request Recommendations to pull in guidance, and the Approval Policy and Generic Approval Policy actions to route approvals. The deprecated Create Request for Access and Request Access Removal also lived here, now folded into Manage Access. Reach here to automate around requests and approvals.

Certification. Create Certification Campaign, Activate Certification Campaign, and Get Certification Campaign let a workflow start and manage access reviews. Reach here to automate the certification cycle, which we sketch as a use case in Module 10.

Ticketing. Manage ServiceNow Ticket opens and updates tickets in ServiceNow directly, without you having to build the call by hand with HTTP Request. Reach here when your process runs on ServiceNow.

Connector and privileged task automation. There are actions that act directly on platforms such as Active Directory, Microsoft Entra ID, and Windows Server for privileged tasks. These depend on the matching setup being in place, so if one does not appear or does not work, check the required capability and connection rather than assuming the workflow logic is wrong.

Forms and interaction. The Form action can assign a form to a specific user and pause until it is completed or the deadline is reached. Interactive Form and Interactive Message are different actions used inside an Interactive Process launched by a user. Module 05 separates those patterns clearly.

## The thread that ties the failures together

Step back and notice something. Almost every caution in this module came from the same root: actions reach outside the workflow, and the outside is not fully under your control. The external API might not answer. A Manage Access request might be submitted but later denied or fail. An account action can take much longer than an identity lookup. The waiting workflow can live for days. This is not a flaw in the actions, it is the nature of doing real work. The skill is not avoiding these steps. It is knowing each action's contract, timeout, output, and failure behavior, then building the next step around what the action actually guarantees.

## Before you move on

Design Priya's offboarding as a sequence of actions, using only this module. When her lifecycle state changes to terminated, what is the first action you would run to make sure you have her full details in hand, and why might the trigger alone not be enough? Which action removes her access, and which single setting on it decides that it removes rather than grants? After Manage Access reports success, what output would you inspect if your process requires every requested access change to have been accepted successfully? If offboarding also has to close out a record in a system ISC has no built-in action for, which action reaches that system, and what is its timeout? And if you wanted to wait a day before sending a final confirmation, which action buys you that day, and what does adding it cost you in how the workflow now lives and how you can test it? If those answers come readily, you can make a workflow act, and you are ready for Module 05, where a human steps into the middle of the flow through forms.

---
[← Previous: Module 03 Operators and Logic](03-operators-and-logic.md) | [Course home](../README.md) | [Next: Module 05 Forms and Interactive Workflows →](05-forms-and-interactive-workflows.md)
