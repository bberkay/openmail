<script lang="ts">
    import * as Input from "$lib/ui/Components/Input";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import type { SearchCriteria } from "$lib/types";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { convertToIMAPDate } from "$lib/utils";

    interface Props {
        searchCriteria: SearchCriteria,
    }

    let {
        searchCriteria = $bindable()
    }: Props = $props();

    let selectedSince: Date | undefined = $state();
    let selectedBefore: Date | undefined = $state();

    const setSince = (selectedDate: Date) => {
        selectedSince = selectedDate;
        searchCriteria.since = convertToIMAPDate(selectedSince);
        if (selectedSince && selectedBefore && selectedSince > selectedBefore) {
            selectedBefore.setDate(selectedSince.getDate() + 1);
        }
    };

    const setBefore = (selectedDate: Date) => {
        selectedBefore = selectedDate;
        searchCriteria.before = convertToIMAPDate(selectedBefore);
        if (selectedSince && selectedBefore && selectedSince > selectedBefore) {
            selectedSince.setDate(selectedBefore.getDate() - 1);
        }
    };
</script>

<!-- TODO: Datepicker should be smaller -->
<FormGroup>
    <Label>{local.date_range[DEFAULT_LANGUAGE]}</Label>
    <FormGroup direction="horizontal">
        <FormGroup style="width:100%">
            <Label for="since">{local.since[DEFAULT_LANGUAGE]}</Label>
            <Input.Date
                id="since"
                value={selectedSince}
                onchange={setSince}
            />
        </FormGroup>
        <FormGroup style="width:100%">
            <Label for="before">{local.before[DEFAULT_LANGUAGE]}</Label>
            <Input.Date
                id="before"
                value={selectedBefore}
                onchange={setBefore}
            />
        </FormGroup>
    </FormGroup>
</FormGroup>
