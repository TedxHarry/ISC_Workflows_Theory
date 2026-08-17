# Module 05: Forms and Interactive Workflows

Bringing a human into the middle of a workflow.

So far our workflows have run on their own. Something happened, steps ran, nobody was asked anything. But plenty of real processes need a person. Sometimes you need someone to give you information the workflow cannot know on its own, and sometimes you need someone to make a decision that a machine should not make alone. Forms and approvals are how a workflow brings a human in.

Here is the honest challenge of this module, and it is the reason the module exists. ISC gives you several human-in-the-loop tools that look alike at a glance: a form that starts a workflow, a form that runs inside a workflow, an interactive message, and a set of approval actions. People reach for the wrong one all the time and then fight the tool. So most of what follows is not "how do I make a form," it is "which of these do I actually want, and why." Get that straight and the rest is easy.

## Two directions a human can enter

Start with the single most important distinction. A form can play two completely different roles, and they are not variations on a theme, they are opposite ends of a workflow.

A form can start a workflow. This is the Form Submitted trigger we met back in Module 02. The form already exists somewhere, a person fills it in and submits it, and that submission is the event that kicks the workflow off. The person acts first, the workflow runs second. Think of this as intake, the front door. Acme might publish a "request a shared mailbox" form, and every submission starts a workflow that processes the request.

A form can pause a workflow that is already running. This is the Form action, and it works the other way around. The workflow is already in motion, it reaches a step where it needs a human, so it hands a specific person a form and stops, waiting, until they submit. The workflow acts first, the person acts second, and then the workflow picks up where it left off using their answers. This is not intake, it is asking a question in the middle of a process.

Same building block, a form, in two opposite roles. One is how a workflow begins. The other is a step inside a workflow. If you can hold that difference clearly, you are most of the way through this module, because almost every mistake people make here comes from confusing the two.

## The Form action, up close

Let us look closely at the pausing kind, because it has the most moving parts and the most interesting failure.

When a workflow reaches a Form action, it assigns a form to a chosen person and sets a deadline. That person gets an email with a link to the form. Meanwhile the workflow halts. It does not move to the next step, it does not end, it simply waits, holding its place, until the person submits the form. When they do, the values they entered become available to the rest of the workflow as variables, read with JSONPath by the step name, exactly like the output of any other step.

Picture it with Priya. During her onboarding, the workflow needs to know which optional systems her manager wants her to have, something no trigger can tell you because it is a human judgment. So the workflow runs a Form action that assigns Priya's manager a short form. You can pre-fill parts of it, because workflow variables map onto the form's inputs, so the manager sees Priya's name and department already filled in and only has to pick the systems. If you named that step pickSystems and the form has a field for the chosen systems, a later step reads the answer at `$.pickSystems.extraSystems` and goes on to grant them. The form also exposes a Submitted attribute, a simple true or false, so your logic can check whether the form was actually completed before it relies on the answers.

Now the failure that you must design for, because it is not an edge case, it is the normal case eventually. What if the manager never fills in the form? A Form action is a pause, and a pause on a human can wait forever, so it has a deadline. When the deadline passes, the form does not just quietly close, it generates a cancellation error. That means a Form action is a step that can fail by silence, and a workflow that ignores this possibility will one day stall or break because someone went on vacation. So you plan for it. You set reminders so the person is nudged. You handle the timeout with an error path that does something sensible, escalate to a backup approver, notify someone, or end cleanly with a clear Failure that a human can see later. This connects straight back to two things you already know: the Wait action from Module 04 made a workflow long-running, and a Form action does the same, only now the delay depends on a person rather than a clock. A form is the most human, and therefore the most unpredictable, step you can add.

## Interactive messages, the lighter touch

A full web form is the right tool when you need structured input with several fields. But sometimes all you want is a quick decision, a single tap, and sending someone to a web form for that is heavier than it needs to be. That is what the interactive options are for.

An Interactive Message sends a person a message they can respond to directly, for example a chat message in Slack with buttons to click, rather than a link to a separate form. It pairs with the interactive trigger and interactive process, which are ISC's way of supporting a human decision point inside a flow. The everyday judgment is about ceremony. Reach for an Interactive Message when the human step is a fast, low-effort choice, approve or reject, yes or no, pick one of two, and your people live in chat. Reach for a full Form when you genuinely need several fields of structured input. Using a heavy form for a one-tap decision trains people to ignore your requests, and using a one-tap message for something that needs real detail leaves you without the information you needed.

I will be straight about the limits of what I can promise here: the fine configuration of the interactive actions is the kind of detail that is best confirmed in the builder and the current docs, because it is more feature-dependent and more likely to shift than the core Form action. The judgment, though, is stable: match the weight of the tool to the weight of the decision.

## Intake versus approval, and a trap to avoid

There is a second distinction that matters as much as the first, and it is about what you are asking the human to do.

Sometimes you want information. What systems does Priya need, what is the business justification, which cost center pays. That is intake, and a form is the right tool, because a form is built to gather arbitrary structured input.

Sometimes you want a governed decision. Should this person be allowed this access, yes or no, made by the right reviewer, with reminders if they stall, an escalation if they never answer, a time limit, and a record of who decided what. That is an approval, and here is the trap: you can almost build an approval out of a plain form with a "yes or no" field, and you should not. If you do, you are rebuilding, by hand and badly, something ISC already does properly. Approvals have dedicated tooling, and it is worth using.

The Approval Policy action is the main one. It governs approvals for access requests, so it pairs with the Access Request Submitted trigger from Module 02. It lets you choose how the approval works: a Single reviewer, a Multi-Step approval where several reviewers approve in sequence or in parallel and all must say yes, or a Quorum where a set percentage of reviewers approving is enough. It lets you choose who reviews, the owner of the access item, a governance group, a specific named identity, or the person's manager. And it handles the human-stalls problem for you, with a priority level, reminders on a schedule such as daily or weekly, and a timeout that can stretch up to ninety days before the request expires. That is a great deal of hard, fiddly logic that you get by configuration instead of by building it yourself.

For Priya, this is the mover moment. When her move to Finance leads to a request for Finance access, an Approval Policy routes that request to the owner of the Finance access, nudges them if they sit on it, and expires the request if it is never answered, all without you wiring up a single reminder by hand.

There is a sibling for decisions that are not access requests. The Generic Approval Policy action handles task-based approvals, things like approving that an account be disabled or that a group be created, work that is not a standard access request. It offers the same reviewer and scheme choices, and it asks for a name and a short description so the reviewer understands what they are approving, with an option to force reauthentication in SSO-enabled tenants when the decision is sensitive enough to warrant proving who you are again.

Finally, when you need to act on a specific request directly rather than route it through a policy, the Approve Access Request and Deny Access Request actions do exactly that. They take the request's id and a comment and record the decision. Like the other actions that reach into the access request service, they carry a ninety second timeout and fail if that service is unavailable, which is one more external dependency to keep in mind.

So the judgment across this whole family: use a form when you need information, use an approval policy when you need a governed yes or no, and use an interactive message when you need a quick decision with little ceremony. Three tools, three jobs, and choosing correctly is most of doing this well.

## Designing the form itself

A quick word on building a good form, because a badly designed form is where human-in-the-loop processes go to die. Every field you add is one more thing standing between the person and the submit button, and one more chance for them to give up. So ask only for what you truly need.

Forms let you define inputs, mark some as required, and pre-fill fields from workflow variables so the person is not retyping things the workflow already knows. They also support conditional visibility, which means a field can appear only when it is relevant, for example showing a "which mailbox" field only after the person has said they need a shared mailbox. Good conditional visibility keeps a form short by hiding everything that does not apply to the choices made so far. For inputs that are a choice from a list, forms provide array inputs, where you configure the value that gets returned along with the label and sublabel that the person sees in the dropdown, so you can present friendly names while capturing the underlying identifiers your later steps need.

The whole art is restraint. A short, well-pre-filled form with only the relevant fields showing gets completed quickly. A long form that asks for everything, relevant or not, gets ignored, and an ignored form is the timeout failure from earlier waiting to happen.

## Before you move on

Design one human-in-the-loop step for Priya and defend your choice of tool. If Acme wants managers to kick off a "request temporary contractor access" process by filling something in, is that a Form Submitted trigger or a Form action, and why are those two not interchangeable? If, in the middle of Priya's onboarding, the workflow needs her manager to pick which optional systems she gets, which tool fits, and what single attribute would you check before trusting the answer? When her Finance access needs a governed yes or no from the access owner, why is an Approval Policy the right choice rather than a form with a yes-or-no field? And for every one of these, answer the question that separates people who have run these in production from people who have not: what happens if the human never responds, and what did you build to handle that? If those answers come readily, you understand human-in-the-loop workflows, and you are ready for Module 06, where we go deep on the data and JSONPath that all of this has been quietly standing on.

---
[← Previous: Module 04 Actions](04-actions.md) | [Course home](../README.md) | [Next: Module 06 Data, Variables, and Expressions →](06-data-variables-and-expressions.md)
