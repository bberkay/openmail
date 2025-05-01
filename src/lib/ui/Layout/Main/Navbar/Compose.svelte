<script lang="ts">
    import Icon from "$lib/ui/Components/Icon";
    import * as Button from "$lib/ui/Components/Button";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";

    const showCompose = () => {
        showContent(Compose);
    }
</script>

<Button.Basic
    type="button"
    class="btn-cta nav-button compose-button"
    style="width:auto"
    onclick={showCompose}
>
    <Icon name="compose" style="fill:var(--color-bg-primary)"/>
    Compose
</Button.Basic>
