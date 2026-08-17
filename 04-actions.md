# Module 04: Actions

Everything a workflow can actually do.

If operators are the thinking of a workflow, actions are the hands. An action is any step that reaches out and affects something: it sends a message, it fetches data, it changes access, it calls another system, it pauses. Every time a workflow touches the world, an action is doing the touching. That also makes actions the place where most real failures happen, because reaching outside your workflow means depending on things you do not fully control. So we will teach the actions you use constantly in real depth, learn where they break, and then map the rest by family so you can place any action you meet.

There is a clean way to hold the whole set in your head. Almost everything a workflow does is one of five verbs: notify, fetch, change, integrate, and pause. Learn one action for each verb and you can build most of what Acme needs. Priya will walk us through them.

## Send Email: notify

We met this one informally in Module 01. Now let us look at it properly. Send Email needs three things: recipients, a subject, and a body. You rarely type real values into these. You point at data, exactly as you learned, so the recipient is a JSONPath to an email address and the body weaves in variables like the first name. Written once, it works for every new hire.

There is one small quirk worth knowing before it puzzles you. The body can contain formatting, but the characters that mean "start of a tag" and "end of a tag," the less-than and greater-than signs, have to be surrounded by spaces to be treated as plain text. If you paste in tightly packed markup and the email comes out looking broken, this spacing rule is the usual reason. It is a tiny thing, and it is exactly the kind of tiny thing that eats an afternoon if you do not know it.

Reach for Send Email whenever a human needs to be told something. If your organization lives in chat instead, there is a Send Slack Message action that plays the same role, and an Interactive Message action for when you want the person to click a response rather than just read. We will treat the interactive ones in Module 05, because they pair with forms.

## Get Identity: fetch what the trigger did not hand you

Here is a problem you will hit early, and it teaches an important habit. Back in Module 02 we saw that a trigger hands you only some of the data about a person. Priya's joiner seed carried her name, email, and department, but not, say, her manager or her full attribute set. Suppose the welcome email needs to also notify her manager. The manager is not in the seed. So where do you get it?

You fetch it. Get Identity takes an identity id and returns the full identity as a JSON blob, with all the attributes you did not get for free. You feed it the id you already have, typically `$.trigger.identity.id`, and in the steps that follow you read from its output with JSONPath the same way you read the trigger. This is the tool that turns "the trigger only gave me a little" into "now I have everything about this person."

Get Identity matters even more for scheduled workflows. Remember that a scheduled workflow starts with no person attached, because nothing happened to anyone. It has to go and find its subjects, and Get Identity, along with its plural cousin Get List of Identities, is how it does that.

One operational fact to carry: this action, like the other actions that call into ISC to fetch or change things, has a ninety second timeout. That is generous for a single lookup and almost never a problem here, but it is a real ceiling, and it becomes relevant the moment you start doing many lookups inside a loop. Keep it in the back of your mind.

## Manage Access: change access

Notifying and fetching are gentle. Manage Access is where a workflow changes real things about real people, so it deserves respect. It does exactly what its name says: it adds access to identities or removes access from them. You give it three things: who, the identity or identities to act on; what, the access items, which can be roles, access profiles, or entitlements; and which direction, add or remove.

For Priya this is both a joiner and a leaver tool. On day one you might add the birthright access every Acme employee gets. On her last day you remove her access as part of offboarding. Same action, opposite direction.

Two things to hold onto. First, this action also carries the ninety second timeout, and because it changes access rather than just reading, a timeout here matters more. Second, and more important, Manage Access has real consequences. Adding or removing access changes what a human being can and cannot do at work. This is precisely the kind of step you do not want to fire by accident while testing, which is why Module 07 covers a simulation mode that lets you run a workflow without letting steps like this actually touch anything. Build the instinct now: when a step changes the world, test it with the safety on.

This action is also a small lesson in how the platform evolves, and it is worth teaching directly. Manage Access replaced two older actions, Create Request for Access and Request Access Removal. Those are deprecated now. Adding access is Manage Access with Add selected, and removing access is Manage Access with Remove selected. You may still open an older workflow someone built years ago and find those deprecated steps inside. When you do, you now know what they were and what to use instead. A good habit across all of ISC: when a step looks unfamiliar or is marked deprecated, check the current documentation rather than copying the old pattern forward.

If your task is about accounts rather than access, there is a parallel action called Manage Accounts, which enables, disables, and otherwise acts on the accounts themselves. Access and accounts are different layers, and the two Manage actions match that split.

## HTTP Request: integrate with anything

Sooner or later you will need a workflow to talk to a system ISC has no built-in action for. HTTP Request is the universal answer, and it is the single most powerful action in the toolbox because it lets a workflow reach almost anywhere.

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

This action is also where the honest warning about actions lands hardest. The moment you call another system, you have taken on a dependency you do not control. It can be slow. It can be down. It can return an error, or return success but in a shape you did not expect. A workflow that assumes the call always works and always returns the same thing is a workflow that will fail in ways your testing never showed you. So treat HTTP Request with care: plan for the response to be missing or malformed, use the error handling that lets a failed call branch to its own path rather than silently poisoning the rest of the run, and never hard-code a password or token into the request. Secrets belong in the secure handling we cover in Module 08, and the full set of ways external calls bite you is the heart of Module 11. For now, the lesson is simply this: an HTTP Request is a door to another system, and you should always ask what happens when whatever is on the other side of that door does not answer the way you hoped.

## Wait: pause

Not every step does something. Sometimes the right move is to do nothing, on purpose, for a while. The Wait action pauses the workflow for a duration you set, in units like hours or days, and then lets it continue.

This is more useful than it first sounds. You might create something in another system, then wait a day for a downstream process to catch up before checking the result. You might wait a set period and then send a follow-up reminder. You might deliberately stagger work. Wait is how a workflow spans time rather than finishing in one burst.

It comes with its own kind of caution, though, and it is a subtle one. A workflow with a Wait in it is a long-running workflow. It is now alive for hours or days, holding its place, which has consequences for how you think about changing it, about ordering, and especially about testing. You cannot practically sit and watch a three day wait during a test, so a Wait is a place where testing genuinely cannot prove the whole path, a limit we take seriously in Modules 07 and 11. Use Wait when spanning time is truly what the task needs, and go in knowing you have made the workflow a slower, longer-lived thing.

## A map of the rest, grouped by family

Those five verbs cover the majority of real work. Here is the rest of the catalog, grouped so you can find the right tool by the kind of job, without memorizing a list. As always, the builder shows each action's exact inputs and the JSON it adds, and the official actions documentation is the full reference.

Notifications. Alongside Send Email you have Send Slack Message for chat and Interactive Message for a message the recipient can respond to. Reach here to tell a human something.

Get data. Beyond Get Identity, there is Get List of Identities for many at once, Get Accounts for account records, Get Access to read what access someone has, and Get Identity History to see how an identity changed over time. Reach here when you need more information than your trigger handed you.

Manage data. Manage Access changes access, and Manage Accounts changes the accounts themselves, enabling or disabling them. Reach here when the workflow must change something rather than just read it.

Access request. This family lets a workflow take part in the request and approval process: Approve Access Request and Deny Access Request to act on a request, Get Pending Access Requests to see what is waiting, Get Access Request Recommendations to pull in guidance, and the Approval Policy and Generic Approval Policy actions to route approvals. The deprecated Create Request for Access and Request Access Removal also lived here, now folded into Manage Access. Reach here to automate around requests and approvals.

Certification. Create Certification Campaign, Activate Certification Campaign, and Get Certification Campaign let a workflow start and manage access reviews. Reach here to automate the certification cycle, which we sketch as a use case in Module 10.

Ticketing. Manage ServiceNow Ticket opens and updates tickets in ServiceNow directly, without you having to build the call by hand with HTTP Request. Reach here when your process runs on ServiceNow.

Connector and privileged task automation. There are actions that act directly on specific platforms, Active Directory, Microsoft Entra ID, and Windows Server, for privileged tasks on those systems. These depend on the matching connector and setup being in place, so if one does not appear or does not work, the likely cause is a missing dependency rather than a mistake in your workflow. Reach here for deep, platform-specific operations.

Forms and interaction. The Form action, the Interactive Form, and the Interactive Message bring a human into the middle of a workflow, and they pair with Wait and with the form triggers. Module 05 is devoted to them.

## The thread that ties the failures together

Step back and notice something. Almost every caution in this module came from the same root: actions reach outside the workflow, and the outside is not fully under your control. The external API might not answer. The access change might time out at ninety seconds. The waiting workflow lives for days and cannot be fully tested. This is not a flaw in the actions, it is the nature of doing real work. The skill is not avoiding these steps, it is using them with your eyes open: expect the failure, give it a path to go down, and never let a step that changes the world run untested. That mindset is what Modules 07 and 11 build into a full practice.

## Before you move on

Design Priya's offboarding as a sequence of actions, using only this module. When her lifecycle state changes to terminated, what is the first action you would run to make sure you have her full details in hand, and why might the trigger alone not be enough? Which action removes her access, and which single setting on it decides that it removes rather than grants? If offboarding also has to close out a record in a system ISC has no built-in action for, which action reaches that system, and name one thing that could go wrong with that call that your happy-path testing would never reveal. And if you wanted to wait a day after disabling her accounts before sending a final confirmation, which action buys you that day, and what does adding it cost you in how the workflow now lives and how you can test it? If those answers come readily, you can make a workflow act, and you are ready for Module 05, where a human steps into the middle of the flow through forms.

---
[← Previous: Module 03 Operators and Logic](03-operators-and-logic.md) | [Course home](../README.md) | [Next: Module 05 Forms and Interactive Workflows →](05-forms-and-interactive-workflows.md)
