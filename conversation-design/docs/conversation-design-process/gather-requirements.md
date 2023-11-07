# Gather requirements

Gathering requirements for a conversational experience is not just about
defining features and functionality, though that is the main outcome. At its
core, the requirements-gathering process is about understanding users and
technical capabilities.

Starting with clear, well-researched requirements is the best way to avoid the
need for major changes after design and/or development is completed.

## Identify your users

Gathering requirements is all about asking questions and using data to answer
them. For example:

- Who are your users?
- What are their needs?
- How are they completing these tasks today?
- What words and phrases do they use to talk about these tasks?
- What situations or circumstances trigger these tasks?

## Accommodate all users

While it’s important to optimize for your most frequent users, don’t do so at
the expense of other users’ experiences. A well-designed product is inclusive
and universally accessible. Designing for different populations means leveraging
inclusive design or universal design strategies. Often, the accommodation you’re
forced to make for one population ends up benefiting everyone (e.g., a ramp is
easier than stairs). For more information, see the [Material Design guidelines
for Accessibility](https://material.io/guidelines/usability/accessibility.html).

Create user personas and journeys | &nbsp; | &nbsp;
---|---|---
User persona | Who is the user? | A user persona is a specific but brief description of an individual user. Think about the types of people you expect to use your Actions, and create a few user personas to represent them. These user personas will help you avoid designing only for yourself and your goals.
User journeys | What are the user’s goals? What’s the user’s context? | A user journey is the pathway for the user to complete a goal in a given context.
Critical user journeys | Describe each of the relevant moments in the journey | Critical user journeys are those that either 1) happen very often or 2) are of key importance to the user. Aim to help users to complete one of these journeys from start to finish. Focusing on these will help you build Actions that reach a large and/or dedicated audience.

## Example from the Google I/O 18 Action

Check out these blog posts for more details on how we
[designed](https://medium.com/google-developers/how-we-designed-it-the-google-i-o-18-action-for-the-google-assistant-9370ffbaf9b0)
and
[built](https://medium.com/google-developers/how-we-built-it-the-google-i-o-18-action-for-the-google-assistant-7f287ad31b7)
the I/O 18 Action. You can also see the
[open-source code](https://github.com/actions-on-google/dialogflow-iosched-nodejs)
for a deeper look into the structure.

Goal | Context | Image
---|---|---
Who is the user | Anna, 27, is a UX designer and sketch artist with a passion for creating engaging user  experiences that help users get things done in their lives. | ![Gather Requirements 1](../static/gather-requirements-1.jpg){ width="1000" }
What are the user’s goals? | Anna’s got a full schedule planned for Google I/O and doesn’t want to miss a thing. She’s excited to learn about how to design an experience with Actions on Google by attending relevant talks. She also wants to check out all the new demos and pick up some Google swag. | ![Gather Requirements 2](../static/gather-requirements-2.jpg){ width="1000" }
What’s the user’s context? | Anna is in Mountain View for Google I/O. She’s just starting her day, leaving her hotel and heading to Shoreline Amphitheatre. | ![Gather Requirements 3](../static/gather-requirements-3.jpg){ width="1000" }
Describe each of the relevant moments in the journey. | Anna starts by getting directions to Shoreline Amphitheatre and info on where to park. Once at the venue, she gets help finding her way to badge pickup. Afterwards, she heads to the main stage for the keynote, grabbing something for breakfast on the way. Once settled, she’s got some time to wait, so she reviews her next few sessions. It’s going to be a sunny day, so she’s reminded to use the sunscreen in her swag bag while she waits. | ![Gather Requirements 4](../static/gather-requirements-4.jpg){ width="1000" }

## Identify technical capabilities

Determine what is and isn’t possible given your timeline and resources.

### Systems

What are the capabilities and limitations of the various systems that your
Actions will rely on?

Example: Google I/O 18 allows users to create a personalized schedule of all the sessions they want to attend |
---|
How will users be identified? Across sessions? |
How and where will their progress be saved? |
Will their changes sync with the Google I/O mobile app? |
How will you handle overlapping sessions? |

## Data

What’s the format and quality of any data you’ll be using?

Example: Google I/O 18 reads information about the sessions |
---|
What information is available? (e.g., titles, descriptions, dates & times, topics) |
What’s the format of the session information? Is it plain text, audio, or other? |
If the content is plain text, was it written to be seen or to be heard? |
How long is it? Or how long does it take to read? |

Often, some reformatting needs to happen before some types of content can be
appropriately rendered in text-to-speech (TTS).

## Identify your key use cases

Considering technical limitations, level of effort, and timeline, what use cases
can you support? Assign priorities accordingly.

### Aim for impact

Put your effort where it will have the most impact. This may be scenarios that
affect the largest number of users. It could be highly visible use cases/market
differentiators. Or it may be a feature that makes a big difference for a
handful of loyal power users.

### What are users asking for?

Do some user research on how users complete this task today and the language
they use to describe it.

### Learnings from the Google I/O 18 Action

If you haven’t already, be sure to read these blog posts for a deep dive on how
we
[designed](https://medium.com/google-developers/how-we-designed-it-the-google-i-o-18-action-for-the-google-assistant-9370ffbaf9b0)
and
[built](https://medium.com/google-developers/how-we-built-it-the-google-i-o-18-action-for-the-google-assistant-7f287ad31b7)
the I/O 18 Action (or take a look at the
[code](https://github.com/actions-on-google/dialogflow-iosched-nodejs)).

For the Google I/O 18 Action, we talked with Googlers who’ve worked at the event
in previous years. We asked them what kinds of questions attendees usually have
during the event. These questions typically fell within one of these 4
categories:

General navigation | Personal navigation | Event details | Location-specific event details
---|---|---|---
"Where’s the bathroom?"| "Where are the codelabs?" | "Where’s my next session?" | "Where can I get my app reviewed?"
"What time is lunch?" | "When’s the after party?" | "What’s the next session in this room?" | "What can I do here?"

With that knowledge, we decided to focus on these key use cases:

- Provide wayfinding information for locations specific to Shoreline
  Amphitheatre, for example: bathrooms, parking, driving directions
- Provide wayfinding information for locations specific to Google I/O, for
  example: badge pickup, sandbox, codelabs, office hours and app reviews, after
  hours, I/O store
- Provide event details for all keynotes, sessions, office hours, and meals;
  allow them to be filtered by time, location, or the user’s schedule
