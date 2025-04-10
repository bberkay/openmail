<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account } from "$lib/types";
    import { isTopLevel } from "$lib/utils";
    import Form, { FormGroup } from "$lib/ui/Components/Form";
    import Modal from "$lib/ui/Components/Modal";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    interface Props {
        folderName: string;
    }

    let { folderName }: Props = $props();

    let destinationFolder = $state("");
    let customFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.folders[
                (SharedStore.currentAccount as Account).email_address
            ].custom
            : []
    );

    const handleMoveFolderForm = async (e: Event): Promise<void> => {
        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;

        const response = await MailboxController.moveFolder(
            SharedStore.currentAccount as Account,
            folderName,
            destinationFolder,
        );
        if (!response.success) {
            showMessage({ content: local.error_move_folder[DEFAULT_LANGUAGE] });
            console.error(response.message);
        }

        target.reset();
    };

    const handleDestinationFolder = (selectedOption: string) => {
        destinationFolder = selectedOption;
    };
</script>

<Modal>
    <Form onsubmit={handleMoveFolderForm}>
        <div>
            <FormGroup>
                <Label for="folder-name">{local.select_folder[DEFAULT_LANGUAGE]}</Label>
                <Input.Basic
                    type="text"
                    name="folder_name"
                    id="folder-name"
                    value={folderName}
                    disabled
                    required
                />
            </FormGroup>
            <FormGroup>
                <Label for="destination-folder">{local.destination_folder[DEFAULT_LANGUAGE]}</Label>
                <Select.Root
                    id="destination-folder"
                    onchange={handleDestinationFolder}
                    placeholder={local.folder_name[DEFAULT_LANGUAGE]}
                >
                    {#if !isTopLevel(folderName)}
                        <Select.Option value="">/</Select.Option>
                    {/if}
                    {#each customFolders as customFolder}
                        {#if customFolder !== folderName}
                            <Select.Option value={customFolder}>
                                {customFolder}
                            </Select.Option>
                        {/if}
                    {/each}
                </Select.Root>
            </FormGroup>
            <Button.Basic type="submit">{local.move[DEFAULT_LANGUAGE]}</Button.Basic>
        </div>
    </Form>
</Modal>
