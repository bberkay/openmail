<script lang="ts">
    import Toolbox from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox.svelte";
    import Content from "$lib/ui/Layout/Main/Content/Mailbox/Content.svelte";

    let emailSelection: "1:*" | string[] = $state([]);
</script>

<Toolbox bind:emailSelection />
<Content bind:emailSelection />
