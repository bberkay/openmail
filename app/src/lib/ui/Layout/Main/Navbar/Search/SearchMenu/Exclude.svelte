<script lang="ts">
    import * as Input from "$lib/ui/Components/Input";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import type { SearchCriteria } from "$lib/types";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";

    interface Props {
        searchCriteria: SearchCriteria
    }

    let {
        searchCriteria = $bindable()
    }: Props = $props();

    const setExclude = (e: Event): void => {
        searchCriteria.exclude = (e.target as HTMLInputElement).value;
    };
</script>

<FormGroup>
    <Label for="searching-exclude">{local.excludes[DEFAULT_LANGUAGE]}</Label>
    <Input.Basic
        type="text"
        id="searching-exclude"
        placeholder={local.excludes_placeholder[DEFAULT_LANGUAGE]}
        onkeydown={setExclude}
    />
</FormGroup>
