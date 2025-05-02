<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import SearchMenu from "./Search/SearchMenu.svelte";

    let isSimpleSearchHidden = $state(true);

    const toggleSimpleSearch = () => {
        isSimpleSearchHidden = !isSimpleSearchHidden;
    };

    const handleShortcuts = (e: KeyboardEvent) => {
        if (e.key === "Escape") {
            e.preventDefault();
            isSimpleSearchHidden = true;
        }
    };
</script>

<svelte:window onkeydown={handleShortcuts} />

<Button.Basic
    type="button"
    class="btn-outline"
    onclick={toggleSimpleSearch}
>
    <Icon name="search" />
</Button.Basic>

<SearchMenu bind:isSimpleSearchHidden />
