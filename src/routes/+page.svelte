<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";

  let greetMsg = "";

  async function greet() {
    greetMsg = await invoke("greet");
  }
</script>

<div class="container">
  <h1>Welcome to Tauri!</h1>

   <button type="submit" on:click={greet}>Greet</button>

  <p>{greetMsg}</p>
</div>
