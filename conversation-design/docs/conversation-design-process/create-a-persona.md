# Create a persona

Think of your persona as the front end of your Action, that is, the
conversational partner you create to interact directly with users. Defining a
clear system persona is vital to ensuring a consistent user experience that
builds user trust.

## Why use a persona?

A persona is a design tool that helps you write conversations. Before you can
write a dialog, you have to have a clear picture of who is communicating. A good
persona evokes a distinct tone and personality, and it’s simple enough to keep
top-of-mind when writing dialog. It should be easy to answer the question: "What
would this persona say or do in this situation?".

Users will project a persona onto your Action whether you plan for one or not.
So it's in your best interest to purposefully design the experience you want
users to perceive, instead of leaving it up to chance.

!!! note

    The goal of creating a persona is not to trick the user into thinking
    they're talking to a human being, but simply to leverage the communication
    system users learned first and know best: conversation.

## How do I create a persona?

Your persona can help provide users with a mental model for what your Action can
do and how it works by starting with what users already know. For example, in a
banking application, the persona could be modeled after an idealized bank teller
— trustworthy with customers' money and personal information. The metaphor of
the bank teller makes this new experience feel familiar, since users’ real-world
banking knowledge can guide them.

### Follow these steps to create your persona

- **Step 1:** Brainstorm a list of adjectives (e.g., friendly, technologically
  competent). Focus on the qualities you want users to perceive when talking to
  your Action.
- **Step 2:** Narrow your list down to 4-6 key adjectives that describe your
  persona’s core personality traits.
- **Step 3:** Come up with a few different characters who embody these qualities
  (e.g., a barista, a fashion icon, a world traveler). Your persona doesn’t have
  to be a person. It could also be an anthropomorphized animal, an alien, an
  artificial intelligence, a cartoon character, etc.
- **Step 4:** Choose one character that best embodies your Action and write a
  short description, no more than a paragraph. This description should provide a
  clear sense of what this persona is like, especially what it would say, write,
  or do. Focus on personality traits, and avoid specifying things like gender or
  age because they almost never critically define or differentiate a persona.
  Furthermore, deciding the gender upfront will make it harder to find the right
  voice, since you’ve already eliminated half of the options.
- **Step 5:** Find, or create, an image or two that visually represents your
  persona. Pictures are a great memory aid and can help you keep the persona in
  mind when writing dialog. If you create your own, consider using it as your
  Action’s logo so users can see it too.

## What voice should I choose?

When people hear a voice, they instantly make assumptions about the speaker’s
gender, age, social status, emotional state, and place of origin, as well as
personality traits like warmth, confidence, intelligence, etc. People can’t help
but do this with virtual assistants, too—so guide the assumptions they make
about your Action by choosing a voice that is consistent with your persona.

## There are 2 types of voices

Type | Description | Pros | Cons
---|---|---|---
Synthesized | The Actions on Google platform provides a variety of text-to-speech (TTS) voices that speak different languages. Go to [Languages and Locales](https://developers.google.com/actions/localization/languages-locales) to hear them. Note that you can adjust the way the synthesized speech sounds by using [Speech Synthesis Markup Language (SSML)](https://developers.google.com/actions/reference/ssml). For example, you may want to add silence or pauses, specify how numbers should be read, or adjust the intonation. | <ul><li>Hear prompts as soon as you’ve written them</li><li>Make quick and easy edits</li><li>Localization is built-in</li></ul> | <ul><li>Can sound unnatural or robotic</li><li>Less expressive. Difficult to convey humor, sarcasm, etc.</li><li>Few voices to choose from</li></ul>
Recorded | You can hire a professional voice actor, or even try using your own voice. Either way, you’ll need to record all the audio that will be used in your Action. | <ul><li>Natural and human</li><li>Very expressive. Can convey humor, sarcasm, etc.</li><li>Unlimited voices to choose from</li></ul> | <ul><li>Edits require re-recording</li><li>Recordings have to be localized</li><li>Requires robust management system for audio files</li></ul>

### Choose the best voice for your persona by holding an audition

- **Step 1:** Write a few spoken prompts that your persona would say. Or better
  yet, write a sample dialog. These will be the lines used for the audition.
- **Step 2:** If you're auditioning TTS voices, render your lines in each voice.
  If you're auditioning voice actors, tell them about what your Action does and
  give them your persona description and key adjectives so they understand the
  character they’re embodying. Then record them reading the lines.
- **Step 3:** Create a scorecard using the key adjectives that describe your
  persona. The goal is to rate how well a voice conveys each adjective using a
  5-point scale, with 1 meaning "not very well" and 5 meaning "very well."
- **Step 4:** Organize a listening party with your friends or colleagues.
  Audition each voice and rate them on the scorecard. Focus on the voice by just
  listening — don't read along. It helps to close your eyes and try to imagine
  the speaker.
- **Step 5:** Review the ratings and choose the winner! If there's a tie, listen
  to the voices again, this time rating them against your short persona
  description.

## Examples

&nbsp; | Here’s an example of the persona created for the Google I/O 18 Action:
---|---
Key Adjectives | <ul><li>Practical/straightforward</li><li>Techie</li><li>Techie</li><li>Enthusiastic</li><li>I/O expert</li></ul>
Characters who embody those adjectives | Who would be an I/O expert? <ul><li>I/O Planning Committee member</li><li>Speaker at I/O</li><li>Google Developer Expert</li><li>Google Developer Group organizer</li><li>Frequent I/O attendee</li></ul>
Short description | The Keeper of I/O-Specific Knowledge is a Google Developer Expert who believes strongly in the power of technology. A skilled networker, they spend their time answering questions on StackOverflow, building apps for big brands, and helping Google run madewithcode.com. They've attended I/O for the past 7 years and are a trusted member of the developer community. As a spokesperson for I/O, they take this responsibility very seriously, but, of course, they’re still going to have fun doing it.
Voice chosen | Of the available TTS voices for United States English, Female 2 ranked highest on practical/straightforward and techie

Check out this two-part blog post for more details on how we
[designed](https://medium.com/google-developers/how-we-designed-it-the-google-i-o-18-action-for-the-google-assistant-9370ffbaf9b0)
and
[built](https://medium.com/google-developers/how-we-built-it-the-google-i-o-18-action-for-the-google-assistant-7f287ad31b7)
the I/O 18 Action. You can also view the
[open-source code](https://github.com/actions-on-google/dialogflow-iosched-nodejs)
for a closer look at the structure.
