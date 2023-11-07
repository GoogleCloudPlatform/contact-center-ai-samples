# What is conversation design?

Conversation design is a design language based on human conversation (similar to
how [material design](https://material.io/guidelines/) is a design language
based on pen and paper). The more an interface leverages human conversation, the
less users have to be taught how to use it. It’s a synthesis of several design
disciplines, including voice user interface design, interaction design, visual
design, motion design, audio design, and UX writing.

The role of a conversation designer is like that of an architect, mapping out
what users can do in a space, while considering both the user’s needs and the
technological constraints. They curate the conversation, defining the flow and
its underlying logic in a detailed design specification that represents the
complete user experience. They partner with stakeholders and developers to
iterate on the designs and bring the experience to life.

## What isn't conversation design?

If you already have a working graphical user interface (GUI), it can be tempting
to simply add voice input and text-to-speech (TTS) output to turn it into a
conversation design. It’s a common misconception to assume that "conversation"
refers only to what is spoken or heard — **Conversation is inherently
multimodal.**

At its core, conversation design is about the flow of the conversation and its
underlying logic. Therefore, one needs to start from the bottom up when
redesigning an interface to be conversational. The logic that works for a
graphical interface is almost never going to work as-is for a conversational
interface.

Conversation shouldn’t be an afterthought; instead, it’s the roadmap of what’s
possible and how users get there.

## System and user personas

Part of the role of a conversation designer is that of a screenwriter. Before
you can write a dialog, you have to have a clear picture of who the characters
are; personas are the design tool used for this. A good persona is specific
enough to evoke a unique voice and personality, yet brief enough that it’s easy
to keep top-of-mind when writing a dialog. It should be easy to answer the
question, "What would this persona say or do in this situation?"

### System persona

The system persona is the conversational partner created to be the front end of
the technology that the user will interact with directly. Defining a clear
system persona is vital to ensuring a consistent user experience. Otherwise,
each designer will follow their own personal conversational style and the
overall experience will feel disjointed.

At Google, we’ve created the Google Assistant. Everything the Assistant does
(for example, says, writes, displays, suggests) and everywhere the Google
Assistant appears (for example, the look and feel of the software and hardware)
were designed to evoke a consistent persona.

Developers of third-party Actions have to create their own personas. Typically,
this starts with brainstorming adjectives (for example, friendly, trustworthy)
and narrowing them down to a short list. This list becomes a short description,
often accompanied by images. For detailed guidance, see
[Create a persona](conversation-design-process/create-a-persona.md).

### User persona

Think of a few specific people you expect to use your Actions. Try to have two
to three different types, for example, a millenial vs a working parent. These
user personas will help you avoid designing only for yourself and your goals.
For detailed guidance, see
[Identify your users](conversation-design-process/gather-requirements.md).

A user persona is a specific, but brief, description of an individual user:

<figure markdown>
  ![User persona for Amy](static/user-persona-amy.jpg){ width="300" }
  <figcaption>User persona: Amy, 32, is an Android developer who designs and
  builds advanced game applications. She’s a member of Women Who Code. She lives
  in Austin, and travels often for work.</figcaption>
</figure>

Add goals and context to create a user journey:

<figure markdown>
  ![User journey](static/user-journey.jpg){ width="300" }
  <figcaption>User goals: She’s planning her trip to Mountain View for Google
  I/O, hoping to make the most out of her trip. User context: She’s at her
  favorite local tearoom since her meeting nearby doesn’t start for another
  hour.</figcaption>
</figure>

## Conversation for computers

Conversation design is about teaching computers to be fluent in human
conversation and its conventions.

Principle | Description
---|---
Start with what humans do | Conversations with a computer should not feel awkward or break patterns that adapt to the communication system users learned first and know best. This helps create an intuitive and frictionless experience.
Adapt to technical limitations | In some ways, computers fall short of human capabilities. Technical limitations introduce scenarios that don’t occur in human-to-human conversation. For example, human conversation never fails due to an unrecoverable error. Human conversation doesn’t require starting with a specific word or phrase, e.g., “Ok Google”. In these cases, rely on user research to determine the best approach.
Leverage technical strengths | In other ways, computers can exceed human capabilities. They don’t get tired of being asked the same questions. They aren’t offended by being given commands. There’s no need to pepper their responses with filler words or other formulaic language, e.g., ums and ahs. They can quickly find and share information. Look for opportunities to avoid annoyance, streamline conversations, and exceed expectations.
