<script lang="ts">
  import { Navbar, NavBrand } from "flowbite-svelte";
  import { onMount } from "svelte";
  import { Input, Label, Helper } from "flowbite-svelte";
  import { Button, ButtonGroup } from "flowbite-svelte";

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

<Navbar let:hidden let:toggle class="mb-9 bg-[#E8F0FE] p-6">
  <NavBrand href="/">
    <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white">
      Bot Comparison - Google Store Virtual Agent
    </span>
  </NavBrand>
</Navbar>

<div class="flex text-center">
  <div class="w-0 grow">
    <form>
      <ButtonGroup class="mb-9 w-1/2">
        <Input
          class="w-full"
          type="text"
          id="utterance"
          bind:value={utterance}
          placeholder="Ask me anything about products in the Google Store"
          required />
        <Button color="blue" type="submit" on:click={() => fillAndSend(utterance, 0)}
          >Submit</Button>
      </ButtonGroup>
      <Button class="mx-2" color="green" on:click={() => autoMode()}>Demo Mode</Button>
    </form>
  </div>
</div>

<div class="flex">
  <div class="w-1/3">
    <iframe src="/bot1.html" height="600" class="mx-auto" title="bot1" />
  </div>
  <div class="w-1/3">
    <iframe src="/bot2.html" height="600" class="mx-auto" title="bot2" />
  </div>
  <div class="w-1/3">
    <iframe src="/bot3.html" height="600" class="mx-auto" title="bot3" />
  </div>
</div>
