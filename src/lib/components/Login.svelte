<script lang="ts">
	import { invoke } from "@tauri-apps/api/core";

    let is_logged_in = false;
    async function handleAddAccount(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;
        
        is_logged_in = await invoke('login', { email: form.email_address.value, password: form.password.value });
        console.log(is_logged_in);
    }
</script>

<section class="add-email">
    <div class="card">
        <form on:submit={handleAddAccount}>
            <div class="form-group">
                <label for="email_address">Email Address</label>
                <input type="email" name="email_address" id="email_address" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" name="password" id="password" required>
            </div>
            <input type="hidden" name="operation" value="add-account">
            <button type="submit">Login to your Email</button>
        </form>
    </div>
</section>

<p>{is_logged_in}</p>

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