<script lang="ts">
    import { onMount } from 'svelte';

    onMount(() => {
        // @ts-ignore
        const body = new WYSIWYGEditor('body');
        body.init();
    });
</script>

<section class="card">
    <h2>Send Email</h2>
    <hr>
    <div>
        <form id="send-email-form">
            <div class="form-group">
                <label for="receiver_emails">Receiver(s)</label>
                <input type="email" name="receiver_emails" id="receiver_emails" required>
                <div class="receivers"></div>
            </div>
            <div class="form-group">
                <label for="subject">Subject</label>
                <input type="text" name="subject" id="subject" required>
            </div>
            <div class="form-group">
                <label for="body">Body</label>
                <div id="body"></div>
            </div>
            <div class="form-group">
                <label for="attachments">Attachment(s)</label>
                <input type="file" name="attachments" id="attachments" multiple>
            </div>
            <input type="number" name="message_id" hidden>
            <input type="text" name="operation" value="send-email" hidden required>
            <button type="submit">Send</button>
        </form>
    </div>
</section>