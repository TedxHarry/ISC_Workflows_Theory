# Module 05: Forms and Interactive Workflows

Bringing a human into the middle of a workflow.

So far our workflows have run on their own. Something happened, steps ran, nobody was asked anything. But plenty of real processes need a person. Sometimes you need someone to give you information the workflow cannot know on its own, and sometimes you need someone to make a decision that a machine should not make alone. Forms and approvals are how a workflow brings a human in.

Here is the honest challenge of this module, and it is the reason the module exists. ISC gives you several human-in-the-loop tools that look alike at a glance: a form that starts a workflow, a Form action that pauses a running workflow for a specific recipient, an Interactive Process launched by a user, Interactive Forms and Messages inside that process, and approval actions. People reach for the wrong one all the time and then fight the tool. So most of what follows is not "how do I make a form," it is "which of these do I actually want, and why." Get that straight and the rest is easy.

## Two directions a human can enter

Start with the single most important distinction. A form can play two completely different roles, and they are not variations on a theme. They are opposite ends of a workflow.

A form can start a workflow. This is the Form Submitted trigger we met back in Module 02. The form already exists, a person fills it in and submits it, and that submission is the event that kicks the workflow off. The person acts first, the workflow runs second. Think of this as intake, the front door. Acme might publish a "request a shared mailbox" form, and every submission starts a workflow that processes the request.

A Form action can pause a workflow that is already running. The workflow is already in motion, it reaches a step where it needs a human, so it assigns a selected form to a specific ISC user and stops until that user submits it. The recipient receives an email containing the form link. The workflow acts first, the person acts second, and then the workflow resumes using the submitted values.

Same broad idea, a form, but two opposite roles. One is how a workflow begins. The other is a step inside a workflow. If you can hold that difference clearly, you are most of the way through the ordinary Form pattern.

## The Form action, up close

Let us look closely at the pausing kind, because it has the most moving parts and the most interesting failure.

When a workflow reaches a Form action, it assigns a form to a chosen person and sets a deadline. That person receives an email notification with a link to the form. Meanwhile the workflow halts. It does not move to the next step, it does not end, it simply waits until the person submits the form or the deadline is reached. When they submit it, the values become available to the rest of the workflow as variables, read with JSONPath by the step name, exactly like the output of another action.

Picture it with Priya. During her onboarding, the workflow needs to know which optional systems her manager wants her to have, something no trigger can know because it is a human judgment. So the workflow runs a Form action that assigns Priya's manager a short form. You can pre-fill parts of it because workflow variables can be mapped to form inputs, so the manager sees Priya's name and department already filled in and only has to choose the systems. If you named that step pickSystems and the form has a field for the chosen systems, a later step can read the answer from that step's output. The Form action also exposes a `Submitted` attribute, so a Compare Boolean operator can verify that the form was submitted before later logic relies on the answers.

Now the failure that you must design for, because it is not an edge case. What if the manager never fills in the form? The Form action has a submission deadline, with a maximum of 30 days. When the deadline is reached, a cancellation error is generated. If you want the workflow to continue, that error has to be handled. The action also supports reminder notifications before the deadline. So plan the non-response path on purpose: remind the person, route the cancellation to an error path, notify a backup, or end with a deliberate Failure that tells an operator what happened.

This connects straight back to the Wait action from Module 04. Both create a long-running workflow, but a Form action depends on a person's response rather than a clock. Human delay is normal, so the timeout path is part of the design, not an afterthought.

## Interactive Processes: a different human experience

ISC also has an Interactive Process, and this is different from assigning a normal Form action to someone by email.

An Interactive Process is built as a Delegated Interactive Workflow with an Interactive Trigger. A user who has been granted the associated Launcher starts the process manually from the Launchpad. The workflow then runs while that user stays inside the interactive experience. During the run, an Interactive Form can ask that launching user for input, and an Interactive Message can display progress or status information to that same user.

So an Interactive Message is not a Slack message and it is not a generic approve-or-reject prompt sent to someone elsewhere. It is a progress message displayed inside the Interactive Process to the user who launched it. If the workflow needs structured input from that user, use an Interactive Form. Interactive Form actions are tied to workflows that use the Interactive Trigger.

Picture a help desk analyst launching a "create shared mailbox" process from the Launchpad. The workflow might first display an Interactive Message saying that validation has started, then show an Interactive Form asking for the mailbox name and owner, then display another Interactive Message when the request completes. The person is not receiving a separate form assignment by email. They are actively driving a delegated workflow from the Launchpad.

The decision rule is simple. Use a normal Form action when a running workflow needs to assign a form to a specific user and wait for that person. Use an Interactive Process when a user should deliberately launch a delegated task from the Launchpad and interact with the workflow while it runs.

## Intake versus approval, and a trap to avoid

There is a second distinction that matters as much as the first, and it is about what you are asking the human to do.

Sometimes you want information. What systems does Priya need, what is the business justification, which cost center pays. That is intake, and a form is the right tool because a form is built to gather structured input.

Sometimes you want a governed decision. Should this person be allowed this access, yes or no, made by the right reviewer, with reminders if they stall, escalation or expiry behavior, and a record of who decided what. That is an approval, and here is the trap: you can almost build an approval out of a plain form with a "yes or no" field, and you usually should not. ISC already has approval tooling built for governed decisions.

The Approval Policy action is the main one for access-request approvals, and it is the mechanism behind Adaptive Approval. When a requested item is configured to use an enabled Workflow as its Approval Type, the Access Request Submitted trigger routes that request into your workflow, and an Approval Policy action inside the workflow makes the governed decision. The documented reviewer categories are Access Item Owner, Governance Group, Identity (Other), and Manager. The policy can use Single, Multi-Step, or Quorum approval types, with Serial or Parallel schemes available for Multi-Step review. The platform handles the approval process rather than forcing you to recreate it from a form.

For Priya, this is the mover moment. When her move to Finance leads to a request for Finance access, an Approval Policy can route that request through the appropriate approval process rather than treating the decision as an ordinary form submission.

There is a sibling for task-based decisions that are not standard access requests. The Generic Approval Policy action handles approval of a named task with a description and configured reviewer behavior. Keep the boundary clear: Approval Policy belongs to governed access-request approval, while Generic Approval Policy is for approving a workflow or task that sits outside normal access-request governance. Do not reach for one where the other belongs, and do not use a Form to recreate a native governed access approval, because a form does not produce the same governed record, reviewer routing, reminders, or expiry behavior that the access-request approval process provides.

Finally, when you need to act on a specific access request directly rather than route it through a policy, the Approve Access Request and Deny Access Request actions record that decision against the selected request. There is a documentation and UI naming trap here worth knowing before it costs you an afternoon. The input field may be labeled Access Request ID, but the documentation describes the value it actually expects as the Approval ID. If an Approve or Deny action fails or appears to act on nothing, this mismatch is a prime suspect, so confirm which identifier the action truly needs and read it from the right place rather than trusting the field label. Those actions also have their own documented timeout behavior, so treat them like other service-dependent actions and plan for failure.

So the judgment across this family is straightforward: use a form when you need information, use approval tooling when you need a governed yes or no, and use an Interactive Process when a user should launch and interact with a delegated workflow from the Launchpad.

> **Work It Out**
>
> Priya requests a sensitive Finance access profile that Acme requires a governed approval for. An engineer proposes assigning a Form to the access owner with an Approve or Reject dropdown, reading the answer, and then having the workflow grant or skip the access. Which human-in-the-loop mechanism actually belongs here, and what is wrong with the form approach?
>
> <details>
> <summary>Check your answer</summary>
>
> A governed access-request approval belongs to approval tooling, not a form. Configure the access profile to use an enabled Workflow as its Approval Type so Access Request Submitted routes the request into the workflow, and make the decision with an Approval Policy action. Choose from the documented reviewer categories: Access Item Owner, Governance Group, Identity (Other), or Manager. The form approach recreates governance the platform already owns. It does not produce the same governed approval record, reviewer routing, reminders, or expiry behavior, and it tempts the workflow into granting access directly rather than letting ISC's native access-request and provisioning processes own fulfillment. Use a form when you need information from a person, and approval tooling when you need a governed yes or no. Reserve Generic Approval Policy for approving a workflow task that is not an access request.
>
> </details>

## Designing the form itself

A quick word on building a good form, because a badly designed form is where human-in-the-loop processes go to die. Every field you add is one more thing standing between the person and the submit button, and one more chance for them to give up. So ask only for what you truly need.

Forms let you define inputs, mark some as required, and pre-fill fields from workflow variables so the person is not retyping things the workflow already knows. They also support conditional visibility, which means a field can appear only when it is relevant, for example showing a "which mailbox" field only after the person has said they need a shared mailbox. Good conditional visibility keeps a form short by hiding everything that does not apply to the choices made so far. For inputs that are a choice from a list, forms provide array inputs, where you configure the value that gets returned along with the label and sublabel that the person sees in the dropdown, so you can present friendly names while capturing the underlying identifiers your later steps need.

The whole art is restraint. A short, well-pre-filled form with only the relevant fields showing gets completed quickly. A long form that asks for everything, relevant or not, gets ignored, and an ignored form is the timeout failure from earlier waiting to happen.

## Before you move on

Design one human-in-the-loop step for Priya and defend your choice of tool. If Acme wants managers to kick off a "request temporary contractor access" process by submitting a form, is that a Form Submitted trigger or a Form action, and why are those two not interchangeable? If, in the middle of Priya's onboarding, the workflow needs her manager to pick which optional systems she gets, which action fits, and what attribute would you check before trusting the answer? If Acme instead wants a help desk analyst to launch a delegated task from the Launchpad and see progress while completing input, which pattern fits, and what is an Interactive Message actually used for there? When her Finance access needs a governed approval from the access owner, why is an Approval Policy the right choice rather than a form with a yes-or-no field? If those answers come readily, you understand human-in-the-loop workflows, and you are ready for Module 06, where we go deep on the data and JSONPath that all of this has been standing on.

---
[← Previous: Module 04 Actions](04-actions.md) | [Course home](../README.md) | [Next: Module 06 Data, Variables, and Expressions →](06-data-variables-and-expressions.md)
