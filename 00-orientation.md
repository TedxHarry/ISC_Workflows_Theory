# Module 00: Orientation

Where workflows sit in Identity Security Cloud, what you should already know, and how workflows relate to the other tools around them.

Before we touch a single trigger or action, I want you to have a clear picture in your head of what workflows are for and where they live. If you get this picture right, everything later in the course has somewhere to attach. If you skip it, workflows can feel like a bag of loose features. So let us slow down here for a few minutes.

## A story we will keep coming back to

All the way through this course we will follow one company and one person. The company is Acme. The person is Priya. Priya gets hired into Acme, so on day one a new identity appears for her in Identity Security Cloud. A few months later she moves from the Sales team to the Finance team, so her identity changes. Later still she leaves the company, so her identity is disabled and her access has to be cleaned up.

Joiner, mover, leaver. Almost every real workflow you will ever build is a reaction to a moment like one of those. Keeping Priya in mind gives us something concrete to point at every time a new idea shows up, instead of talking in the abstract. When you read "an identity attribute changed," do not picture a diagram. Picture Priya moving to Finance.

## What a workflow actually is

Identity Security Cloud, which most people shorten to ISC, spends its day watching identities and access. It aggregates accounts from your sources, it works out who should have what, it runs certifications, it fulfills access requests. All of that is the core of the product.

A workflow is the part that lets you say: when this specific thing happens, do these specific things automatically. The official definition is plain, and I like it: a workflow is a set of steps that run every time a certain event occurs.

That is the whole idea. Something happens. Steps run. No human has to remember to do it.

Think about what Acme did before they had workflows. When Priya was hired, someone in IT got an email, then they logged into a few systems by hand, then they sent a welcome message, then they opened a ticket so the facilities team could set up her desk. Every one of those steps depended on a person noticing and remembering. People are busy. Steps get missed. New hires sit for two days without an account.

A workflow takes that whole chain and makes it happen the instant Priya's identity is created. That is the problem workflows solve. They turn "someone should really do this every time" into "this happens every time, on its own, in seconds." When you find yourself describing a task with the words "every time X happens, we always do Y," you have almost certainly found a job for a workflow.

## What you should already know before this course

I am going to assume three things, and I want to be honest about them so you can shore up any gaps now rather than get stuck later.

First, the ISC identity model at a high level. You should know that an identity is the central record for a person, that it has attributes such as department or lifecycle state, and that it is connected to accounts on various sources. You do not need to be an expert. You just need to not be surprised when I say "identity" or "account" or "source."

Second, comfort reading JSON. This one matters more than people expect, so I will not pretend otherwise. Everything that moves through a workflow is JSON. If a block of curly braces and quoted keys makes you nervous, spend an hour with a JSON primer before Module 01. It will pay you back many times over, because the single most common workflow bug in the world is reaching for a piece of data that is not shaped the way you thought it was.

Third, a basic idea of what a REST call is. You should know that software can call other software over the web by sending a request to a URL and getting a response back. That is enough. When we get to the HTTP Request action in Module 04, we will build on exactly that idea and nothing fancier.

You do not need a tenant to learn any of this. That is the point of a theory course. A tenant helps when you move to the labs, but the understanding comes first, and understanding is portable.

## Turning workflows on, and the wait that surprises people

There is one practical detail worth knowing at the very start, because it trips up almost everyone the first time. When you enable workflows in a tenant for the first time, they do not become active instantly. It takes about two hours for the feature to fully switch on.

This is not a bug and it is not something you did wrong. It is just how the platform provisions the capability behind the scenes. I mention it now so that if you ever enable workflows and then sit there wondering why nothing fires, you remember this paragraph, make a coffee, and come back later. Knowing a normal delay is normal is a small thing that saves a lot of confused debugging.

## Where workflows sit among the other tools

Here is the part that separates people who understand ISC from people who only understand workflows. ISC gives you several tools that can change or react to identity data, and workflows are only one of them. If you reach for a workflow every time, you will sometimes pick the wrong tool and build something fragile. So let us map the neighborhood. We will go deep on this decision in Module 09. For now I just want you to know who the neighbors are.

Transforms are for shaping attribute values. When Priya's identity is built, a transform can take her raw first name and last name from a source and turn them into a clean display name, or force a department code into upper case. Transforms are quiet, declarative, and they run as part of how an identity or an account is calculated. They do not make decisions or call other systems. They just shape data. If your task is "the value should look like this instead of that," you probably want a transform, not a workflow.

Rules are for logic that transforms cannot express, usually written as code and often reviewed by SailPoint before they run in your tenant. Reach for a rule only when the simpler tools genuinely cannot do the job. Rules are powerful and heavier to maintain, so they are a last resort, not a first instinct.

Provisioning is the machinery that actually creates, updates, and disables accounts on your connected sources. When Priya leaves and her accounts get disabled, provisioning is what carries that out. A workflow might decide that something should happen, but provisioning is often the thing that makes the account change real on the far system.

Event trigger subscriptions are the closest relative of all, and the relationship is worth getting straight. Under the hood, ISC publishes events such as "identity created." A workflow is essentially one kind of subscriber to those events. You could instead subscribe your own external service directly to an event and receive it as a webhook, and then do whatever you want in your own code. So the honest way to think about it is this: a workflow is the managed, no code way to react to an event inside ISC, and a direct event trigger subscription is the do it yourself way to react to the same event in your own system. Same underlying events. Different amount of control and different amount of work. We will return to when each one fits.

You do not need to memorize all of this today. You just need to hold one sentence: workflows are the automation layer that reacts to events, and they live next to transforms, rules, provisioning, and raw event subscriptions, each of which is better at a different kind of job.

## Before you move on

Here is a small thing to do in your head, not on a keyboard. Picture three tasks at Acme. One: whenever a new identity is created, send the hiring manager a welcome note. Two: whenever an identity is built, make sure the display name is formatted as "Last, First." Three: whenever an account is disabled, actually remove it from the target system. For each one, ask yourself which tool from this module is the natural fit. If you can say "workflow, transform, provisioning" and give yourself a reason for each, you are ready for Module 01, where we open up a workflow and watch the data move through it.

---
[Course home](../README.md) | [Next: Module 01 The Workflow Model →](01-the-workflow-model.md)
