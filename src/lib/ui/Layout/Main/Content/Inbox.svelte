<script lang="ts">
    import Toolbox from "$lib/ui/Layout/Main/Content/Inbox/Toolbox.svelte";
    import Content from "$lib/ui/Layout/Main/Content/Inbox/Content.svelte";

    let emailSelection: string[] = $state([]);
</script>

<Toolbox bind:emailSelection />
<Content bind:emailSelection />
