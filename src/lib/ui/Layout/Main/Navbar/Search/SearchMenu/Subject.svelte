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

    const setSubject = (e: Event): void => {
        searchCriteria.subject = (e.target as HTMLInputElement).value;
    };
</script>

<FormGroup>
    <Label for="searching-subject">{local.subject[DEFAULT_LANGUAGE]}</Label>
    <Input.Basic
        type="text"
        id="searching-subject"
        placeholder={local.subject_placeholder[DEFAULT_LANGUAGE]}
        onkeydown={setSubject}
    />
</FormGroup>
