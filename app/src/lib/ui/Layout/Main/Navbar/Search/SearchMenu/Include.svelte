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

    const setInclude = (e: Event): void => {
        searchCriteria.include = (e.target as HTMLInputElement).value;
    };
</script>

<FormGroup>
    <Label for="searching-include">{local.includes[DEFAULT_LANGUAGE]}</Label>
    <Input.Basic
        type="text"
        id="searching-include"
        placeholder={local.includes_placeholder[DEFAULT_LANGUAGE]}
        onkeydown={setInclude}
    />
</FormGroup>
