<script lang="ts">
    import MailboxLength from "./Mailbox/MailboxLength.svelte";
    import SendDelay from "./Mailbox/SendDelay.svelte";
</script>

<div class="settings-content-header">
    <h1 class="settings-content-title">Mailbox</h1>
    <span class="settings-content-description muted">These are general settings for your application.</span>
</div>
<div class="settings-content-body">
    <MailboxLength />
    <SendDelay />
</div>
