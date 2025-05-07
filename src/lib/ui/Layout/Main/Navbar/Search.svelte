<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import SearchMenu from "./Search/SearchMenu.svelte";
    import { show as showModal } from "$lib/ui/Components/Modal";

    const showSearchMenu = () => {
        showModal(SearchMenu);
    };
</script>

<Button.Basic
    type="button"
    class="btn-outline"
    onclick={showSearchMenu}
>
    <Icon name="search" />
</Button.Basic>
