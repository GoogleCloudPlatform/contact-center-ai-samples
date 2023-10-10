<script lang="ts">
  import { Navbar, NavBrand, NavUl, NavLi } from "flowbite-svelte";
  import { A, Input, Button, ButtonGroup } from "flowbite-svelte";
  import { Card, Tabs, TabItem } from "flowbite-svelte";
  import { Dropdown, DropdownItem } from "flowbite-svelte";
  import { onMount } from "svelte";

  var utterance: string;
  function fillAndSend(utterance: string, time: number) {
    if (!utterance) {
      return;
    }

    document.querySelectorAll("iframe").forEach((item) =>
      setTimeout(function () {
        item.contentWindow.document.body
          .querySelector("df-messenger")
          .shadowRoot.querySelector("df-messenger-chat")
          .shadowRoot.querySelector("df-messenger-user-input")
          .shadowRoot.querySelector(".input-box-wrapper > input").value = utterance;
      }, time * 1000),
    );

    document.querySelectorAll("iframe").forEach((item) =>
      setTimeout(
        function () {
          item.contentWindow.document.body
            .querySelector("df-messenger")
            .shadowRoot.querySelector("df-messenger-chat")
            .shadowRoot.querySelector("df-messenger-user-input")
            .shadowRoot.querySelector(".input-box-wrapper > button")
            .click();
        },
        (time + 1) * 1000,
      ),
    );
  }

  function autoMode() {
    fillAndSend("Does the Pixel 7 Pro support fast charging?", 1);
    fillAndSend("Will the Pixel Watch work in the winter temperatures in Alaska?", 10);
    fillAndSend("Which smart locks are available?", 20);
    fillAndSend("What is the most popular color for the Pixel Watch?", 30);
    fillAndSend("Where can I buy a Google Cloud hoodie and how much does it cost?", 40);
    fillAndSend("Should I buy a Pixel 7 or a Pixel 7 Pro?", 50);
    fillAndSend("What are some good places to visit while I'm in San Francisco?", 60);
  }

  onMount(() => {
    fillAndSend("Hello", 1);
  });
</script>

<Navbar class="mb-4 bg-[#a3cef1] p-4">
  <NavBrand href="/">
    <img src="dialogflow-logo.png" class="mr-3 h-6 sm:h-9" alt="Dialogflow CX Logo" />
    <span class="self-center whitespace-nowrap text-xl font-semibold">
      Generative AI Chatbots in Google Cloud
    </span>
  </NavBrand>
  <NavUl>
    <NavLi id="nav-docs" class="cursor-pointer">Documentation</NavLi>
    <NavLi id="nav-codelabs">Codelabs</NavLi>
    <NavLi
      href="https://github.com/GoogleCloudPlatform/contact-center-ai-samples/tree/main/generative-chatbots"
      >Source code</NavLi>
  </NavUl>
  <Dropdown trigger="hover" triggeredBy="#nav-docs" class="z-20 p-1">
    <DropdownItem href="https://cloud.google.com/dialogflow/cx/docs/concept/data-store-agent"
      >Data Store Agent</DropdownItem>
    <DropdownItem href="https://cloud.google.com/dialogflow/cx/docs/concept/generative-fallback"
      >Generative Fallback</DropdownItem>
    <DropdownItem href="https://cloud.google.com/dialogflow/cx/docs/concept/generators"
      >Generators</DropdownItem>
  </Dropdown>
  <Dropdown trigger="hover" triggeredBy="#nav-codelabs" class="z-20 p-1">
    <DropdownItem href="https://codelabs.developers.google.com/codelabs/gen-app-builder-chat"
      >Data Store Agent</DropdownItem>
    <DropdownItem
      href="https://codelabs.developers.google.com/codelabs/dialogflow-generative-fallback"
      >Generative Fallback</DropdownItem>
    <DropdownItem href="https://codelabs.developers.google.com/codelabs/dialogflow-generator"
      >Generators</DropdownItem>
  </Dropdown>
</Navbar>

<div class="container mx-auto">
  <div class="mb-4">
    <Card class="mx-auto min-w-[100%]">
      <div class="flex">
        <div class="ml-4">
          <Tabs contentClass="p-4 mt-4 leading-7" style="underline">
            <TabItem open title="What is this?">
              <p class="text-md h-fit font-normal text-gray-700">
                These chatbots demonstrate the behavior of different
                <A
                  href="https://cloud.google.com/ai/generative-ai"
                  class="font-bold text-blue-600 hover:underline">generative AI</A> features in
                <A
                  href="https://cloud.google.com/dialogflow/cx/docs/basics"
                  class="font-bold text-blue-600 hover:underline">Dialogflow CX</A> when answering questions
                about products in the <A
                  href="https://store.google.com/"
                  class="font-bold text-blue-600
                hover:underline">Google Store</A>
              </p>
            </TabItem>
            <TabItem title="How to use">
              <p class="text-md h-fit font-normal text-gray-700">
                Click <span class="font-bold">Start Demo Mode</span> to see example questions, or
                try <span class="font-bold">asking a question</span> in the text box below to see how
                the chatbots behave in different scenarios
              </p>
            </TabItem>
            <TabItem title="How it works">
              <p class="text-md h-fit font-normal text-gray-700">
                These virtual agents were built with <A
                  href="https://cloud.google.com/ai/generative-ai"
                  class="font-bold text-blue-600 hover:underline">generative AI</A> functionality in
                <A
                  href="https://cloud.google.com/dialogflow/cx/docs/basics"
                  class="font-bold text-blue-600 hover:underline">Dialogflow CX</A
                >. The <A
                  href="https://cloud.google.com/dialogflow/cx/docs/concept/data-store-agent"
                  class="font-bold text-blue-600 hover:underline">Data Store Agent</A> chatbot queries
                indexed documents and data using <A
                  href="https://cloud.google.com/generative-ai-app-builder"
                  class="font-bold text-blue-600 hover:underline">Vertex AI Search</A
                >, and each chatbot calls large language models (LLMs) in <A
                  href="https://cloud.google.com/vertex-ai"
                  class="font-bold
                text-blue-600 hover:underline">Vertex AI</A> to generate dynamic, personalized responses
                to users based on your website content, structured data, or unstructured data. This static
                website is hosted on <A
                  href="https://firebase.google.com/"
                  class="font-bold text-blue-600 hover:underline">Firebase</A> and is using the <A
                  href="https://cloud.google.com/dialogflow/cx/docs/concept/integration/dialogflow-messenger"
                  class="font-bold text-blue-600 hover:underline"
                  >Dialogflow CX Messenger integration</A
                >.
              </p>
            </TabItem>
            <TabItem title="Why separate chatbots?">
              <p class="text-md h-fit font-normal text-gray-700">
                Each generative AI feature is shown here independently (only one feature per
                chatbot) to clearly demonstrate how it works and what specific problem it solves.
              </p>
              <p class="text-md h-fit font-normal text-gray-700">
                In real-world applications, these features can be combined in one chatbot to provide
                the best customer experience and automatically handle different scenarios.
              </p>
            </TabItem>
            <TabItem title="Learn more">
              <p class="text-md h-fit font-normal text-gray-700">
                You can learn more about each generative AI feature in <A
                  href="https://cloud.google.com/dialogflow/cx/docs/basics"
                  class="font-bold text-blue-600 hover:underline">Dialogflow CX</A> by viewing the documentation
                for <A
                  href="https://cloud.google.com/dialogflow/cx/docs/concept/data-store-agent"
                  class="font-bold text-blue-600 hover:underline">Data Store Agent</A
                >, <A
                  href="https://cloud.google.com/dialogflow/cx/docs/concept/generative-fallback"
                  class="font-bold text-blue-600 hover:underline">Generative Fallback</A
                >, and <A
                  href="https://cloud.google.com/dialogflow/cx/docs/concept/generators"
                  class="font-bold text-blue-600 hover:underline">Generators</A
                >. You can build these chatbots yourself by following the codelabs for <A
                  href="https://codelabs.developers.google.com/codelabs/gen-app-builder-chat"
                  class="font-bold text-blue-600 hover:underline">Data Store Agent</A
                >, <A
                  href="https://codelabs.developers.google.com/codelabs/dialogflow-generative-fallback"
                  class="font-bold text-blue-600 hover:underline">Generative Fallback</A
                >, and <A
                  href="https://codelabs.developers.google.com/codelabs/dialogflow-generator"
                  class="font-bold text-blue-600 hover:underline">Generators</A
                >. You can also learn more about <A
                  href="https://cloud.google.com/ai/generative-ai"
                  class="font-bold text-blue-600 hover:underline">Generative AI</A> and <A
                  href="https://cloud.google.com/use-cases/generative-ai"
                  class="font-bold text-blue-600 hover:underline">Generative AI Use Cases</A> in Google
                Cloud.
              </p>
            </TabItem>
          </Tabs>
        </div>
      </div>
    </Card>
  </div>
  <div class="mb-7">
    <Card class="mx-auto min-w-[100%]">
      <form>
        <div class="mx-6 mb-8 mt-3 flex">
          <div class="w-full items-center">
            <ButtonGroup class="w-full">
              <Input
                class="text-md"
                type="text"
                id="utterance"
                bind:value={utterance}
                placeholder="Ask me anything about products in the Google Store"
                required />
              <Button
                class="text-md"
                color="blue"
                type="submit"
                on:click={() => fillAndSend(utterance, 0)}>Send</Button>
            </ButtonGroup>
          </div>
          <div class="w-60 grow text-end">
            <Button class="text-md" color="green" on:click={() => autoMode()}
              >Start Demo Mode</Button>
          </div>
        </div>
      </form>
      <div class="mx-10 -mb-1 flex space-x-16 pb-5">
        <div class="w-1/3 content-center items-center justify-center">
          <div
            class="mb-3 block rounded-3xl border border-b-4 border-l-4 border-r-4 border-t-4 border-gray-200 bg-white px-6 py-3 hover:bg-gray-100">
            <div class="mb-3 mt-2 flex">
              <img src="agent.svg" alt="Agent" width="100px" />
              <div class="ml-4">
                <p class="text-sm font-normal text-gray-700">
                  <A
                    href="https://cloud.google.com/dialogflow/cx/docs/concept/data-store-agent"
                    class="font-bold text-blue-600 hover:underline">
                    Data Store Agent
                  </A>
                  uses LLMs to generate responses based on the content of your websites and documents
                </p>
              </div>
            </div>
          </div>
          <iframe
            class="min-h-[50vh] min-w-full border border-b-0 border-l-0 border-r-0 border-t-0 border-gray-200"
            src="/bot1.html"
            title="bot1" />
        </div>
        <div class="w-1/3">
          <div
            class="mb-3 block rounded-3xl border border-b-4 border-l-4 border-r-4 border-t-4 border-gray-200 bg-white px-6 py-3 hover:bg-gray-100">
            <div class="mb-3 mt-2 flex">
              <img src="support.svg" alt="Agent" width="100px" />
              <div class="ml-4">
                <p class="text-sm font-normal text-gray-700">
                  <A
                    href="https://cloud.google.com/dialogflow/cx/docs/concept/generative-fallback"
                    class="font-bold text-blue-600 hover:underline">
                    Generative Fallback
                  </A>
                  uses LLMs with a custom prompt to respond to users when your chatbot doesn't know the
                  answer
                </p>
              </div>
            </div>
          </div>
          <iframe
            class="min-h-[50vh] min-w-full border border-b-0 border-l-0 border-r-0 border-t-0 border-gray-200"
            src="/bot2.html"
            title="bot2" />
        </div>
        <div class="w-1/3">
          <div
            class="mb-3 block rounded-3xl border border-b-4 border-l-4 border-r-4 border-t-4 border-gray-200 bg-white px-6 py-3 hover:bg-gray-100">
            <div class="mb-3 mt-2 flex">
              <img src="write.svg" alt="Agent" width="100px" />
              <div class="ml-4">
                <p class="text-sm font-normal text-gray-700">
                  <A
                    href="https://cloud.google.com/dialogflow/cx/docs/concept/generators"
                    class="font-bold text-blue-600 hover:underline">
                    Generators
                  </A>
                  use LLMs with a custom prompt to create dynamic responses for users at any point in
                  a conversation
                </p>
              </div>
            </div>
          </div>
          <iframe
            class="min-h-[50vh] min-w-full border border-b-0 border-l-0 border-r-0 border-t-0 border-gray-200"
            src="/bot3.html"
            title="bot3" />
        </div>
      </div>
    </Card>
  </div>
  <div class="inset-x-0 bottom-0 mx-6 h-16">
    <p class="font-normal leading-tight text-gray-700">
      Powered by <A
        class="font-medium text-blue-600 hover:underline"
        href="https://cloud.google.com/dialogflow">Dialogflow CX</A> and <A
        class="font-medium text-blue-600 hover:underline"
        href="https://cloud.google.com/generative-ai-app-builder">Vertex AI Conversation</A>
      in <A class="font-medium text-blue-600 hover:underline" href="https://cloud.google.com/"
        >Google Cloud</A>
    </p>
  </div>
</div>
