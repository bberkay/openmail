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
        parentFolderName?: string;
    }

    let { parentFolderName }: Props = $props();

    let customFoldersOfAccount = $derived(
        SharedStore.customFolders.find(
            (acc) =>
                acc.email_address === SharedStore.currentAccount.email_address,
        )!.result,
    );

    const handleCreateFolderForm = async (e: Event): Promise<void> => {
        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;

        const response = await MailboxController.createFolder(
            SharedStore.currentAccount,
            folderName,
            parentFolderName || undefined,
        );
        if (!response.success) {
            showMessage({ content: "Error while creating folder. " });
            console.error(response.message);
        }

        target.reset();
    };

    const handleParentFolder = (selectedOption: string) => {
        parentFolderName = selectedOption;
    };
</script>

<Modal>
    <Form onsubmit={handleCreateFolderForm}>
        <div>
            <FormGroup>
                <Label for="folder-name">Folder Name</Label>
                <Input.Basic
                    type="text"
                    name="folder_name"
                    id="folder-name"
                    placeholder="My New Folder"
                    required
                />
            </FormGroup>
            <FormGroup>
                <Label for="parent-folder">Parent Folder</Label>
                <Select.Root
                    id="parent-folder"
                    onchange={handleParentFolder}
                    placeholder="Select Parent Folder"
                    value={parentFolderName || undefined}
                    disabled={!!parentFolderName}
                >
                    {#each customFoldersOfAccount as customFolder}
                        <Select.Option value={customFolder}>
                            {customFolder}
                        </Select.Option>
                    {/each}
                </Select.Root>
            </FormGroup>
            <Button.Basic type="submit">Create</Button.Basic>
        </div>
    </Form>
</Modal>
