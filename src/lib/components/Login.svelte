<script lang="ts">
    import { onMount } from "svelte";
    import type { OpenMailDataString } from "$lib/types";
    import { createEventDispatcher } from "svelte";
	import { invoke } from "@tauri-apps/api/core";

    const dispatch = createEventDispatcher();
    let loginButton: HTMLButtonElement;
    onMount(() => {
        loginButton = document.getElementById('login-button')! as HTMLButtonElement;
    });

    async function handleLoginOnSubmit(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;

        loginButton.disabled = true;
        loginButton.textContent = 'Logging in...';
        const response: OpenMailDataString = await invoke('login', { email: form.email_address.value, password: form.password.value });
        dispatch('login', JSON.parse(response));
    }
</script>

<section class="add-email">
    <div class="card">
        <form on:submit={handleLoginOnSubmit}>
            <div class="form-group">
                <label for="email_address">Email Address</label>
                <input type="email" name="email_address" id="email_address" autocomplete="off" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" name="password" id="password" required>
            </div>
            <input type="hidden" name="operation" value="add-account">
            <button type="submit" id="login-button">Login to your Email</button>
        </form>
    </div>
</section>

<style>
    input:-webkit-autofill {
        -webkit-box-shadow: 0 0 0 1000px white inset;
    }

    .add-email{
        width: 100%;
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        & .card{
            width: 300px;
        }
    }
</style>