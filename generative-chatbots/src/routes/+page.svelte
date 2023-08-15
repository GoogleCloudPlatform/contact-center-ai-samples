<script lang="ts">
  import { Navbar, NavBrand } from "flowbite-svelte";
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

<Navbar class="mb-9 bg-[#a3cef1] p-6">
  <NavBrand href="/">
    <img src="dialogflow-logo.png" class="mr-3 h-6 sm:h-9" alt="Dialogflow CX Logo" />
    <span class="self-center whitespace-nowrap text-xl font-semibold">
      Generative Chatbots in Google Cloud
    </span>
  </NavBrand>
</Navbar>

<div class="mx-auto container">

<form>
  <div class="flex text-center mx-14 items-center mb-6">
    <div class="w-full items-center">
      <ButtonGroup class="w-full">
        <Input
          class="text-md"
          type="text"
          id="utterance"
          bind:value={utterance}
          placeholder="Ask me anything about products in the Google Store"
          required />
        <Button class="text-md" color="blue" type="submit" on:click={() => fillAndSend(utterance, 0)}
          >Submit</Button>
      </ButtonGroup>
      </div>
      <div class="grow text-end w-60">
      <Button class="text-md" color="green" on:click={() => autoMode()}>Start Demo Mode</Button>
    </div>
  </div>
</form>

<div class="mx-20 flex h-[60vh] mx-auto pb-4">
  <div class="w-1/3 px-[3vw]">
    <iframe src="/bot1" title="bot1" width="100%" style="height: 100%;" />
  </div>
  <div class="w-1/3 px-[3vw]">
    <iframe src="/bot2" title="bot2" width="100%" style="height: 100%;" />
  </div>
  <div class="w-1/3 px-[3vw]">
    <iframe src="/bot3" title="bot3" width="100%" style="height: 100%;" />
  </div>
</div>

<div class="mb-4 flex pb-6">
  <div class="mx-auto w-1/3">
    <Card class="mx-auto min-w-[80%]">
      <div class="flex">
        <img src="agent.svg" alt="Agent" width="100px" />
        <div class="ml-4">
          <p class="font-normal text-gray-700 dark:text-gray-400 text-sm">
            <A
              href="https://cloud.google.com/dialogflow/cx/docs/concept/generative-agent"
              class="font-bold text-blue-600 hover:underline">
              Generative AI Agent
            </A>
            creates responses using large language models (LLMs) and the content of your websites and documents
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
          <p class="font-normal text-gray-700 dark:text-gray-400 text-sm">
            <A
              href="https://cloud.google.com/dialogflow/cx/docs/concept/generative-fallback"
              class="font-bold text-blue-600 hover:underline">
              Generative fallback
            </A>
            responds to users when your agent doesn't know the answer by calling an LLM with a custom prompt
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
          <p class="font-normal text-gray-700 dark:text-gray-400 text-sm">
            <A
              href="https://cloud.google.com/dialogflow/cx/docs/concept/generators"
              class="font-bold text-blue-600 hover:underline">
              Generators
            </A>
            create dynamic responses at a specific point in a conversation by calling an LLM with a custom prompt
          </p>
        </div>
      </div>
    </Card>
  </div>
</div>

</div>
