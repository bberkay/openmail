<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import { FormGroup } from "$lib/ui/Components/Form";
    import type { SearchCriteria } from "$lib/types";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";

    interface Props {
        searchCriteria: SearchCriteria,
        onSearch: (((e: Event) => void) | ((e: Event) => Promise<void>)),
    }

    let {
        searchCriteria = $bindable(),
        onSearch
    }: Props = $props();

    const clear = () => {
        searchCriteria = {};
    };
</script>

<FormGroup direction="horizontal" class="search-button-group">
    <Button.Basic type="button" class="btn-inline" onclick={clear}>
        <Icon name="trash" />
    </Button.Basic>
    <Button.Action type="button" class="btn-outline" onclick={onSearch}>
        <Icon name="search" />
        <span>{local.search[DEFAULT_LANGUAGE]}</span>
    </Button.Action>
</FormGroup>
