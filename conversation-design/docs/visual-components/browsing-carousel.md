# Browsing carousel

Browsing carousels are optimized for allowing users to select one of many items
when those items are content from the web. When users select an item, it’s
opened in a web browser (or an AMP browser if all items are Accelerated Mobile
Pages).

Example

Here’s an example of what a browsing carousel looks like when all required and
optional fields are completed.

Note: for code examples, see the Actions on Google developer documentation.

Requirements
Field name	Required?	Restrictions/Customizations
URL	Yes
Every item in the carousel must link to web content. Accelerated Mobile Pages (AMP) content is recommended.
Item image	No
Choose from three different image aspect ratios: square, landscape, and portrait.
Default size depends on screen size and aspect ratio; any extra space will fill with bars.
Image source is a URL. If an image link is broken, then a placeholder image is used instead.
Alt text is required for accessibility.
Primary text	Yes
Each item’s primary text must be unique (to support voice selection).
Plain text. Fixed font and size.
Max 2 lines recommended. Depending on surface, additional characters will be cut off.
Secondary text
Also called body or formatted text.

No
Plain text. Fixed font and size.
Max 2 lines recommended. Depending on surface, additional characters will be cut off.
Footer	No
Fixed font and size.
Max 1 line. This is about 50 characters, depending on the screen. Additional characters will be truncated with an ellipsis.
Anchored at the bottom of the card, so items with shorter descriptions may have white space above the footer.
Number of items
Maximum: 10
Minimum: 2
Consistency
All items in a browsing carousel must include the same fields—e.g., if one item includes an image, then all items in the carousel must include images.

If all items link to AMP-enabled content, the user will be taken to an AMP browser with additional functionality. If any items link to non-AMP content, then all items will direct users to a web browser.

Interactivity
Swipe: Slide the carousel to reveal different cards.
Tap: Tapping an item opens a browser, displaying the linked page.
The mic doesn't re-open when a browsing carousel is sent to the user.
Guidance
Browsing carousels are used for browsing and selecting from web content.

Browsing carousels take users out of the multimodal conversational interaction with your Action, so make this transition clear to users. They’ll no longer be talking/typing to your Action, but will instead be tapping/reading content from a web browser.

Be transparent
Make it clear to the user that they need to select an item by interacting with the screen. Set expectations that this will open a web page and take them out of the conversation.

The mic doesn't re-open when a browsing carousel is sent to the user, so don’t ask the user a question since you won’t hear their reply.


Do.

Let users know that selecting an item will take them outside of the Action.


Don't.

Don’t ask a question when the mic is closed, and don’t mislead users. Here, it isn’t clear to the user that if they select a hotel, they’ll no longer be talking to Ibento and will be taken to the hotel’s webpage.
