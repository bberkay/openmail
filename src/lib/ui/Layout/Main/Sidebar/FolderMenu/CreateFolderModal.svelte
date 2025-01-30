<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import Form from "$lib/ui/Elements/Form";
    import Modal from "$lib/ui/Elements/Modal";
    import * as Select from "$lib/ui/Elements/Select";

    const mailboxController = new MailboxController();

    interface Props {
        parentFolderName: string | null,
    }

    let { parentFolderName }: Props = $props();

    onMount(() => {
        if (parentFolderName) {
            document.getElementById("parent-folder")!.setAttribute("disabled", "true");
        }
    });

    const handleCreateFolderForm = async (e: Event): Promise<void> => {
        if (!SharedStore.currentAccount) {
            alert("Current account should be selected");
            return;
        }

        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;

        const response = await mailboxController.createFolder(
            SharedStore.currentAccount,
            folderName,
            parentFolderName || undefined
        );
        if(!response.success){
            alert(response.message);
        }

        target.reset();
    }

    const handleParentFolder = (selectedOption: string | null) => {
        parentFolderName = selectedOption;
    }
</script>

<Modal>
    <Form onsubmit={handleCreateFolderForm}>
        <div class="form-group">
            <label for="folder-name">Folder Name</label>
            <input
                type="text"
                name="folder_name"
                id="folder-name"
                placeholder="My New Folder"
                required
            />
        </div>
        <div class="form-group">
            <label for="parent-folder">Parent Folder</label>
            <div class="input-group">
                <Select.Menu placeholder="Select Parent Folder" value={parentFolderName || undefined} onchange={handleParentFolder}>
                    {#each SharedStore.customFolders[0].result as customFolder}
                        <Select.Option value={customFolder}>{customFolder}</Select.Option>
                    {/each}
                </Select.Menu>
            </div>
        </div>
        <div class="display:flex;justify-content:space-between:align-items:center;">
            <button type="submit" class="bg-primary">Create</button>
        </div>
    </Form>
</Modal>
