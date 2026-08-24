# AI Usage

## Tools Used

I used:

* ChatGPT
* vs code 

I mainly used ChatGPT during the planning, design, debugging, and review stages of the project.

## Why I Used AI

I used ChatGPT mainly because I wanted to use it like a second developer who I could ask questions to when I was stuck or unsure about a design decision.

The assignment looked simple at first, but there were some parts that needed more thought, especially the packing logic. For example, deciding what should happen when a product can fit only after rotation, how multiple quantities should be handled, and how to choose between two boxes that can both fit the order.

I also used it to review my approach and point out cases that I might have missed.

I did not want the AI to decide the box for the application. The actual box-selection logic is deterministic and is implemented as normal application logic. This was an important decision for me because I wanted the same input to always produce the same result.

## Prompts Used

Some of the main things I asked ChatGPT about were:

* Breaking the assignment into smaller requirements.
* Understanding what a good Django structure would look like for this project.
* Thinking through the product and shipping-box data model.
* Finding edge cases for the packing logic.
* Handling rotation of products.
* Deciding how multiple products and quantities should be handled.
* Designing the box-ranking rules.
* Suggesting test cases for the recommendation engine.
* Reviewing the project for unnecessary complexity.
* Reviewing whether the AI integration was actually useful or was just being added for the sake of saying the project used AI.

One of the questions I kept coming back to was essentially:

> How can I use AI in the project without allowing AI to make the actual fulfillment decision?

That led to the separation between the deterministic fulfillment engine and the optional AI assistant.

## Output I Accepted

I used some of the AI suggestions as a starting point, especially for planning and identifying things I should test.

For example, the suggestions around testing different product orientations were useful because it made me realize that simply comparing length, width, and height in their original order would not be enough.

I also found the suggestions for testing boundary cases useful, such as:

* a product exactly matching the box dimensions;
* an order exactly reaching the box weight limit;
* a product that is slightly too large;
* an order where no box can be used;
* multiple boxes being valid.

I also used AI feedback while reviewing the project structure. It helped me notice places where I had started making the project more complicated than it needed to be.

## Output I Rejected

I did not accept everything suggested by AI.

One of the main things I had to push back on was unnecessary architecture. Some suggestions made the project look more like a large production platform than a small Django hiring assignment.

For example, I did not want to introduce a lot of separate layers just for the sake of having them. If a normal Django view and a small domain function were enough, I preferred that over adding several extra abstractions.

I also rejected the idea of making the LLM responsible for selecting the shipping box.

That would make the most important part of the application unpredictable and difficult to properly test.

I also removed or avoided features that were not really needed for the assignment, rather than adding them just because they looked impressive.

## Changes I Made to AI Output

I treated AI output as suggestions, not as final code.

When I used a suggestion, I still looked at how it fitted into the existing project.

Some of the changes I made were around:

* simplifying the project structure;
* changing the packing logic to match the actual requirements;
* removing unnecessary abstractions;
* changing validation behavior;
* adding missing test cases;
* changing the UI to focus more on the warehouse workflow;
* keeping the AI assistant separate from the deterministic recommendation engine.

The most important change was keeping the AI integration away from the actual box-selection decision.

The flow is intentionally:

Order
→ Deterministic packing/selection
→ Recommended box
→ Optional AI explanation

and not:

Order
→ AI
→ Recommended box

## Mistakes Made by AI

The biggest issue I noticed was that AI sometimes tried to make the project bigger than it needed to be.

It was easy to end up with suggestions that sounded good technically but did not really help with the assignment.

For example, some suggestions added extra layers or features when the same thing could be done with normal Django code.

There were also cases where an AI suggestion needed to be checked against the actual requirements instead of being accepted immediately.

This made me realize that using AI does not remove the need to understand the code. In some cases, it actually makes reviewing the code more important because generated code can look convincing even when the design is unnecessary or slightly wrong.

## How I Verified the Code

I did not consider the project finished just because the generated code looked correct.

I checked the project using Django's checks, migrations, automated tests, and manual testing through the application.

The main things I verified were:

* Django starts correctly.
* Models and migrations work correctly.
* Products and boxes can be managed.
* Orders can be created.
* Quantities are handled correctly.
* Product rotation is handled.
* Weight limits are respected.
* Boxes that cannot fit the order are rejected.
* The smallest suitable box is selected according to the defined rules.
* Tie-breaking behaves consistently.
* An order with no suitable box is handled correctly.
* Invalid input is rejected.
* The recommendation is repeatable for the same input.

I also tested the AI separately.

The important test for me was making sure that the application still gives the deterministic recommendation when the AI service is unavailable.

The AI is only there to explain the result. It is not part of the decision-making process.

The exact commands and actual test output are included in `TEST_OUTPUT.md`.

## Important Design Decisions I Made Myself

The biggest decision I made was that the box-selection system should not depend on an LLM.

The assignment mentions AI assistance, but I felt that using an LLM to decide whether something physically fits inside a box would make the system harder to trust.

For a warehouse system, I would rather have:

`same input → same box`

every time.

So I kept the actual decision deterministic.

The system checks the order, calculates the required weight, checks the available boxes, considers the allowed product orientations, removes boxes that cannot handle the order, and then ranks the remaining boxes using the defined rules.

After that, the AI assistant can explain the result in normal language.

For example, if the system has already determined that a smaller box does not fit because of its dimensions, the AI can explain that reason to the warehouse user. It does not get to change the result.

Another decision I made was to keep the project relatively small. I wanted the final code to be something another Django developer could open and understand without having to learn a large custom architecture first.

## What I Took Away From Using AI

One thing I learned from this project is that getting code from AI is usually not the difficult part.

The more important part is deciding whether the code actually makes sense.

AI was useful for giving me ideas, finding edge cases, and helping when I was stuck. But I still had to decide what belonged in the project and what did not.

The packing logic especially made me think about this because a solution can look technically impressive while still solving the wrong problem.

For me, the useful way of using AI was not:

> "Build the whole project for me."

It was closer to:

> "Here is the problem and my approach. What am I missing?"

That helped me keep control over the final implementation.
