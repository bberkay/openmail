<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import SearchMenu from "./Search/SearchMenu.svelte";
    import { show as showModal } from "$lib/ui/Components/Modal";
    import * as Input from "$lib/ui/Components/Input";

    const showSearchMenu = () => {
        showModal(SearchMenu);
    };
</script>

<Input.Basic
    type="text"
    id="simple-search"
    style="width:500px;padding:0;"
    placeholder="Search emails, contacts, labels"
/>
<Button.Basic
    type="button"
    class="btn-outline btn-sm"
    onclick={showSearchMenu}
>
    <Icon name="search" />
</Button.Basic>
