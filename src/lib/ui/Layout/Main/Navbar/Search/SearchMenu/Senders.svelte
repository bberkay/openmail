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

    const addSender = (e: Event) => {
        if (!searchCriteria.senders) searchCriteria.senders = [];
        const targetInput = (e.target as HTMLElement)
            .closest(".form-group")!
            .querySelector<HTMLInputElement>('input[id="searching-senders"]')!;
        addEmailToAddressList(e, targetInput, searchCriteria.senders);
    };
</script>

<FormGroup>
    <Label for="searching-senders">{local.sender_s[DEFAULT_LANGUAGE]}</Label>
    <Input.Group>
        <Input.Basic
            type="email"
            id="searching-senders"
            placeholder={local.add_email_address_with_space_placeholder[DEFAULT_LANGUAGE]}
            onkeyup={addSender}
            onblur={addSender}
        />
        <Button.Basic type="button" onclick={addSender}>
            <Icon name="add" />
        </Button.Basic>
    </Input.Group>
    <div class="tags">
        {#if searchCriteria.senders}
            {#each searchCriteria.senders as sender}
                <Badge
                    content={sender}
                    onclick={() => {
                        searchCriteria.senders =
                            searchCriteria.senders!.filter(
                                (addr) => addr !== sender,
                            );
                    }}
                />
            {/each}
        {/if}
    </div>
</FormGroup>
