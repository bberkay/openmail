<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import Icon from "$lib/ui/Components/Icon";
    import Label from "$lib/ui/Components/Label";
    import Badge from "$lib/ui/Components/Badge";
    import { FormGroup } from "$lib/ui/Components/Form";
    import type { SearchCriteria } from "$lib/types";
    import { addEmailToAddressList } from "$lib/utils";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";

    interface Props {
        searchCriteria: SearchCriteria
    }

    let {
        searchCriteria = $bindable()
    }: Props = $props();

    const addCc = (e: Event) => {
        if (!searchCriteria.cc) searchCriteria.cc = [];
        const targetInput = (e.target as HTMLElement)
            .closest(".form-group")!
            .querySelector<HTMLInputElement>('input[id="searching-cc"]')!;
        addEmailToAddressList(e, targetInput, searchCriteria.cc);
    };
</script>

<FormGroup>
    <Label for="searching-cc">{local.cc[DEFAULT_LANGUAGE]}</Label>
    <Input.Group>
        <Input.Basic
            type="email"
            id="searching-cc"
            placeholder={local.add_email_address_with_space_placeholder[DEFAULT_LANGUAGE]}
            onkeyup={addCc}
            onblur={addCc}
        />
        <Button.Basic type="button" onclick={addCc}>
            <Icon name="add" />
        </Button.Basic>
    </Input.Group>
    <div class="tags">
        {#if searchCriteria.cc}
            {#each searchCriteria.cc as cc}
                <Badge
                    content={cc}
                    righticon="close"
                    onclick={() => {
                        searchCriteria.cc =
                            searchCriteria.cc!.filter(
                                (addr) => addr !== cc,
                            );
                    }}
                />
            {/each}
        {/if}
    </div>
</FormGroup>
