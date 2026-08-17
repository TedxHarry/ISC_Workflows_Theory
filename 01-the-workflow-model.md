# Module 01: The Workflow Model

The core anatomy of every workflow and how data moves through it.

Most explanations of workflows start by naming the parts. We are going to do the opposite. First I want you to watch one whole workflow work, start to finish, so you have a complete thing in your head. Then we will take it apart and name the pieces. A part makes a lot more sense once you have seen the job it does.

So let us build Priya a welcome email.

## One whole workflow, start to finish

Here is the task. When Priya is hired at Acme, a new identity is created for her in ISC. The moment that happens, we want to send her a short welcome email. That is the entire automation. Small on purpose, because a small example you fully understand beats a big one you half follow.

When Priya's identity is created, ISC hands the workflow a piece of JSON that describes what just happened. It looks like this:

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

Read that slowly. There is an `identity` object holding the type, the internal id, and the login name. There is an `attributes` object holding the everyday fields, first name, last name, email, department. The identity created event carries all of the identity attributes as they are set up in your identity profile, so at Acme the attributes block will hold whatever Acme configured. For Priya today it holds these four.

This JSON is the seed. Everything the workflow does, it does by reading from this seed and adding to it.

Now the workflow does its one job. It runs a Send Email step. In that step we have to fill in who the email goes to and what it says. We do not type Priya's address by hand, because tomorrow this same workflow has to work for the next new hire, and the one after that. Instead we point at the data. For the "to" field we point at the email in the seed. For the greeting we point at the first name. When the step runs for Priya, those pointers resolve to `priya.patel@acme.com` and `Priya`, and out goes the email. When it runs for the next hire, the same pointers resolve to their address and their name. We wrote it once. It works for everyone.

That is a complete workflow. An event happened, data arrived, a step read that data and acted on it. Hold that picture. Now we name the parts.

## The three kinds of building block

Every workflow is made of three kinds of thing: one trigger, some number of actions, and some number of operators. Our welcome email used a trigger and an action and did not need an operator yet. Let us take them one at a time.

The trigger is what starts the workflow. There is exactly one per workflow, always. It is the "when this happens" part. In our example the trigger was Identity Created. The trigger is also where the seed JSON comes from. The event supplies that first block of data, and the rest of the workflow reads from it. A workflow with no trigger cannot exist, because nothing would ever set it going. Module 02 is entirely about triggers and the full set you can choose from.

Actions are the steps that do something. Sending the email was an action. Actions are the verbs of a workflow. Some actions reach outside ISC, like sending mail or calling another system's API. Some actions fetch more data, like looking up an identity's full details. Some actions change things, like managing an account or an access assignment. Whenever a workflow actually affects the world, an action is doing it. Module 04 walks through the families of actions.

Operators are the steps that make decisions and shape data without reaching outside. An operator is how a workflow asks a question and takes different paths based on the answer. If we wanted to send the welcome email only to people in the Sales department, we would add an operator that compares the department to "Sales" and lets the workflow continue only when it matches. Operators are the thinking of a workflow. Module 03 covers them in full.

A clean way to remember it: the trigger is when, actions are do, operators are decide and shape. Almost everything you build is some arrangement of those three.

## How data moves: the payload that grows

Here is the idea that makes workflows finally click for most people, so I want to give it room.

A workflow is not just a list of steps that run in order. It is a piece of JSON that travels through those steps and grows as it goes. The trigger drops the seed data in at the start. Then each step can read everything that came before it, and each step can add its own output to the pile. By the time you are deep in a workflow, the data available to you is the seed plus the output of every step that already ran.

This is why order matters so much, and it leads to one hard rule that you must burn into memory: a step can only use data from steps that ran before it. You cannot reach forward. If step five produces a value, step two cannot see it, because when step two runs, step five has not happened yet. This is not an arbitrary restriction. It falls straight out of the fact that the data is being built up as the workflow moves forward. There is nothing there yet to read.

In our welcome email, the Send Email step could read the trigger's seed because the trigger came first. If we had somehow put the Send Email step before the trigger, there would be no email address to read, because nothing would have supplied it. Forward references are the single most common beginner mistake, and now you know exactly why they fail.

## Pointing at data: a first look at JSONPath

So how does a step actually point at a piece of data? With a small path language called JSONPath. We are going to keep this light here and go deep in Module 06, because JSONPath rewards a whole module of its own. For now you only need to be able to read a path.

A path starts at the root of the data, written as a dollar sign, and then walks down into the JSON by naming each key. To reach Priya's email in that seed, you start at the root, step into the trigger data, step into `attributes`, and step into `email`. Written out, that is `$.trigger.attributes.email`. To reach her first name, `$.trigger.attributes.firstname`. To reach her login name, which sits one level up in the `identity` object rather than in `attributes`, it is `$.trigger.identity.name`.

Look carefully at that last one, because it hides a trap. The login name lives under `identity`. The email lives under `attributes`. They are in different places in the JSON, so their paths are different. If you assume everything about a person lives in one tidy spot, you will write a path that points at nothing.

Let me show you that exact failure, because seeing it now saves you an afternoon later. Suppose you want the email address and you write `$.trigger.identity.email`. It reads fine in English, "the identity's email." But look back at the JSON. There is no `email` inside the `identity` object. The email is inside `attributes`. So that path resolves to nothing. The Send Email step then has an empty "to" field, and either the workflow fails or an email goes out to no one. Nothing crashes loudly. You just get silence and a confused afternoon. The cure is boring and reliable: look at the actual JSON and follow the real nesting, key by key, instead of guessing where a field ought to be.

## Two ways to write a path: the Variable Selector and inline variables

You will not have to type most paths by hand, which is a relief. The builder gives you a Variable Selector. You click it, you pick the step whose output you want, then you pick the field from a list, and the builder writes the correct JSONPath for you. When you are learning, use the selector. It looks at the real data shape and spells the path correctly, which protects you from the exact nesting mistake we just saw.

The other way is to write the reference inline, right inside a text field, using double curly braces. Inside a message body you might write `Welcome to Acme, {{ $.trigger.attributes.firstname }}` and when the step runs it swaps in `Priya`. One small convenience to know: if you are referencing a value that comes from the very same step you are configuring, you can leave the step name out. Across steps, name the step. Same step, no need.

There is one more detail I will flag now and explain properly later, so it does not surprise you. Trigger filters, which decide whether a workflow should fire at all, use a slightly different flavor of JSONPath than the one steps use to read data. They come from two different underlying engines. You do not need that distinction yet. Just tuck away the fact that "the path in a trigger filter" and "the path in a step" are close cousins, not identical twins, and Module 06 will make the difference clear.

## Steps, order, start, and end

Now the plumbing that holds it together. Inside a workflow, every step has a name, and every step except the trigger and the final ones points at the step that should run next. That "next" pointer is what puts the steps in order. The workflow also marks which step is the start, so it knows where to begin after the trigger fires.

Every path through a workflow has to end somewhere, and it ends at one of two end steps: Success or Failure. These are not decoration. They are how the workflow records whether it finished cleanly or fell over, and later, when you read a workflow's run history in Module 07, that Success or Failure is the first thing you will look at. When you build branching logic, different branches can end in different places, but each branch has to land on an end.

So the shape of any workflow is: a trigger fires, control passes to the start step, each step hands off to its named next step, and the line eventually reaches Success or Failure. Simple to say, and it holds for the smallest welcome email and the largest joiner automation alike.

## The builder is a friendly face over JSON

One last thing, and it is the thing that will make you comfortable rather than intimidated. Everything you do in the visual builder is really editing a JSON document underneath.

The builder itself is a canvas. Down the left you have the steps you can add, sorted into tabs for triggers, actions, and operators. In the middle is the canvas where you drag steps and draw the connections between them. On the right is the configuration panel for whatever step you have selected, which is where you fill in fields like the email recipient. You build by dragging, connecting, and filling in.

But when you save, all of that becomes a JSON definition with a clear structure. There is a name and a description at the top. Then there is a `definition` that holds the `trigger`, a `start` naming the first step, and a `steps` object holding every step keyed by its name. Here is the skeleton so you recognize it when you meet it:

```json
{
  "name": "Priya Welcome Email",
  "description": "Send a welcome email when an identity is created",
  "definition": {
    "trigger": { },
    "start": "Send Welcome Email",
    "steps": {
      "Send Welcome Email": { }
    }
  }
}
```

Why does this matter to you as a learner? Because you can download that JSON, edit it, and upload it again. That is how workflows get copied between tenants, saved in version control, and built by scripts instead of by hand. You do not need to do any of that yet. I point it out so that the builder never feels like a black box. It is a comfortable front end, and underneath is plain JSON that you can read and, one day, drive directly.

## Before you move on

Go back to the seed JSON at the top of this module and answer three questions in your head. What is the JSONPath to Priya's department? What is the JSONPath to her last name? And if a step tried to read `$.trigger.attributes.manager`, what would it get, and why? If you can answer all three, and especially if your answer to the third one is "nothing, because there is no manager field in that data," then you understand how data lives and moves inside a workflow, and you are ready for Module 02, where we meet every kind of trigger that can set one of these off.

---
[← Previous: Module 00 Orientation](00-orientation.md) | [Course home](../README.md) | [Next: Module 02 Triggers →](02-triggers.md)
