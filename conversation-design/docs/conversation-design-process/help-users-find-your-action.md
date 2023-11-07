# Help users find your Action

Once you’ve designed and built your Action, you’ll need to help users find it.
Leverage implicit and explicit invocations, built-in intents, and Action links
to make your Action easily discoverable to virtually any user.

## Tools and definitions

&nbsp; | What are they? | What do they do? | How do I use them? | How to:
---|---|---|---|---
Explicit invocations | Explicit invocations are phrases that users can say to call on, or invoke, your Action | Allow users to call on your Action by name. | Come up with a name for your Action.<br><br>The phrases themselves are already specified. | <ul><li>[Design](../building-blocks/discovery.md)</li><li>[Build](https://developers.google.com/actions/discovery/explicit)</li></ul>
Invocation phrases | Invocation phrases are more phrases that users can say to call on, or invoke, your Action. | Allow users to call on your Action by name and function. | Design phrases that describe a specific function your Action provides.<br><br>Users can either 1) add these phrases onto the ends of explicit invocations, or 2) use them alone as implicit invocations. | <ul><li>[Design](../building-blocks/discovery.md)</li><li>[Build](https://developers.google.com/actions/discovery/implicit#best_practices_for_writing_useful_invocation_phrases)</li></ul>
Implicit invocations | Implicit invocations are even more phrases users can say to call on, or invoke, your Action. | Allow the Assistant to suggest your Action to fulfill a user request. | Design invocation phrases that describe functions your Action provides.<br><br>When a user requests one of these functions, the Google Assistant may suggest your Action to fulfill the request. | <ul><li>[Design](../building-blocks/discovery.md)</li><li>[Build](https://developers.google.com/actions/discovery/implicit)</li></ul>
Built-in intents | Built-in intents are unique identifiers that allow the Google Assistant to know which category (or categories) of user requests your Action can fulfill. | Allow the Assistant to suggest your Action to fulfill a user request. | Choose appropriate intents from the [list](https://developers.google.com/assistant/df-asdk/discovery/built-in-intents) of the ones we currently support, and assign them to your Action. | <ul><li>[Design](../building-blocks/discovery.md)</li><li>[Build](https://developers.google.com/actions/discovery/built-in-intents)</li></ul>
Action links | Action links are essentially what they sound like: links that direct users to your Action from wherever you place them. | Allow users to access your Action by clicking a link. | Use the [Actions Console](https://console.actions.google.com/) to generate a URL that links to your Action.<br><br>You can either 1) direct users to the initial greeting, or 2) deep link to a specific intent. | <ul><li>[Design](../building-blocks/discovery.md)</li><li>[Build](https://developers.google.com/actions/deploy/action-links)</li></ul>
