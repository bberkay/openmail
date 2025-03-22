<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import Form, { FormGroup } from "$lib/ui/Components/Form";
    import Modal from "$lib/ui/Components/Modal";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import { show as showMessage } from "$lib/ui/Components/Message";

    interface Props {
        folderName: string
    }

    let { folderName }: Props = $props();

    let destinationFolder = $state("");
    let customFoldersOfAccount = $derived(
        SharedStore.customFolders.find(
            (acc) =>
                acc.email_address === SharedStore.currentAccount.email_address,
        )!.result,
    );

    const handleMoveFolderForm = async (e: Event): Promise<void> => {
        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;

        const response = await MailboxController.moveFolder(
            SharedStore.currentAccount,
            folderName,
            destinationFolder
        );
        if (!response.success) {
            showMessage({ content: "Error while moving folder." });
            console.error(response.message);
        }

        target.reset();
    }

    const handleDestinationFolder = (selectedOption: string) => {
        destinationFolder = selectedOption;
    };
</script>

<Modal>
    <Form onsubmit={handleMoveFolderForm}>
        <div>
            <FormGroup>
                <Label for="folder-name">Select Folder</Label>
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
                <Label for="destination-folder">Destination Folder</Label>
                <Select.Root
                    id="destination-folder"
                    onchange={handleDestinationFolder}
                    placeholder="Select Destination Folder"
                >
                    {#each customFoldersOfAccount as customFolder}
                        {#if customFolder !== folderName}
                            <Select.Option value={customFolder}>
                                {customFolder}
                            </Select.Option>
                        {/if}
                    {/each}
                </Select.Root>
            </FormGroup>
            <Button.Basic type="submit">Move</Button.Basic>
        </div>
    </Form>
</Modal>
