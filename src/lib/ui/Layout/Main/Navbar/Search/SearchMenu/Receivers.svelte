<script lang="ts">
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import Label from "$lib/ui/Components/Label";
    import Badge from "$lib/ui/Components/Badge";
    import { FormGroup } from "$lib/ui/Components/Form";
    import type { SearchCriteria } from "$lib/types";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { addEmailToAddressList } from "$lib/utils";

    interface Props {
        searchCriteria: SearchCriteria
    }

    let {
        searchCriteria = $bindable()
    }: Props = $props();

    const addReceiver = (e: Event) => {
        if (!searchCriteria.receivers) searchCriteria.receivers = [];
        const targetInput = (e.target as HTMLElement)
            .closest(".form-group")!
            .querySelector<HTMLInputElement>(
                'input[id="searching-receivers"]',
            )!;
        addEmailToAddressList(e, targetInput, searchCriteria.receivers);
    };
</script>

<FormGroup>
    <Label for="searching-receivers">{local.receiver_s[DEFAULT_LANGUAGE]}</Label>
    <Input.Group>
        <Input.Basic
            type="email"
            id="searching-receivers"
            placeholder={local.add_email_address_with_space_placeholder[DEFAULT_LANGUAGE]}
            onkeyup={addReceiver}
            onblur={addReceiver}
        />
        <Button.Basic type="button" onclick={addReceiver}>
            <Icon name="add" />
        </Button.Basic>
    </Input.Group>
    <div class="tags">
        {#if searchCriteria.receivers}
            {#each searchCriteria.receivers as receiver}
                <Badge
                    content={receiver}
                    onclick={() => {
                        searchCriteria.receivers =
                            searchCriteria.receivers!.filter(
                                (addr) => addr !== receiver,
                            );
                    }}
                />
            {/each}
        {/if}
    </div>
</FormGroup>
