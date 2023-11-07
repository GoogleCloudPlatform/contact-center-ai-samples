# Test and iterate

User research can be helpful at any time during the design process. There’s no
substitute for getting feedback from actual users to find out what’s working and
what isn’t. The earlier you do this, the better.

Identifying problems is difficult when you’re immersed in design—an outsider’s
opinion is required. The good news is that you can (and should) get insight,
quickly and easily, into whether your design will work for users before writing
a single line of code.

## Get feedback to see if your dialog is working

**Find someone unfamiliar with your project to try out your dialog.** Getting
feedback during the design process exposes usability issues and gives you the
opportunity to self-correct early. Before you write a single line of code, it’s
important to run a usability test on your conversational experience. We
recommend conducting a quick and dirty Wizard of Oz (WOZ) experiment to help you
figure out if you’re on the right path.

## Use a Wizard of Oz experiment

**Why is it called that?** Wizard of Oz (WOZ) experiments get their name from the
movie The Wizard of Oz; they refer to the idea that there is a man behind the
curtain pulling the levers.

**What’s Wizard of Oz prototyping?** Simply put, it’s a way to test a prototype
without actually developing the software. WOZ prototyping is used to evaluate a
design’s functionality, its ability to meet users’ goals, and to improve the
user experience (UX) overall. WOZ experiments are meant to look and feel like
the real experience, but instead of software, there’s a person (the “wizard”)
simulating how the persona would behave in production. Participants may or may
not know that they are interacting with the wizard behind the curtain.

**Why you should do it?** One of the biggest advantages of WOZ prototyping is
that you can test your design without having to build it. WOZ experiments are
the minimum viable product (MVP) of prototypes for voice testing. They’re
relatively easy to run and require little to no extra effort. The prototype may
be quite simple, using everyday objects to represent parts of the design. Or it
may be a working model (collection of existing products) capable of performing
some, but not all of the tasks. Of course, the more realistic your prototype is,
the better your feedback will be. But choose wisely: How much time can you
afford to allocate to this? And is the prototype ‘realism’ worth it?

## How to conduct usability tests

There are 3 different approaches you can take for testing your application:

### 1) Quick and dirty WOZ experiment

**Use what you have.** All you need is your
[sample dialogs](../conversation-design-process/write-sample-dialogs.md) (which
you should already have at this point). Simply find someone unfamiliar with your
project (e.g., family, friends, colleagues) and ask them to role-play your
dialog with you—you’ll read your persona’s lines and observe how they react as
the user. If the user goes “off script”, feel free to improvise what your
persona would say.

### 2) Standard WOZ experiment

For the most realistic experience, simulate the persona’s role by playing the
persona’s prompts using the
[TTS Simulator](https://developers.google.com/actions/reference/ssml#tts_simulator)
in the
[Actions on Google Developer Console](https://console.actions.google.com/).
Download the audio to have it ready to play on demand.

!!! note

    If the TTS doesn't sound good, rewrite the prompt or use SSML to
    change its performance.

This version requires four things:

- A conversation script that provides directions on what the persona should say
  after each user response. The high-level flow (or a simplified version of it)
  is ideal for this.
- Downloaded audio of all the persona's spoken prompts. Use file names that will
  help you quickly identify the correct file to play.
- Someone to play the "user." This should be someone who’s unfamiliar with your
  Action.
- Someone to play the "wizard." This should be someone highly familiar with your
  Action.

Have the wizard start the conversation by playing the audio for your Action’s
greeting, for example, "Welcome to your launchpad for all things Google I/O. The
festival's underway right now. Are you one of the lucky attendees?" The wizard
will then wait for the user to respond, hopefully with a synonym of "yes" or
"no". Once the user has responded, the wizard will have to quickly consult the
high level-flow to determine what prompt to play next, then find and play the
correct audio file.

### 3) Standard usability experiment

Of course, once you’ve started building your Action, you should test it often
using the the Actions Simulator in the Actions on Google Developer Console. Have
your friends, family, or colleagues test it too!

&nbsp; | No matter what experiment you use, be sure to do the following:
---|---
**Talk it out** | Since your goal is to update your design to reflect what works best for real users, you want your WOZ prototype to be as close to reality as possible. What looks good on paper doesn’t necessarily sound or feel natural in real conversation, so make sure users are hearing your prompts and speaking their response.
**Record your sessions** | Get permission to record your sessions so you can go back and listen to them. Take note of any issues that arose during the session.
**Ask for feedback** | Ask the user to describe their experience in their own words. How did it meet or fail to meet their expectations? Did anything surprise them? Were they satisfied? Remember that the focus is on their behavior, not their opinion.

## What can you expect to learn?

Running a WOZ experiment allows you to understand how people will engage with
your design. You may find that users were doing something very different than
what you had expected, requiring you to alter the design to better align with
their needs and expectations.

**Bottom line:** Focus on the usability of your design (and not on users’
opinions). Iterate based on user behavior, and test again if time permits.

&nbsp; | Things to look for (and how you might improve your dialog):
---|---
Natural conversation | Pay attention to the way users naturally ask for things. Do they feel like they can only speak in short keyword-like phrases, or do they sound more conversational? Do they sound hesitant or confident when speaking to your persona? Does the flow make users feel like they can only provide one piece of information at a time, or does it encourage them to provide multiple details in one sentence?
User confusion | Look for places where users look confused or are unsure of what to say or do. Examine the previous prompts to see where you could make some clarifications. Was the call to action clear?
Unexpected utterances | Users might say something you didn’t expect. Take note of it and add handling for it in your design.
Signs of frustration or impatience | This is typically a sign that the interaction is too long-winded. Review your prompts to see if you can be more concise. Are there details that can be omitted?
Observe who’s speaking the most | Do users seem to be in control of the conversation? If not, how can you change that?

## How to test your Actions

Robust testing is essential for developing high-quality software and creating
user satisfaction.

<figure markdown>
  <iframe width="560" height="315"
src="https://www.youtube.com/embed/eD4x4gj4u2Y?si=4zdn-8XI0FyBS5AN"
title="YouTube video player" frameborder="0" allow="accelerometer; autoplay;
clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
allowfullscreen></iframe>
  <figcaption>
    Aylin Altiok and Nick Felker, on testing your Actions at Google I/O 2018
  </figcaption>
</figure>

This video is a deep dive into developing end-to-end tests for your Actions, and
it covers the tools that are available to make the process easier. It will also
share best practices on a variety of topics, like how to handle unexpected user
queries.
