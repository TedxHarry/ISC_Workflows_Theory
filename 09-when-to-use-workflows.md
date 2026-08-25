# Module 09: When to Use Workflows and When Not

Module 08 ended with a different kind of engineering question:

> **Should this requirement be implemented as a Workflow at all?**

Up to this point, you have spent most of the course learning how to reason **inside** a Workflow.

You learned how to:

- choose the correct event boundary;
- inspect actual data;
- route with operators;
- understand what actions really prove;
- build governed human interactions;
- test and diagnose executions;
- operate a Workflow responsibly over time.

Now we change perspective.

```text
Module 08

Can we operate this Workflow responsibly?

        ↓

Module 09

Should this requirement be a Workflow at all?
```

That is a harder question.

A Workflow can technically participate in many kinds of automation.

That is exactly why judgment matters.

The engineer who asks only:

> Can I make Workflow do this?

will eventually build something that works but belongs in the wrong place.

The better question is:

> **Which capability naturally owns the outcome, and does Workflow have an orchestration job around it?**

That is what this module teaches.

---

## 1. Core — From operating Workflows to choosing architecture

Imagine Priya moves from Sales to Finance.

Acme has several requirements around that move:

1. Priya should receive the standard access appropriate for Finance.
2. The Finance access owner should be notified.
3. A ticket should be opened for a manual downstream task.
4. If Priya later requests privileged Finance access, that request should go through the governed approval process.
5. Any approved target access change still has to be fulfilled.

You could look at that list and say:

> I know Workflows. I will build one Workflow that does all of it.

But that skips the architecture question.

These requirements do not all have the same natural owner.

Conceptually:

```text
standard Finance access
        ↓
access model

target access change
        ↓
provisioning

governed privileged request
        ↓
native access-request governance

notification + ticket orchestration
        ↓
Workflow may fit
```

That does not mean the capabilities are isolated from one another.

Quite the opposite.

A good ISC architecture can involve several capabilities working together.

The important skill is knowing **which one owns which responsibility**.

---

## 2. Core — “Can” is not “should”

Every module before this showed you what Workflows can do.

This one teaches the more valuable lesson:

> **“It can” is not “it should.”**

Technical possibility is not architecture.

Suppose you can build a Workflow that calculates a derived attribute.

That does not prove Workflow should own attribute calculation.

Suppose you can build a Workflow that grants standard employee access one identity at a time.

That does not prove Workflow should own Acme's standard-access model.

Suppose a scheduled Workflow can repeatedly call an API looking for a change.

That does not prove polling is the right design if a suitable event-driven mechanism already exists.

Architecture asks a different set of questions:

```text
WHAT OUTCOME IS REQUIRED?
        ↓
WHICH CAPABILITY OWNS THAT OUTCOME?
        ↓
DOES WORKFLOW ADD ORCHESTRATION?
        ↓
DOES WORKFLOW'S EXECUTION MODEL FIT?
        ↓
CAN I DEFEND THE CHOICE?
```

Notice what is missing.

We did not begin with:

> Which Workflow trigger should I use?

That question comes too early.

First decide whether Workflow belongs in the solution.

---

> **Engineering Habit**
>
> Do not start architecture with the capability you know best.
>
> Start with the outcome that must be owned.

---

## 3. Core — Find the primary owner first

When someone gives you an automation requirement, resist the urge to choose a tool immediately.

First ask:

> **What business state or process must actually change?**

Then ask:

> **Which capability naturally owns that state or process?**

That gives us the concept of a **primary owner**.

```text
REQUIREMENT
        ↓
WHAT MUST CHANGE?
        ↓
PRIMARY OWNER
```

But real architecture is rarely a one-tool competition.

After identifying the primary owner, ask a second question:

> **Does Workflow need to coordinate something around that owner?**

```text
PRIMARY OWNER
Which capability owns the business state or governed process?

        +

SUPPORTING ORCHESTRATION
Does Workflow coordinate work around it?
```

That distinction matters.

### Example: Priya moves to Finance

Suppose Acme says:

> When Priya moves into Finance, give her normal Finance access and tell the Finance access owner.

There are at least two outcomes here.

```text
Outcome 1
Determine Priya's standard Finance access

        ↓
access model owns it


Outcome 2
React to the move and send a notification

        ↓
Workflow may orchestrate it
```

So the architecture does not have to be:

```text
Access model
OR
Workflow
```

It can be:

```text
Access model
        +
Workflow
        +
Provisioning
```

with each capability doing the job it naturally owns.

That is a much stronger way to think than:

> Find the first tool that can technically perform every step.

---

## 4. Core — The capability decision map

Now that you have the reasoning model, we can examine the neighboring capabilities.

Do not memorize this as a feature comparison table.

For each capability, ask:

> **What does this capability naturally own?**

---

### Attribute-value calculation or manipulation → Transform

Transforms are the purpose-built configurable mechanism for calculating and manipulating attribute values.

Think:

```text
derive
normalize
format
combine
calculate
conditional value logic
fallback logic
```

For example:

```text
givenName = Priya
surname   = Patel

        ↓

displayName = Patel, Priya
```

A Transform can also contain conditional logic.

So do **not** use this old rule:

```text
Transform
→ cannot make decisions
```

That is wrong.

The architectural boundary is different:

```text
Transform
→ calculate / derive / normalize / manipulate values

Workflow
→ react to events and orchestrate actions,
   integrations, human steps, and process decisions
```

If you catch yourself building a Workflow whose real purpose is to calculate one identity attribute, pause.

You may be looking at **a Transform wearing a Workflow costume**.

---

### Standard access based on identity criteria → Role using Access Profiles

The access-model family contains several capabilities with different jobs.

Do not collapse them into one thing.

An **Access Profile** represents a bundle of access.

A **Role** can group Access Profiles and can use assignment criteria to determine who should receive that access automatically.

Conceptually:

```text
identity meets business criteria
        ↓
Role assignment logic
        ↓
Access Profiles describe the access
```

Suppose Finance employees should receive Acme's normal Finance application access because their identity attributes identify them as Finance workers.

That is fundamentally an access-model requirement.

A Workflow might notify someone that Priya entered Finance.

It should not become the primary mechanism that reconstructs standard access identity by identity when the access model owns that decision.

---

### Access driven by lifecycle status → Lifecycle State using Access Profiles

Lifecycle States represent employment or lifecycle conditions and can drive access changes associated with those states.

For example:

```text
Active
Leave of Absence
Terminated
```

can represent different lifecycle conditions.

So a requirement such as:

> When a person enters Acme's leaver state, apply the access behavior associated with that lifecycle condition.

naturally points toward Lifecycle State configuration and the access model.

Again:

```text
Lifecycle State
→ owns lifecycle-state-driven access behavior

Access Profile
→ represents bundled access

Workflow
→ may coordinate surrounding activity
```

A Workflow might open an offboarding ticket or notify Facilities.

That does not mean it should replace the lifecycle-access model.

---

### Governed access request and approval → Native access-request governance

Suppose Priya wants privileged Finance access.

The business requirement is not merely:

> Send somebody a form and wait for yes or no.

It is:

> Run a governed access-request process.

That process has a natural owner.

```text
governed access request
        ↓
native access-request governance
```

Workflow can participate through supported approval mechanisms or react around the request lifecycle.

But Workflow participation does not turn generic Workflow into a replacement for the native governance subsystem.

Keep the boundary simple:

```text
Native access-request governance
→ owns the governed request process

Workflow
→ may participate in supported approval logic
  or orchestrate around that process
```

Module 06 taught the mechanics.

Here we care only about architecture ownership.

---

### Fulfillment of supported target access/account changes → Provisioning

Eventually, some access or account state may need to change.

That fulfillment belongs to provisioning.

```text
approved or configured access change
        ↓
provisioning process
        ↓
target-side fulfillment
```

A Workflow can initiate or coordinate around provisioning-related work.

But Workflow does not replace the provisioning process itself.

Also be careful with the word **fulfillment**.

Do not assume every provisioning process means ISC directly performs every change through a connector in exactly the same way.

Depending on the source and configuration, fulfillment may involve different supported mechanisms.

The durable ownership boundary is:

> **Provisioning owns the fulfillment process for supported target access and account changes.**

---

### Event-driven bounded orchestration → Workflow may fit

Now we reach Workflow's natural territory.

Workflow is a strong candidate when the requirement looks like:

```text
event occurs
        ↓
inspect context
        ↓
make bounded decisions
        ↓
coordinate supported actions
        ↓
notify / integrate / route / request
```

Examples might include:

- react to an aggregation problem and notify an operator;
- react to Priya's department move and open a ticket;
- react to an identity event and coordinate several bounded actions;
- route a supported process according to event data;
- call an external service as one step in an event-driven process.

That is orchestration.

Workflow is good at connecting these boundaries without requiring you to build and operate a custom application for every automation.

---

### External event-driven processing → Event Trigger subscription plus external service may fit

Sometimes the event is useful, but the work belongs outside the managed Workflow service.

SailPoint supports Event Trigger subscriptions that can deliver supported events to external subscribers through supported subscription mechanisms.

Conceptually:

```text
supported Event Trigger
        ↓
external subscriber
        ↓
your service / processing environment
```

Do not assume this is the same surface as Workflow triggers.

There is overlap between the available event families, but:

```text
Workflow trigger catalog
        ≠
Event Trigger subscription catalog
```

and the mechanisms are not interchangeable.

A Workflow trigger starts managed Workflow orchestration.

A supported Event Trigger subscription delivers an event to an external subscriber.

That distinction becomes important when your own service, infrastructure, scaling model, libraries, or state management should own the processing.

---

### Purpose-specific code extension → Supported Rule type may fit

Rules require even more discipline.

Do not use:

```text
Nothing configurable fits
        ↓
use a Rule
```

That turns Rules into a generic escape hatch.

ISC Rules are supported, purpose-specific code extension points.

A better decision is:

```text
supported configurable capabilities do not solve the requirement
        ↓
is there a supported Rule type
for this specific extension point and purpose?
        ↓
if yes, consider that Rule
```

Rules use BeanShell and execute in defined contexts depending on Rule type.

They also carry code lifecycle and support considerations.

The important architecture lesson is not that Rules are the “most powerful” feature.

Remove that idea from your mental model.

The better model is:

> **A Rule is code used at a supported ISC extension point for a documented purpose, and should be considered deliberately rather than treated as a universal fallback.**

---

### Put the map together

At a high level:

```text
Need to calculate or manipulate attribute data?
        ↓
Transform


Need standard access based on shared identity criteria?
        ↓
Role, using Access Profiles


Need lifecycle-status-driven access behavior?
        ↓
Lifecycle State, using Access Profiles


Need a governed request and approval process?
        ↓
Native access-request governance
        +
Workflow may participate


Need fulfillment of supported target access/account changes?
        ↓
Provisioning
        +
Workflow may initiate or coordinate around it


Need to react to an event and coordinate bounded work?
        ↓
Workflow may own the orchestration


Need custom processing, libraries, application state,
or execution characteristics poorly matched to Workflow?
        ↓
Consider an external service / integration


Need code at a specific supported ISC extension point?
        ↓
Consider the applicable supported Rule type
```

Notice that several boxes can belong to the same business process.

That is intentional.

---

## 5. Core — Workflow as an orchestrator, not a replacement engine

Return to Priya's move into Finance.

Imagine Acme's complete requirement is:

> When Priya moves into Finance, make sure standard access follows the Finance model, tell the Finance access owner, and open a ticket for a manual application review.

A weak architecture starts with:

> How do I build all of that in Workflow?

A stronger architecture separates ownership.

```text
Priya moves to Finance
        |
        +------------------------------+
        |                              |
        v                              v
Access model                     Workflow
determines standard access       reacts to the move
        |                              |
        v                              +--> notify Finance owner
Provisioning                           |
fulfills access change                 +--> open review ticket
```

No capability needs to pretend it owns the whole business process.

### Add a governed request

Now suppose Priya later requests Finance Administrator access.

That adds another owner:

```text
Priya requests privileged access
        ↓
native access-request governance
        ↓
governed decision
        ↓
provisioning fulfills approved change
```

Workflow may participate in supported approval logic or react around the request lifecycle.

But the architecture still has clear ownership.

### The key question

When you see several ISC capabilities in one design, do not ask:

> Which one is the real tool?

Ask:

> **Which responsibility does each one own?**

That is how mature IAM systems are usually composed.

---

## 6. Core — When Workflow is a good fit

So when should Workflow move toward the center of the design?

There is no magic checklist that certifies an architecture.

But several signals make Workflow a natural candidate.

### 1. There is an identifiable event

Something meaningful happens.

For example:

```text
identity changes
aggregation completes
provisioning completes
scheduled point arrives
supported external interaction occurs
```

You can identify what starts the orchestration and what that event actually proves.

### 2. The work is orchestration

The requirement is not merely value calculation or access modeling.

It involves coordinating steps.

For example:

```text
event
→ inspect
→ branch
→ notify
→ call
→ request
→ end
```

### 3. The work is bounded

You can explain where this orchestration starts and where its responsibility ends.

That matters because **Green Does Not Mean Done** still applies.

A Workflow can complete its part successfully without proving that every downstream business state has completed.

### 4. The required actions and integrations fit supported mechanisms

Workflow should not become an excuse to invent an execution environment that the product does not provide.

If the required work naturally fits the supported Workflow model, that is a positive signal.

### 5. The operating characteristics are reasonable

From Module 08, you already know to think about:

- volume;
- payload and definition boundaries;
- schedule behavior;
- external dependencies;
- runtime evidence;
- maintainability.

You do not need the numeric limit catalog again.

You need to ask whether the requirement's normal operating shape fits the Workflow environment.

### 6. The design does not fundamentally require an application runtime

If the heart of the requirement is:

- substantial custom code;
- specialized libraries;
- durable application state;
- heavy computation;
- specialized correlation infrastructure;
- unusually large-scale processing;

that is a signal to consider another execution environment.

That is an **architecture warning**, not automatically a statement that the requirement is technically unsupported.

There is a difference between:

```text
documented limit exceeded
→ technically blocked
```

and:

```text
design fights the natural operating model
→ poor architectural fit
```

A good engineer knows the difference.

---

> **Engineering Habit**
>
> “Supported” and “well designed” are not synonyms.
>
> A design can remain technically possible while becoming architecturally awkward.

---

## 7. Core — Anti-patterns as architecture warnings

The old anti-pattern names are useful because they make bad shapes easy to recognize.

But do not memorize them as:

> This pattern is bad because the course said so.

Diagnose them.

For each one ask:

```text
What outcome is actually required?
        ↓
Which capability naturally owns it?
        ↓
Why is Workflow replacing that owner?
        ↓
Does Workflow still have a supporting role?
```

---

### The attribute-shaper

Shape:

```text
Workflow starts
→ Get Identity
→ Define Variable
→ several calculations
→ maybe HTTP Request
→ produce one derived value
```

Diagnosis:

> What is the business outcome?

Calculate an attribute value.

Natural owner:

> Transform.

Remember: the problem is **not** that Transforms are incapable of conditional logic.

The problem is that attribute-value computation has a purpose-built owner and does not inherently require an event/action orchestration engine.

Workflow might still react to an event involving the resulting attribute.

It just should not become the value engine by accident.

---

### Birthright-by-Workflow

Shape:

```text
person matches normal employee condition
        ↓
Workflow
        ↓
grant the same standard access
```

Diagnosis:

> What state is being owned?

Who should receive standard access based on identity or lifecycle criteria.

Natural owner:

> Access model.

That may mean a Role using Access Profiles or lifecycle-state-driven access configuration depending on the requirement.

Workflow might notify someone or coordinate an exception.

It should not quietly replace the model that answers **who should have standard access**.

---

### The bulk processor

Shape:

```text
schedule
        ↓
load huge population
        ↓
process person 1
process person 2
process person 3
...
```

Diagnosis:

> What dominates the requirement?

Large recurring population processing.

That should immediately make you examine the operating model.

From Module 08, you know Workflows have execution and operating boundaries.

You do not need to memorize those numbers again here.

Ask instead:

> Is Workflow really the natural execution environment for this workload?

High volume is not a magical word that makes Workflow universally unsupported.

It is an architecture signal.

If large-scale processing dominates the requirement, consider a processing environment designed for that responsibility.

---

### The poller

Shape:

```text
every few minutes
        ↓
ask whether something changed
        ↓
nothing changed
        ↓
wait
        ↓
ask again
```

Diagnosis:

> Is repeated checking fundamental, or is there a suitable supported event?

If a suitable event-driven mechanism exists, reacting to the event is usually cleaner than repeatedly checking for it.

That might mean a Workflow trigger.

For external processing it might mean a supported Event Trigger subscription.

Do not invent an event that does not exist.

But when an appropriate one does exist, prefer the real signal over unnecessary polling.

---

### The no-filter firehose

Shape:

```text
many events occur
        ↓
every event starts Workflow
        ↓
later operator discovers
most were irrelevant
```

If the trigger supports an appropriate filter using data available at that boundary, move relevance earlier.

```text
event occurs
        ↓
supported trigger filter
        ↓
irrelevant event does not start Workflow
```

That reduces unnecessary Workflow starts and operational noise.

Do not make the lesson depend on an invented execution-accounting formula.

The durable fact is simpler:

> **When the appropriate trigger filter excludes an irrelevant event, that event does not start the Workflow.**

---

### Rebuilding governed approvals

Shape:

```text
generic form
→ custom yes/no handling
→ manual grant logic
→ home-grown recordkeeping
```

while the real business requirement is:

> Govern an access request and approval.

Diagnosis:

> Native access-request governance owns that process.

Workflow can participate through supported approval mechanisms.

It should not replace the governance subsystem merely because you can draw an approval-shaped sequence.

---

### The mega-Workflow

Shape:

```text
one enormous Workflow
→ onboarding
→ access
→ tickets
→ notifications
→ cleanup
→ unrelated exceptions
→ everything else
```

The problem is not a magic step count.

The problem is that ownership and boundaries disappear.

Ask:

- Are several independent business outcomes being forced into one execution?
- Which capabilities naturally own those outcomes?
- Which parts are actually orchestration?
- Which responsibilities could evolve or fail independently?

A huge canvas is often evidence that architecture boundaries were never identified.

Module 10 will give you reusable Workflow shapes.

For now, learn to recognize when one Workflow is pretending to be an entire system.

---

### Hard-coded credentials

If an integration needs a credential, do not treat embedding a secret directly into a definition as normal architecture.

Use supported secure parameter handling where the action and supported mechanism allow it.

Remember the Module 08 boundary:

```text
supported secure parameter handling
        ≠
universal secret manager for every possible credential
```

The architecture lesson is to make credential handling an explicit dependency rather than an invisible string buried in automation.

---

## 8. Working Engineer — When constraints change the architecture

Module 08 treated constraints as an operations problem:

> What operating envelope must this production Workflow stay inside?

Module 09 asks another question:

> **What if the requirement itself naturally pushes against that envelope?**

Then an operating constraint becomes an architecture signal.

```text
requirement
        ↓
natural operating characteristics
        ↓
compare with Workflow's operating model
        ↓
good fit?
```

### Scale

Suppose someone asks:

> Recompute an enormous dataset for a large population every night.

You should not begin by drawing a giant loop.

Ask what owns that processing job.

If high-volume batch computation is the central requirement, Workflow may be the wrong execution environment even if some form of processing could technically be constructed.

### Duration

Suppose the process fundamentally relies on long-running external computation.

Again, do not begin with:

> Which action can I keep alive longest?

Ask whether Workflow should be coordinating the request while another system owns the long-running work.

### State

Suppose the process requires durable application state, sophisticated correlation across many independent events, and custom recovery logic.

Those requirements should influence architecture before implementation begins.

Module 11 will go deeper into replay, concurrency, retries, and failure behavior.

Here, simply recognize that a state-heavy process may be signaling:

> This wants an application or service, not just a Workflow definition.

### Custom code and libraries

Workflow is not an arbitrary custom-library runtime.

If a specialized library or substantial custom algorithm is fundamental to the requirement, an external execution environment may be more natural.

Or, for a specific ISC extension point, there may be an applicable supported Rule type.

Do not jump from:

```text
Workflow feels awkward
```

to:

```text
therefore Rule
```

The Rule still has to exist as a supported extension type for the job you need.

---

### Constraints are not only an operations concern

This is the bridge between Modules 08 and 09:

```text
Module 08

We chose Workflow.
Can we operate it safely?

        ↓

Module 09

The requirement naturally strains that operating model.
Should we choose Workflow in the first place?
```

That is architecture judgment.

---

## 9. Work It Out — Choose the capability for Acme

Now apply the full model.

For every requirement, answer four things:

```text
PRIMARY OWNER:
Which capability owns the main business state or process?

WORKFLOW ROLE:
primary orchestration / supporting / none

WHY:
Why does that ownership make sense?

WHY NOT THE OBVIOUS ALTERNATIVE:
What tempting capability would be weaker, and why?
```

Try each one before reading the discussion.

---

### Scenario 1 — Format every display name

Acme wants every identity's display name formatted as:

```text
Last, First
```

Think before reading on.

**PRIMARY OWNER:** Transform

**WORKFLOW ROLE:** None for the calculation itself.

**WHY:** The requirement is attribute-value calculation and formatting.

**WHY NOT WORKFLOW:** Starting an orchestration process merely to derive a value gives an attribute-computation problem to the wrong owner.

Conditional complexity would not by itself change that answer. Transforms can contain supported conditional value logic.

---

### Scenario 2 — Give employees standard access

Acme says:

> Every employee who meets the standard business criteria should receive the normal employee access package.

**PRIMARY OWNER:** Access model — typically a Role using Access Profiles for identity-criteria-based assignment.

If the requirement is specifically driven by employment/lifecycle status, Lifecycle State configuration may own that part.

**WORKFLOW ROLE:** Possibly supporting, for notifications or surrounding orchestration.

**WHY:** The business state being owned is standard access entitlement based on identity or lifecycle criteria.

**WHY NOT WORKFLOW:** Granting the same normal access identity by identity in Workflow rebuilds access-model behavior as orchestration.

---

### Scenario 3 — Priya moves to Finance

Requirement:

> When Priya moves into Finance, notify the Finance access owner and open a ticket for a manual application review.

**PRIMARY OWNER:** Workflow for this orchestration.

**WORKFLOW ROLE:** Primary orchestration.

**WHY:** An identifiable event occurs, the process inspects context, then coordinates bounded notification and integration work.

But be precise:

```text
Workflow
→ owns notification and ticket orchestration

Access model
→ still owns normal Finance access

Provisioning
→ still owns fulfillment of supported target access changes
```

**WHY NOT ACCESS MODEL ALONE:** The access model can own standard access, but the ticket and notification are orchestration around that state change.

---

### Scenario 4 — Govern privileged Finance access

Requirement:

> Priya should be able to request Finance Administrator access, and that request must go through Acme's governed approval process.

**PRIMARY OWNER:** Native access-request governance.

**WORKFLOW ROLE:** Supporting where a supported approval Workflow is appropriate, or surrounding orchestration is needed.

**WHY:** The business process is a governed access request and decision.

**WHY NOT GENERIC WORKFLOW ALONE:** A custom form and home-grown approval chain would replace governance that has a purpose-built owner.

---

### Scenario 5 — Fulfill an approved target access change

Requirement:

> Once the appropriate process determines that Priya should receive supported target access, make the required account/access change.

**PRIMARY OWNER:** Provisioning.

**WORKFLOW ROLE:** Supporting or initiating where appropriate.

**WHY:** Provisioning owns the fulfillment process for supported target access/account changes.

**WHY NOT WORKFLOW AS THE FULFILLMENT ENGINE:** Workflow can coordinate the request or surrounding work, but that does not make it the owner of provisioning itself.

---

### Scenario 6 — Recompute a large risk dataset every night

Requirement:

> Recompute a large risk dataset for eighty thousand identities every night using substantial custom processing.

**PRIMARY OWNER:** Likely an external processing service or purpose-built integration environment.

**WORKFLOW ROLE:** Possibly trigger or coordinate a bounded part of the process if that adds value.

**WHY:** Large recurring processing and substantial custom computation dominate the requirement.

**WHY NOT WORKFLOW:** This is a strong architecture warning that the requirement may fit another execution environment better.

Notice the wording.

We did **not** say:

> Workflows universally cannot process eighty thousand identities.

That would turn an architecture heuristic into an unsupported product guarantee.

The engineering conclusion is:

> Investigate the operating characteristics before choosing Workflow as the processing engine.

---

### Scenario 7 — Send identity events to external analytics

Requirement:

> When supported identity-created events occur, Acme's analytics service should receive them and handle the processing in its own application.

**PRIMARY OWNER:** External service for the analytics processing, with a supported Event Trigger subscription as the event-delivery mechanism where applicable.

**WORKFLOW ROLE:** None unless separate orchestration inside ISC is also required.

**WHY:** The event needs to leave ISC so Acme's own service can process it using its own runtime and architecture.

**WHY NOT ASSUME A WORKFLOW TRIGGER:** Workflow triggers and Event Trigger subscriptions overlap in places but are not one identical or interchangeable event catalog.

Choose the mechanism that owns the required interaction.

---

### Scenario 8 — Compute a value that supported Transforms cannot express

Requirement:

> Acme needs a value calculation that the supported Transform capabilities do not solve.

Do not answer automatically:

> Rule.

The correct next question is:

```text
Is there a supported Rule type
for this specific extension point and purpose?
```

If yes, that Rule may be considered.

If no, the architecture may need another solution.

**PRIMARY OWNER:** Depends on the supported extension point.

**WORKFLOW ROLE:** Not automatically relevant simply because Transform did not solve the value calculation.

**WHY:** Rules are purpose-specific supported extension points, not a generic fallback programming environment.

**WHY NOT “Transform failed, therefore Workflow or Rule”:** Failure of one candidate does not remove the need to establish who should own the requirement.

---

## The pattern behind all eight answers

You were never really answering:

> Which feature can perform these steps?

You were answering:

```text
What outcome is required?
        ↓
Who naturally owns it?
        ↓
Does Workflow add orchestration?
        ↓
Does Workflow's execution model fit?
        ↓
Why is this architecture better
than the obvious alternative?
```

That is the real Module 09 skill.

---

## 10. Checkpoint — Defend the architecture

You should now be able to hear a new requirement and reason through five questions.

### 1. What outcome is actually required?

Do not begin with implementation.

Name the state or process that must change.

### 2. Which capability owns that outcome?

Examples:

```text
attribute value
→ Transform

standard identity-criteria-driven access
→ Role using Access Profiles

lifecycle-status-driven access
→ Lifecycle State using Access Profiles

governed access request
→ native access-request governance

target access/account fulfillment
→ provisioning

event-driven bounded orchestration
→ Workflow may fit

external custom processing
→ external service may fit

supported code extension point
→ applicable Rule type may fit
```

### 3. Does Workflow have a supporting orchestration role?

Do not force a false either/or choice.

Architecture can be compositional.

```text
PRIMARY OWNER
        +
SUPPORTING ORCHESTRATION
```

### 4. Does the Workflow execution model fit the requirement?

Think about:

- scale;
- duration;
- state;
- dependencies;
- custom processing;
- maintainability;
- operating constraints.

Use current product documentation when those boundaries matter.

### 5. Can you defend why the alternative is worse?

A junior engineer says:

> I picked Workflow.

A stronger engineer says:

> Workflow owns the event-driven orchestration, while the access model owns standard access and provisioning owns fulfillment. Putting all three responsibilities into Workflow would blur ownership and duplicate purpose-built capabilities.

That is architecture reasoning.

---

> **Engineering Habit**
>
> Reach for the most purpose-built supported capability first.
>
> Then ask whether Workflow adds useful orchestration around it.

---

## 11. From architecture choice to Workflow patterns

You now know how to decide whether Workflow belongs in a solution.

That gives Module 10 a clean starting point.

```text
Module 09

Should Workflow participate?
What should it own?

        ↓

Module 10

Workflow belongs here.
What proven Workflow shape should we begin from?
```

Module 10 is not about proving Workflow is the right capability.

That decision should already have been made.

Instead, you will begin looking at reusable patterns:

- joiner, mover, and leaver orchestration;
- data-quality and operations patterns;
- governance patterns;
- integration patterns;
- other Workflow shapes engineers repeatedly encounter.

Do not copy a pattern merely because it resembles your requirement.

Keep this module's questions with you:

```text
WHAT OUTCOME?
        ↓
PRIMARY OWNER
        ↓
SUPPORTING ORCHESTRATION
        ↓
WORKFLOW FIT
        ↓
DEFEND THE ARCHITECTURE
```

That is how you prevent a useful automation tool from becoming the answer to every IAM problem.

---

## Official References

- [Transforms — SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/transforms/)
- [Access Overview — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/access/index.html)
- [Provisioning Overview — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/provisioning/index.html)
- [Access Request Overview — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/requests/index.html)
- [Adaptive Approvals Overview — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/adaptive_approvals/index.html)
- [Using Event Triggers — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/common/event_triggers.html)
- [Workflow Triggers — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-triggers.html)
- [Rules — SailPoint Developer Community](https://developer.sailpoint.com/docs/extensibility/rules/)
- [Managing Workflows — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/workflows/workflow-manage.html)
- [Managing Parameter Storage — SailPoint Documentation](https://documentation.sailpoint.com/saas/help/parameter_storage/managing_parameters.html)

---

[← Previous: Module 08 Operations, Limits & Governance](08-operations-limits-and-governance.md) | [Course home](README.md) | [Next: Module 10 Real-World Workflow Patterns →](10-use-case-patterns.md)
