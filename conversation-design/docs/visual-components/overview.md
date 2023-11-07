# Overview

Visual components include cards, carousels, lists, and other visual assets.
Visual components are useful if you're presenting detailed information, but they
aren't required for every dialog turn.

This section offers guidance on what visual components are available for you to
use in your Action, when to use them, and how to customize them.

## When to create visuals

### When scaling your design to help users wherever they are

If you’ve followed our
[conversation design process](../conversation-design-process/how-do-i-get-started.md),
then you’ll have started by designing for a screenless device like Google Home.
This is because getting the conversational flow right is easier if everything is
in one place—the spoken prompts.

You’ll start creating visuals as you expand your design to include other
devices, like mobile phones.

### When they supplement the conversation

Visuals are meant to supplement the conversation and therefore are not required
for every turn in the dialog.

Think about what information could be better represented on a screen. Ask
questions like:

- Would it help users to see an image of what’s being discussed?
- Would it be easier for the user to make a choice from a visual list rather
  than a spoken one?
- Is there additional content that, though not critical for the conversation,
  would be helpful to show users?

## Where and how visuals appear

### On devices with screen output

Obviously, visuals will only be displayed on devices with screen output. They’ll
automatically be resized and rearranged to fit the size of the screen on which
they appear.

### With conversational components

Visuals will never appear alone. They’ll always be accompanied by a spoken
prompt and/or display prompt. They should also be accompanied by chips.

### In a pre-formatted template

Think of these visual components as templates with required and optional fields.
All you need to do is specify the data (i.e., the text strings, image files,
etc.) that you want to appear. See the “Requirements” sections under each visual
component for details on what you need to specify.

## Types of visual components

Visual Component | Description
---|---
[Basic card](basic-card.md) | Use basic cards to display an image and text to users.
[Browsing carousel](browsing-carousel.md) | Browsing carousels are optimized for allowing users to select one of many items, when those items are content from the web.
[Carousel](carousel.md) | Carousels are optimized for allowing users to select one of many items, when those items are most easily differentiated by an image.
[List](list.md) | Lists are optimized for allowing users to select one of many items, when those items are most easily differentiated by their title.
[Media response](media-response.md) | Media responses are used to play and control the playback of audio content like music or other media.
[Table](table.md) | Tables are used to display static data to users in an easily scannable format.
