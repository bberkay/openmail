<script lang="ts">
    function handleLoginOnSubmit(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        console.log(data);
    }
</script>

<section class="login">
    <div class="card">
        <h2>Login</h2>
        <hr>
        <form on:submit={handleLoginOnSubmit}>
            <div class="form-group">
                <label for="email_address">Email Address</label>
                <input type="email" name="email_address" id="email_address" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" name="password" id="password" required>
            </div>
            <input type="hidden" name="operation" value="login">
            <button type="submit">Login</button>
        </form>
    </div>
</section>

<style>
    .login{
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