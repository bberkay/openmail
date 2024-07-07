<script lang="ts">
    function handleAddAccount(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        console.log(data);
    }
</script>

<section class="add-email">
    <div class="card">
        <h2>Add Account</h2>
        <hr>
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
            <button type="submit">Add</button>
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