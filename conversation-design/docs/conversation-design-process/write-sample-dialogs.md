# Write sample dialogs

Now that you have a clear picture of who's communicating (your
[persona](../conversation-design-process/create-a-persona.md) and your
[users](../conversation-design-process/gather-requirements.md)) and what they're
communicating about
([your key use cases](../conversation-design-process/gather-requirements.md)),
it's time to write the dialog.

## Why write sample dialogs

Sample dialogs are the
[key to creating great Actions on Google](https://developers.googleblog.com/2018/09/sample-dialogs-key-to-creating-great.html);
they'll give you a quick, low-fidelity sense of the "sound-and-feel" of the
interaction you're designing. They convey the flow that the user will actually
experience, without the technical distractions of code notation, complex flow
diagrams, recognition-grammar issues, etc.

By writing sample dialogs, you can informally experiment with and evaluate
different design strategies, such as how to promote the
[discoverability](../conversational-components/suggestions.md) of new features
or how to [confirm](../conversational-components/confirmations.md) a user's
request (for example: should you use an implicit confirmation, an explicit
confirmation, or no confirmation at all?).

## Start with a spoken conversation

When starting, we recommend focusing on just the spoken conversation — that is,
designing for a screenless device like Google Home. Getting the flow right is
easier if everything is in one place — the spoken prompts. As you expand to
other devices like mobile phones, pieces will move out of the spoken prompts and
into the display prompts, chips, and visuals.

!!! note

    If you start designing with a screen in mind, it can be easy to lose the
    thread of the conversation and end up with a graphical interface that is not
    suitable for conversation.

## High-level design strategies

Experienced conversation designers all have slightly different approaches to
high-level design, and the strategies they use can vary depending on the key use
cases. However, they all end up with 2 high-level design deliverables: 1) a set
of sample dialogs, and 2) a diagram of the conversation flow.

Some designers prefer to start by writing sample dialogs, while others prefer to
start by drawing the high-level flows. Often, designers are switching between
these two as they go. Whatever approach they take, they are leveraging a deep
knowledge of [human conversation](../learn-about-conversation.md) and
user-research-driven best practices for conversations with technology.

Writing for conversation takes practice. When typing spoken prompts to document
them, it can be easy to slip into the writing style for an email or an essay.
Avoid this pitfall by listening to each spoken prompt in text-to-speech (TTS)
and imagining the conversation. You should do this even if you've chosen to
record a voice for your persona, so you can get quick feedback on how the lines
sound when spoken.

The sections that follow offer a beginners walk-through of one approach to
high-level design.

## Sample dialogs for beginners

Watch this video to learn what a sample dialog is, and how to write one, in 60
seconds:

<figure markdown>
  <iframe width="560" height="315"
src="https://www.youtube.com/embed/sb75sitmPCc?si=uVHT07kgqUl5OGmU"
title="YouTube video player" frameborder="0" allow="accelerometer; autoplay;
clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
allowfullscreen></iframe>
  <figcaption>Cathy Pearl, Head of Conversation Design Outreach at Google
</figcaption>
</figure>

The easiest way to start writing dialogs is to channel your own expertise as a
lifetime communicator. People can generally tell when something sounds right or
wrong, even if they can't articulate the underlying linguistic principles as to
why it sounds that way; because of this, role-playing a dialog is the easiest
way to create the initial draft and iterate on successive drafts.

### Follow these steps to write sample dialogs for your feature

- **Step 1:** Focus on one
  [user persona](../conversation-design-process/gather-requirements.md) and one
  [key use case](../conversation-design-process/gather-requirements.md).
- **Step 2:** Find a partner and role-play the conversation, with one person
  pretending they're the user and the other pretending they're the system
  persona. Record the conversation. If you don't have a partner, you'll have to
  switch between playing both roles.
- **Step 3:** Transcribe the conversation. This is the first draft of your
  sample dialog.
- **Step 4:** Step through the dialog, saying the user's lines and playing each
  of the system persona's lines in the text-to-speech (TTS) in which it will be
  rendered. If the TTS doesn't sound good, rewrite it or use Speech Synthesis
  Markup Language (SSML) to change its performance.
- **Step 5:** Repeat steps 1-4 with different user personas and key use cases.

### Here's an example of an early sample dialog draft from the Google I/O Action

- **User persona:** Anna, 27, is a UX designer and sketch artist with a passion
  for creating engaging user experiences that help users get things done in
  their lives.
- **User context**: Anna's currently at I/O
- **User goals**: She wants information about the sessions remaining in the day.
- **Key use cases**: browsing sessions, wayfinding, and linking to the mobile
  app
- **System persona**: The Keeper of I/O-Specific Knowledge is a Google Developer
  Expert who believes strongly in the power of technology. A skilled networker,
  they spend their time answering questions on StackOverflow, building apps for
  big brands, and helping Google run madewithcode.com. They've attended I/O for
  the past 7 years and are a trusted member of the developer community. As a
  spokesperson for I/O, they take this responsibility very seriously, but, of
  course, they're still going to have fun doing it.

Speaker | User utterance / Spoken prompt | Notes
---|---|---
User | Ok Google, talk to Google I/O |
Assistant| Alright, here's Google I/O. <[earcon](../conversational-components/earcons.md)> |
I/O | Welcome to your launchpad for all things Google I/O. The festival's underway right now. Are you one of the lucky attendees? | Keep greeting short and light.<br><br> Split experience by attendees and non-attendees since different options will be relevant (e.g., directions vs livestream).
User | Yeah | Remember user's answer (do not ask again on subsequent interactions)
I/O | Congrats! As the Keeper of I/O-Specific Knowledge, consider me your guide. I can manage your schedule, help you find things to do, or give you directions. So, which do you need? | Introduce persona & give examples of what this Action can do
User | Find things to do |
I/O | Sure. Do you want to learn from the experts? Try some demos? Or kick back and relax? | Reduce cognitive load by grouping options:<br><br>experts = keynote<br><br>(day 1 only), sessions, office hours, app reviews<br><br>demos = codelabs, sandboxes<br><br>kick back = food, swag, after hours
User | Learn from the experts |
I/O | Great. I can tell you about the keynote. Help you browse sessions. Or recommend specific office hours and app reviews. Which would you like? |
User | Browse sessions |
I/O | Here are some of the topics left to cover today: machine learning and artificial intelligence, identity, Nest, Android and Play, open source, and Assistant. Do any of those sound good? | Instead of overwhelming the user with all possible topics on all days, focus on what's happening now/soon. Keep the list manageable by only offering a max of 6 at a time.<br><br>Needs SSML<br><br>&lt;speak&gt;Here're some of the topics left to cover today, &lt;break time="300ms"/&gt; Machine learning and artificial intelligence, &lt;break time="300ms"/&gt; identity, &lt;break time="300ms"/&gt; Nest, &lt;break time="300ms"/&gt; Android and Play, &lt;break time="300ms"/&gt; open source, &lt;break time="300ms"/&gt; and Assistant. &lt;break time="750ms"/&gt; Do any of those sound good?&lt;/speak&gt;
User | Yeah, AI |
I/O | At 1 PM, there's AI Adventures: art, science, and tools of machine learning. Then at 2:30, there's AutoML: build a custom model, no model code required. Do you want to hear more about either of those? | These titles are long and not written to be heard. Use silence to indicate start and end of titles. Only offer max of 2 at a time.<br><br>Needs SSML&lt;speak&gt;At 1 PM, there's &lt;break time="250ms"/&gt;AI Adventures: art, science, and tools of machine learning.&lt;break time="750ms"/&gt; Then at 2:30, there's &lt;break time="250ms"/&gt;AutoML: build a custom model, no model code required. &lt;break time="1s"/&gt;Do you want to hear more about either of those?&lt;/speak&gt;<br><br>The titles need to be reviewed and edited to be appropriately rendered in TTS, e.g., "AutoML" is pronounced as a single word.
User | Nah |
I/O | Alright. Later at 4, there's Distributed TensorFlow training. Do you want to hear more about it? | Needs SSML<br><br>&lt;speak&gt;Alright. Later at 4, there's &lt;break time="250ms"/&gt;Distributed TensorFlow training. &lt;break time="750ms"/&gt;Do you want to hear more about it?&lt;/speak&gt;
User | No |
I/O | Okay then. Since that's all for machine learning and artificial intelligence today, do you want to pick another topic? | Needs SSML<br><br>&lt;speak&gt;Okay. Since that's the last session today on machine learning and artificial intelligence&lt;break time="250ms"/&gt;, do you want to pick another topic?&lt;/speak&gt;
User | Yeah |
I/O | Other topics today include identity, Nest, Android and play, open source, Assistant, and Firebase. Do any of those sound good | Needs SSML<br><br>&lt;speak&gt;Other topics today include &lt;break time="250ms"/&gt;identity,&lt;break time="300ms"/&gt;Nest,&lt;break time="300ms"/&gt;Android and play,&lt;break time="300ms"/&gt;open source,&lt;break time="300ms"/&gt;Assistant,&lt;break time="300ms"/&gt;and Firebase.&lt;break time="750ms"/&gt;Do any of those sound good?&lt;/speak&gt;
User | Assistant |
I/O | At 11 AM, there's 10 tips for building better actions. Then at 2 PM, there's Creating a persona: what does your product sound like?. Do you want to hear more about either of those? | Needs SSML<br><br>&lt;speak&gt;At 11 AM, there's &lt;break time="250ms"/&gt;10 tips for building better actions. &lt;break time="750ms"/&gt;Then at 2 PM, there's &lt;break time="250ms"/&gt;Creating a persona: what does your product sound like?. &lt;break time="1s"/&gt;Do you want to hear more about either of those?&lt;/speak&gt;
User | Yeah, the second one |
I/O | That's a great session! Here's the description. What is a persona? And how can it reinforce your product's identity? Learn about tools, get tips, and see examples of how well-designed personas can transform voice-enabled interfaces and boost user engagement. Now, do you want me to repeat that, add it to your schedule, or tell you how to get there? | Session descriptions are long and not written to be heard. Consider editing.<br><br>Needs SSML<br><br>&lt;speak&gt;That's a great session! Here's the description. &lt;break time="250ms"/&gt;What is a persona? And how can it reinforce your product's identity? Learn about tools, get tips, and see examples of how well-designed personas can transform voice-enabled interfaces and boost user engagement. &lt;break time="1s"/&gt;Now, do you want me to repeat that, &lt;break time="250ms"/&gt;add it to your schedule, &lt;break time="250ms"/&gt;or tell you how to get there?&lt;/speak&gt;
User | Add it to my schedule |
I/O | To do that, you'll need to link this I/O 2018 Action to your Google Account. Do you want to do that now? |
User | No thanks | If yes, need specific instructions for helping the user link their account
I/O | No problem. Now, do you want to get directions, or hear about other sessions? |
User | How do I get there? |
I/O | The session Creating a persona: what does your product sound like? is located &lt;describe with landmarks&gt;. It starts at 2 PM. Do you want to hear that again? | Need directions for all locations
User | No |
I/O | Alright, anything else I can help you with right now? |
User | No
I/O | OK. Enjoy I/O! | Needs SSML<br><br>&lt;speak&gt;&lt;prosody rate="fast"&gt;OK. Enjoy IO!&lt;/prosody&gt;&lt;/speak&gt;
Assistant | &lt;earcon&gt; |

For more insight on writing sample dialogs, check out this two-part blog post
that details how we
[designed](https://medium.com/google-developers/how-we-designed-it-the-google-i-o-18-action-for-the-google-assistant-9370ffbaf9b0)
and
[built](https://medium.com/google-developers/how-we-built-it-the-google-i-o-18-action-for-the-google-assistant-7f287ad31b7)
the I/O 18 Action.

## High-level flows for beginners

Once you have a few sample dialogs, you can abstract the flow and logic of the
conversation. This provides the structure of your conversational interface. You
may want to start by sketching your high-level flows on a whiteboard or paper
before creating something more formal using a flowchart tool like [Google
Drawings](https://docs.google.com/drawings/).

![Map](../static/write-sample-dialog-map.jpg){ align=right width="400" }

Good designs balance the need for clearly defined user paths with the users'
desire for shortcuts directly to what they want.

Think of your high-level flow as the map for how users navigate your Action.

Users won’t automatically know what they can ask for when they start talking to
your Action, so you need to give them paths to follow, with signposts along the
way. Do this by creating menus and tree structures that guide users to every
part of your Action.

However, don’t let this get in the way of leveraging the magic of natural
language understanding (NLU) technology, which lets users ask for what they
want, whenever they want it (as long as they know it’s there).

### Here’s an example of an early draft from the Google I/O Action

Note that this flow only shows the functionality covered in the sample dialog
above. There are multiple “arrows to nowhere” that are not fully specified in
this example (created using
[Google Drawings](https://docs.google.com/drawings/)).

If you haven’t already, read this
[blog post](https://medium.com/google-developers/how-we-designed-it-the-google-i-o-18-action-for-the-google-assistant-9370ffbaf9b0)
for a detailed account of how we fleshed out our design.

![Image of a flowchart. All paths start with the Greeting then branch depending
on whether it’s before, during or after I/O. If it’s during I/O, the path splits
again based on whether or not the user is attending. Then there’s a series of
menus that further branch the user experience.](../static/io-action-diagram.png)
