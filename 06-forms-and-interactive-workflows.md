# Module 06: Forms, Approvals & Interactive Workflows

What changes when a Workflow needs a person?

Module 05 gave you a way to reason about actions:

```text
What job must happen?
        ↓
What input does the action need?
        ↓
What does success actually prove?
        ↓
What output should I inspect?
        ↓
What happens if the action errors?
```

Now add a human.

The process may need information that ISC cannot determine on its own. It may need someone to make a governed decision. Or it may need a user to deliberately launch a process and interact with it while it runs.

Those requirements can look similar on the surface because all of them involve a person.

They are not the same engineering problem.

The useful question is not:

> Which human-interaction feature should I add?

Start one level earlier:

> **What exactly do I need the person to do, and where does that person enter the process?**

---

## 1. Core: Start with the human-interaction decision map

Use this map before you think about individual action names.

```text
What do I need from the person?
        │
        ├── INFORMATION
        │
        │   Does the person's submission START the Workflow?
        │          │
        │          ├── Yes
        │          │    → Form Submitted trigger
        │          │
        │          └── No
        │               │
        │               ├── Is a running Workflow asking
        │               │   a selected person for input?
        │               │       → Form action
        │               │
        │               └── Does a user deliberately launch
        │                   a delegated process and interact
        │                   with it?
        │                       → Interactive Process
        │
        └── GOVERNED DECISION
                   │
                   └── Approval tooling
                       → Adaptive Approvals
```

This is a teaching map, not a replacement for current product documentation.

Its job is to keep you from choosing a feature merely because its name sounds close to the requirement.

You have already learned this engineering habit with triggers and actions:

```text
business requirement
        ↓
correct boundary
        ↓
product mechanism
```

Human interaction deserves the same discipline.

---

## 2. The human interaction contract

Module 05 taught you to read an action as a contract.

Use a similar contract whenever a Workflow involves a person:

```text
PURPOSE
What do I need from the person?

PARTICIPANT
Who is supposed to respond?

INITIATION
Who starts the interaction?

RESPONSE / EVIDENCE
What does completion actually prove?

NON-RESPONSE
What happens if the person does not respond?

DOWNSTREAM BOUNDARY
What is still not proven afterward?
```

Suppose Acme says:

> “We need Priya's manager involved.”

That is not enough information to choose a mechanism.

You still need to know what the manager is doing.

Are they supplying onboarding choices?

Approving sensitive Finance access?

Submitting the request that starts the whole process?

Those are different contracts.

---

## 3. Core: Intake: the person acts first

You met **Form Submitted** earlier as a specialized trigger.

Now you can place it in the human-interaction model.

A Form Submitted Workflow begins because somebody submitted a form.

```text
person
  ↓
submits form
  ↓
Form Submitted event
  ↓
Workflow starts
```

The person acts first.

The Workflow does not exist as a running execution waiting for that person. Their submission is the event that creates the execution.

Think of this as **intake: the front door**.

Acme might provide a form for requesting a shared mailbox:

```text
Mailbox name
Owner
Business reason
```

Someone submits it.

That submission starts the Workflow that processes the request.

The **Form Submitted** event includes submitted form data. The exact fields under that data depend on the form definition, so later logic should work from the actual technical keys and payload rather than assuming a field path from its display label.

The same habit from Module 02 still applies:

> **Inspect the data you actually received.**

### What does submission prove?

Keep the evidence boundary narrow.

```text
form submitted
        ≠
request fulfilled
```

Submission proves that the form-submission boundary occurred and supplied its documented data.

It does not prove whatever business process comes afterward has completed.

That distinction will keep appearing throughout this module.

---

## 4. Core: Assigned response: the Workflow acts first

Now reverse the direction.

Suppose Priya's onboarding Workflow is already running.

It has identity data. It knows her department. It has performed its earlier logic.

Then it reaches a question ISC cannot answer:

> Which optional systems does Priya's manager want included in her onboarding?

This is not intake.

The Workflow already exists.

It now needs information from a selected person.

That is where the **Form** action fits.

You will often hear it described naturally as the **Form action**.

The pattern is:

```text
Workflow already running
        ↓
needs information from a selected person
        ↓
Form action
        ↓
person receives the assigned form
        ↓
Workflow waits
        ↓
person submits
        ↓
Workflow resumes
```

Compare that with Form Submitted:

```text
FORM SUBMITTED

person
→ submission
→ Workflow starts
```

versus:

```text
FORM ACTION

Workflow starts earlier
→ Workflow asks person
→ person responds
→ same Workflow continues
```

The shared word **Form** should not hide that boundary.

## Priya's manager-input example

The Workflow can assign Priya's manager a short form asking which optional systems Priya needs.

Information the Workflow already knows can be supplied to the form rather than asking the manager to type it again.

So the manager might see:

```text
Employee: Priya Patel
Department: Finance

Select optional systems:
[ ... ]
```

The human contributes only the information the process is missing.

After successful submission, submitted form data becomes available to later Workflow logic.

Do not invent a universal JSONPath for those answers.

When you need an exact answer path, use the current Variable Selector or inspect the actual Form step output and reference the structure ISC produced.

The Form action also documents a `Submitted` attribute that can be evaluated with **Compare Boolean** when later logic needs to verify submission state.

That gives you another useful boundary:

```text
action completed
        ↓
inspect the response data you actually need
        ↓
validate before depending on it
```

A human entered the value.

That does not make the value automatically suitable for every later business decision.

---

## 5. Core: Human delay is part of the contract

A system action may finish in seconds.

A person may respond in five minutes, tomorrow, or not at all.

That changes the design.

Waiting for a human is not just a slower version of waiting for a deterministic action.

Human delay is part of the process contract.

The wrong model is:

```text
human step
→ eventually succeeds
```

Use this instead:

```text
human interaction
        │
        ├── response arrives
        │       → inspect response
        │       → continue deliberately
        │
        └── response does not arrive
                → follow that mechanism's
                  documented non-response behavior
```

That last line matters because there is **not one universal human-timeout rule in ISC**.

Different mechanisms resolve non-response differently.

## Form deadline

A Form action has a submission deadline.

When that deadline is reached, ISC generates a **cancellation error**.

If the Workflow must continue after that condition, its error handling has to account for it.

Conceptually:

```text
Form deadline reached
        ↓
cancellation error
        ↓
deliberate Error path if continuation is required
```

The Form action also supports reminder configuration.

Do not build your mental model around memorizing the current maximum deadline or reminder limits. Those are lookup facts.

Keep the engineering rule:

> **A Form deadline is part of the Form action's error contract.**

## Interactive Form cancellation

An **Interactive Form** has different documented cancellation behavior.

If the Interactive Form is canceled and Error handling is enabled:

```text
Interactive Form canceled
        ↓
Error branch
```

If Error handling is not enabled:

```text
Interactive Form canceled
        ↓
Workflow canceled
```

Notice the wording.

Do not casually replace **canceled** with **failed** simply because Module 05 taught generic failure handling.

The specific action contract wins.

## Approval-policy timeout

Approval policies introduce a different kind of non-response again.

An approval review can reach its configured review timeout.

That timeout is governed by the approval policy and can resolve according to its configured timeout action:

```text
review timeout
        ↓
configured policy outcome
        ↓
Approve
or
Expire
```

So this reasoning is unsafe:

```text
reviewer did not respond
        ↓
must mean denial
```

And this is also unsafe:

```text
reviewer did not respond
        ↓
must mean technical Workflow Error
```

The policy defines what that review timeout means.

That is why you inspect the contract instead of generalizing from another human step.

> **Engineering Habit:** When a Workflow waits for a person, ask how that specific mechanism represents non-response. Do not invent one global “human timeout” rule.

---

## 6. Core: Information is not approval

Now consider a different requirement.

Priya requests sensitive Finance access.

Acme requires an authorized reviewer to approve or deny it.

An engineer proposes this:

```text
Form question:

Approve access?
[ Yes ]
[ No  ]
```

Technically, a form can capture those words.

That does not make the process a governed approval.

The shape of the answer does not determine the governance meaning of the decision.

```text
Yes / No form field
        ≠
native approval merely because
the answer is binary
```

A Form collects form data.

Approval tooling creates and governs an approval process.

That difference matters more than whether both interfaces happen to present two choices.

If the requirement is:

> “Tell me which systems Priya needs.”

you need information.

If the requirement is:

> “An authorized reviewer must decide whether this access request is approved.”

you need governed approval.

Do not make a Form impersonate an approval mechanism simply because both involve a person clicking something.

---

## 7. Core / Working Engineer: Adaptive Approvals

ISC's **Adaptive Approvals** capability currently contains two policy types:

```text
Adaptive Approvals
│
├── Approval Policy
│      → access-request-based approval
│
└── Generic Approval Policy
       → task-based approval item
```

You do not need every reviewer type, approval mode, timeout value, or configuration option in your head.

First learn the boundary.

## Approval Policy

Use **Approval Policy** for the governed approval process around an access request.

At a high level, the pattern is:

```text
access item requires approval
        ↓
enabled Workflow selected as Approval Type
        ↓
Access Request Submitted
        ↓
Approval Policy defines the review process
        ↓
reviewers make their decisions
        ↓
configured policy reaches a result
        ↓
downstream Workflow logic can use that result
```

There is a wording distinction worth keeping precise.

The Approval Policy action does not personally “make” the human review decision.

It defines the governed review process.

The assigned reviewers make review decisions, and the configured policy determines when the approval reaches its resulting state.

For Priya's sensitive Finance access, that is the correct family of problem:

```text
access request
        ↓
governed review
        ↓
approval result
```

not:

```text
access request
        ↓
ordinary Form asking Yes / No
```

### Working Engineer: reviewer configuration

Approval Policy supports current reviewer and review-mode options that matter when you build a real approval design.

Those options are configuration knowledge, not the Core lesson.

Look them up when the requirement needs them.

Do not memorize a reviewer list and mistake that for understanding approval architecture.

## Generic Approval Policy

Sometimes the Workflow needs a governed decision that is not an ordinary access-request approval.

That is where **Generic Approval Policy** belongs.

It creates a native task-based approval item that reviewers can act on through ISC's approval experience.

The distinction is:

```text
Approval Policy
→ access-request approval process

Generic Approval Policy
→ task-based approval item
```

The two policy types do not have identical reviewer-category contracts, so do not assume that a reviewer option documented for one automatically exists for the other.

And one more boundary matters:

```text
Generic Approval Policy result = APPROVED
        ≠
the requested business task automatically happened
```

Later Workflow steps determine what to do with that result.

An approved decision is evidence for downstream logic.

It is not the downstream action itself.

---

## 8. Green Does Not Mean Done: human edition

Module 05 separated action success from later business outcomes.

Human interaction does not change that rule.

It gives you more boundaries to distinguish.

## Form

```text
form submitted
        ≠
business request fulfilled
```

## Approval

```text
approval decision recorded
        ≠
provisioning completed
        ≠
target state independently confirmed
```

This matters directly for Priya.

Suppose her Finance access request receives approval.

You now know something significant:

> The approval boundary was satisfied.

You do **not** yet know:

> The Finance application has provisioned the access and Priya can use it.

Those are later boundaries.

Module 05 gave you the larger ladder:

```text
Workflow action succeeded
        ≠
Access request approved
        ≠
Provisioning completed
        ≠
Target state independently confirmed
```

Module 06 fills in the human part without collapsing the rest.

## Generic approval

The same logic applies outside access requests:

```text
generic approval = APPROVED
        ≠
later Workflow task completed
```

The Workflow still has to honor that result with whatever downstream logic the design requires.

The useful engineering question remains:

> **What did this human step actually prove, and what still has to happen afterward?**

---

## 9. Working Engineer: Interactive Process

There is another human-participation pattern that does not look like either intake or an emailed Form assignment.

A user may deliberately launch a delegated process and interact with it as the Workflow reaches human-facing steps.

The current exact product term to anchor on is **Interactive Process**.

The surrounding model includes:

```text
Interactive Trigger
Launcher
Launchpad
Interactive Process
Interactive Form
Interactive Message
```

Conceptually:

```text
user has access to a Launcher
        ↓
user launches from Launchpad
        ↓
Interactive Trigger starts the Workflow
        ↓
Interactive Process runs
        ↓
Interactive Form / Interactive Message
present the interactive experience
```

A Launcher is associated with access granted through ISC, and only a Workflow using an **Interactive Trigger** can be attached to a Launcher.

You do not need the entitlement and Launcher administration details as Core knowledge.

What matters now is the interaction boundary.

## Form action versus Interactive Process

Compare them directly.

```text
FORM ACTION

Workflow is already running
        ↓
Workflow reaches out to a selected person
        ↓
person responds to assigned form
        ↓
Workflow resumes
```

```text
INTERACTIVE PROCESS

user deliberately launches process
        ↓
Workflow runs through Interactive Trigger
        ↓
same participating user interacts
with human-facing steps
```

That is the design distinction.

## Help-desk example

Suppose an Acme help-desk analyst has an approved Launcher for a delegated “Create Shared Mailbox” process.

The analyst opens the Launchpad and starts it.

The process may display information about what is happening, ask the analyst for structured mailbox details, continue its Workflow logic, and then present later status information.

The analyst is not waiting for a separate Form assignment email from a Workflow that started somewhere else.

They deliberately initiated the Interactive Process.

Also, do not teach this as requiring the person to remain continuously on the screen until the entire process finishes.

In-progress Interactive Processes can be returned to and continued from the Launchpad.

---

## 10. Working Engineer: Interactive Form and Interactive Message

Inside an Interactive Process, two names are easy to confuse.

## Interactive Form

An **Interactive Form** collects structured input from the participating user.

It belongs to Workflows using **Interactive Trigger**.

Conceptually:

```text
Interactive Process running
        ↓
needs structured input
        ↓
Interactive Form
        ↓
user supplies input
        ↓
process continues
```

It is not a substitute for a normal Form action assigned to some unrelated selected person.

Its participant is the user involved in the Interactive Process.

Its cancellation behavior also follows the Interactive Form contract described earlier:

```text
canceled
+ Error handling
→ Error branch

canceled
+ no Error handling
→ Workflow canceled
```

## Interactive Message

An **Interactive Message** displays progress or informational content inside the Interactive Process to the participating user.

For example:

```text
Validating mailbox name...
```

or:

```text
Your request has been submitted.
```

Do not think of it as:

- a Slack message;
- an email;
- a generic notification to somebody elsewhere;
- an ordinary external approval request.

It belongs to the Interactive Process experience.

Current product documentation is less useful for teaching exact acknowledgement/continuation mechanics than it is for establishing this stable purpose, so do not invent those details.

Keep the safe boundary:

> **Interactive Message presents in-process information to the person participating in the Interactive Process.**

---

## 11. Working Engineer: Design forms for completion

Once you choose the correct mechanism, the form itself still needs good engineering judgment.

A form is not better because it contains more fields.

Every extra question creates:

- more work for the person;
- another chance for misunderstanding;
- another value later logic may need to validate.

The better rule is:

> **Ask only for information the process genuinely needs and does not already know.**

Return to Priya's manager form.

If the Workflow already knows:

```text
Priya's name
department
manager
```

do not make the manager re-enter those values simply because the form can contain more fields.

Use supported pre-population where appropriate.

Forms also support design features such as required fields, conditional behavior, selectable values, and technical keys.

Those features should serve the process, not become the process.

A useful design might show an additional mailbox question only when the manager indicates that Priya needs a shared mailbox.

That keeps irrelevant questions out of the way.

And think ahead to later logic.

A friendly display label may not be the same value your Workflow needs downstream.

When later logic depends on submitted form data, work from the technical value ISC actually provides rather than guessing from what the human saw on the screen.

The art is restraint:

```text
short
relevant
pre-filled where appropriate
technically usable downstream
```

A form that respects the person's time is more likely to be completed correctly.

---

## 12. Advanced / Reference: Direct Approve and Deny actions

ISC also provides direct actions named:

- **Approve Access Request**
- **Deny Access Request**

You do not need these for first-pass mastery of Module 06.

They are useful to recognize because they expose a good Working Engineer lesson:

> Similar-looking identifiers are not automatically interchangeable.

Current documentation retains a naming mismatch worth verifying when you use these actions: the input may be labeled **Access Request ID**, while the documented value expected is the **Approval ID** associated with the request.

Do not memorize the mismatch as trivia.

Carry the engineering habit instead:

```text
action needs identifier
        ↓
read current action contract
        ↓
identify exact required object
        ↓
use that object's actual ID
```

These direct actions also have their own technical action-execution timeout.

That is a completely different concept from an Adaptive Approval **review-policy timeout**.

Keep those two clocks separate:

```text
APPROVAL POLICY TIMEOUT
human/governance review boundary
→ configured Approve or Expire outcome
```

versus:

```text
ACTION EXECUTION TIMEOUT
technical action/service boundary
→ action execution problem
```

Same word.

Different contract.

That distinction is more valuable than memorizing the current numeric timeout values.

---

## 13. The human-in-the-loop decision method

You now have enough pieces to use one method across this entire family.

When a requirement brings a person into the Workflow, work through these questions in order:

```text
1. What do I need from the person?
   Information or a governed decision?

2. When does the person enter the process?
   Before the Workflow starts?
   During an existing execution?
   By deliberately launching an Interactive Process?

3. Who initiates the interaction?
   Person?
   Workflow?
   Governed approval process?

4. Which mechanism owns that job?

5. What does completion actually prove?

6. What returned information or decision evidence
   will later logic depend on?

7. What happens if the person does not respond?
   Use that mechanism's specific contract.

8. What business boundary remains unproven?
```

You should be able to apply those questions even when you encounter a human-interaction feature that this course has not discussed.

That is more useful than memorizing a feature catalog.

---

## 14. Work It Out

## Scenario 1: Intake

Acme publishes a “Request Shared Mailbox” form.

A manager fills it out, and every submission should start a new Workflow.

Which mechanism owns the boundary?

Use **Form Submitted**.

The person's submission is the event that should start the Workflow:

```text
person submits
→ Workflow starts
```

A Form action would be the wrong direction because there is no already-running Workflow waiting to assign this form.

---

## Scenario 2: Priya's onboarding choices

Priya's onboarding Workflow is already running.

It now needs her manager to choose which optional systems Priya should receive.

Which pattern fits?

Use the **Form** action.

The Workflow already exists and needs structured information from a selected person:

```text
Workflow running
→ asks Priya's manager
→ waits
→ manager submits
→ Workflow resumes
```

Later logic should use the Form action's actual returned data rather than an invented answer path.

If the deadline is reached, that belongs to the Form action's cancellation-error contract.

---

## Scenario 3: Help-desk delegated process

An Acme help-desk analyst should deliberately launch a “Create Shared Mailbox” process from the Launchpad, enter information as the process reaches interactive steps, and see progress information inside that experience.

Which pattern fits?

Use an **Interactive Process** built around the **Interactive Trigger** and an appropriate Launcher.

Use **Interactive Form** when the participating analyst must supply structured input.

Use **Interactive Message** for progress or informational content inside the Interactive Process.

This is different from assigning a normal Form action to somebody from an already-running Workflow.

---

## Scenario 4: Sensitive Finance access

Priya requests a sensitive Finance access profile.

Acme requires a governed approval.

An engineer proposes sending the access owner a Form with an Approve/Reject dropdown.

What is wrong with the design?

The requirement is not merely “collect a yes/no value.”

It requires a governed access-request decision.

That belongs to the **Approval Policy** side of Adaptive Approvals.

A Form can capture the words Approve and Reject, but the binary shape of the response does not turn ordinary form data into the native approval process.

The Approval Policy defines the governed review process, reviewers make their review decisions, and the policy resolves the approval result.

That approval still does not prove provisioning completed.

---

## Scenario 5: Nobody responds

A human step reaches its deadline without a response.

An engineer says:

> “No problem. Human timeouts always go to the Error branch, so I will handle them all the same way.”

What assumption is hidden?

The engineer has generalized across mechanisms.

That is unsafe.

```text
Form deadline
→ cancellation error

Interactive Form cancellation
→ Error branch when Error handling is enabled
→ otherwise Workflow canceled

approval-policy review timeout
→ configured policy outcome
→ Approve or Expire
```

Human non-response is a normal design condition.

Its meaning still belongs to the specific mechanism's contract.

---

## 15. Checkpoint

You should now be able to hear a requirement involving a person and classify the interaction before reaching for a feature.

You should be able to explain:

```text
Form Submitted
→ person supplies intake that starts the Workflow

Form action
→ running Workflow asks a selected person for information

Interactive Process
→ user deliberately launches and participates
  in a delegated process

Approval Policy
→ governed access-request review

Generic Approval Policy
→ governed task-based approval item
```

You should also be able to defend three boundaries:

```text
information
≠
governed approval

human non-response
≠
one universal Error rule

approval completed
≠
provisioning completed
≠
target state independently confirmed
```

At this point you know how to choose the human-interaction boundary.

The next question is operational:

> The Workflow ran. What actually happened?

Module 07 moves into testing, execution history, and systematic diagnosis.

---

## Official References

- [Workflow Triggers - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-triggers.html)
- [Workflow Actions - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-actions.html)
- [Forms - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/forms/index.html)
- [Interactive Process - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-interactive-process.html)
- [Adaptive Approvals - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/adaptive_approvals/index.html)
- [Managing Launchers - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/access/launchers.html)

---

[← Previous: Module 05 Actions & Error Handling](05-actions.md) | [Course home](README.md) | [Next: Module 07 Testing, Debugging & Execution →](07-testing-debugging-and-execution.md)