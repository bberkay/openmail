<script lang="ts">
    import { onMount } from "svelte";
    import type { OpenMailData } from "$lib/types";
    import { createEventDispatcher } from "svelte";

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
        // TODO: Change this after the login system is done.
        const response: OpenMailData = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            body: new FormData(form)
        }).then(res => res.json());
        dispatch('login', response);
    }
</script>

<section class="add-email">
    <div class="card">
        <form on:submit={handleLoginOnSubmit}>
            <div class="form-group">
                <label for="email">Email Address</label>
                <!-- svelte-ignore a11y-autofocus -->
                <input type="email" name="email" id="email" autocomplete="off" value="testforprojects42webio@gmail.com" autofocus required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" name="password" id="password" autocomplete="off" required>
            </div>
            <button type="submit" id="login-button">Login to your Email</button>
        </form>
    </div>
</section>

<style>
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