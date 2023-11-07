# Helpers

Helpers allow the Assistant to quickly and easily ask the user common questions
on your behalf. Helpers use a standard, consistent UI that saves you the time
and effort of building your own.

## What are helpers?

Helpers tell the Assistant to take over the conversation to ask the user common
questions, such as for their full name, a date and time, or a delivery address.
When you request a helper, the Assistant presents the appropriate standard UI to
users to ask for this information, so you don't have to design your own. Visit
our [developer site](https://developers.google.com/assistant/df-asdk/helpers)
for more technical guidance.

## Types of helpers and what they do

Helper type | Info you can ask for | Call the helper or get results
---|---|---
User information | <ul><li>Display name</li><li>Given name</li><li>Family name</li><li>Coarse/general device location (zip code and city)</li><li>Precise device location (coordinates and street address)</li></ul> | <ul><li>[Call the helper](https://developers.google.com/assistant/df-asdk/helpers#calling_the_helper)</li><li>[Get the results](https://developers.google.com/assistant/df-asdk/helpers#getting_the_results_of_the_helper)</li></ul>
List and carousel option | <ul><li>Display a list or carousel UI and let the user select an option.</li></ul> | <ul><li>[Get the results](https://developers.google.com/assistant/df-asdk/helpers#getting_the_results_of_the_helper)</li></ul>
Date and time | <ul><li>Get a date and time from the user.</li></ul> | <ul><li>[Call the helper](https://developers.google.com/assistant/df-asdk/helpers#calling_the_helper)</li><li>[Get the results](https://developers.google.com/assistant/df-asdk/helpers#getting_the_results_of_the_helper)</li></ul>
Account sign-in | <ul><li>Have users sign-in to their accounts that are associated with your service.</li></ul> | <ul><li>[Call the helper](https://developers.google.com/assistant/df-asdk/helpers#calling_the_helper)</li><li>[Get the results](https://developers.google.com/assistant/df-asdk/helpers#getting_the_results_of_the_helper)</li></ul>
Place and location | <ul><li>Prompt the user for addresses and other locations, including any home/work/contact locations that they've saved with Google.</li></ul> | <ul><li>[Call the helper](https://developers.google.com/assistant/df-asdk/helpers#calling_the_helper)</li><li>[Get the results](https://developers.google.com/assistant/df-asdk/helpers#getting_the_results_of_the_helper)</li></ul>
Confirmation | <ul><li>Ask a generic confirmation from the user (yes/no question) and get the resulting answer. The grammar for "yes" and "no" naturally expands to things like "Yea" or "Nope", making it usable in many situations.</li></ul> | <ul><li>[Call the helper](https://developers.google.com/assistant/df-asdk/helpers#calling_the_helper)</li><li>[Get the results](https://developers.google.com/assistant/df-asdk/helpers#getting_the_results_of_the_helper)</li></ul>
