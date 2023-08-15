<script lang="ts">
  import { Navbar, NavBrand, NavUl, NavLi } from "flowbite-svelte";
  import { A, Input, Button, ButtonGroup } from "flowbite-svelte";
  import { Card } from "flowbite-svelte";
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
      }, time * 1000)
    );

    document.querySelectorAll("iframe").forEach((item) =>
      setTimeout(function () {
        item.contentWindow.document.body
          .querySelector("df-messenger")
          .shadowRoot.querySelector("df-messenger-chat")
          .shadowRoot.querySelector("df-messenger-user-input")
          .shadowRoot.querySelector(".input-box-wrapper > button")
          .click();
      }, (time + 1) * 1000)
    );
  }

  function autoMode() {
    fillAndSend("Does the Pixel 7 Pro support fast charging?", 1);
    fillAndSend("How does the Pixel Watch track sleep?", 10);
    fillAndSend("How long does the battery on the Nest Doorbell last?", 20);
    fillAndSend("Which smart locks do you sell?", 30);
    fillAndSend(
      "How does the Nest Camera tell the difference between people, animals, vehicles, and packages?",
      40
    );
  }

  onMount(() => {
    fillAndSend("Hello", 1);
  });
</script>

<Navbar class="mb-6 bg-[#a3cef1] p-4">
  <NavBrand href="/">
    <img src="dialogflow-logo.png" class="mr-3 h-6 sm:h-9" alt="Dialogflow CX Logo" />
    <span class="self-center whitespace-nowrap text-xl font-semibold">
      Generative AI Chatbots in Google Cloud
    </span>
  </NavBrand>
  <NavUl>
    <NavLi href="/" active={true}>Home</NavLi>
    <NavLi href="https://cloud.google.com/generative-ai-app-builder/docs/introduction"
      >Documentation</NavLi>
    <NavLi href="https://codelabs.developers.google.com/codelabs/gen-app-builder-chat"
      >Codelab</NavLi>
    <NavLi
      href="https://github.com/GoogleCloudPlatform/contact-center-ai-samples/tree/main/generative-chatbots"
      >Source code</NavLi>
  </NavUl>
</Navbar>

<div class="container mx-auto">
  <form>
    <div class="mx-14 mb-6 flex items-center text-center">
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
            on:click={() => fillAndSend(utterance, 0)}>Submit</Button>
        </ButtonGroup>
      </div>
      <div class="w-60 grow text-end">
        <Button class="text-md" color="green" on:click={() => autoMode()}>Start Demo Mode</Button>
      </div>
    </div>
  </form>

  <div class="mx-20 mx-auto flex h-[60vh] pb-4">
    <div class="w-1/3 px-[3vw]">
      <iframe src="/bot1.html" title="bot1" width="100%" style="height: 100%;" />
    </div>
    <div class="w-1/3 px-[3vw]">
      <iframe src="/bot2.html" title="bot2" width="100%" style="height: 100%;" />
    </div>
    <div class="w-1/3 px-[3vw]">
      <iframe src="/bot3.html" title="bot3" width="100%" style="height: 100%;" />
    </div>
  </div>

  <div class="mb-4 flex pb-6">
    <div class="mx-auto w-1/3">
      <Card class="mx-auto min-w-[80%]">
        <div class="flex">
          <img src="agent.svg" alt="Agent" width="100px" />
          <div class="ml-4">
            <p class="text-sm font-normal text-gray-700 dark:text-gray-400">
              <A
                href="https://cloud.google.com/dialogflow/cx/docs/concept/generative-agent"
                class="font-bold text-blue-600 hover:underline">
                Generative AI Agent
              </A>
              creates responses using large language models (LLMs) and the content of your websites and
              documents
            </p>
          </div>
        </div>
      </Card>
    </div>
    <div class="w-1/3">
      <Card class="mx-auto min-w-[80%]">
        <div class="flex">
          <img src="support.svg" alt="Agent" width="100px" />
          <div class="ml-4">
            <p class="text-sm font-normal text-gray-700 dark:text-gray-400">
              <A
                href="https://cloud.google.com/dialogflow/cx/docs/concept/generative-fallback"
                class="font-bold text-blue-600 hover:underline">
                Generative fallback
              </A>
              responds to users when your agent doesn't know the answer by calling an LLM with a custom
              prompt
            </p>
          </div>
        </div>
      </Card>
    </div>
    <div class="w-1/3">
      <Card class="mx-auto min-w-[80%]">
        <div class="flex">
          <img src="write.svg" alt="Agent" width="100px" />
          <div class="ml-4">
            <p class="text-sm font-normal text-gray-700 dark:text-gray-400">
              <A
                href="https://cloud.google.com/dialogflow/cx/docs/concept/generators"
                class="font-bold text-blue-600 hover:underline">
                Generators
              </A>
              create dynamic responses at a specific point in a conversation by calling an LLM with a
              custom prompt
            </p>
          </div>
        </div>
      </Card>
    </div>
  </div>

  <div class="inset-x-0 bottom-0 mx-6 h-16">
    <p class="font-normal leading-tight text-gray-700 dark:text-gray-400">
      Powered by <A
        class="font-medium text-blue-600 hover:underline"
        href="https://cloud.google.com/dialogflow">Dialogflow CX</A> and <A
        class="font-medium text-blue-600 hover:underline"
        href="https://cloud.google.com/generative-ai-app-builder">Gen App Builder</A>
      in <A class="font-medium text-blue-600 hover:underline" href="https://cloud.google.com/"
        >Google Cloud</A>
    </p>
  </div>
</div>
