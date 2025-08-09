<script lang="ts">
    import * as Input from "$lib/ui/Components/Input";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import type { SearchCriteria } from "$lib/types";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";

    interface Props {
        searchCriteria: SearchCriteria;
    }

    let { searchCriteria = $bindable() }: Props = $props();

    const setHasAttachments = (e: Event) => {
        searchCriteria.has_attachments = (e.target as HTMLInputElement).checked;
    };
</script>

<FormGroup direction="horizontal">
    <Input.Basic
        type="checkbox"
        id="has-attachments"
        onchange={setHasAttachments}
    />
    <Label for="has-attachments">
        {local.has_attachments[DEFAULT_LANGUAGE]}
    </Label>
</FormGroup>
