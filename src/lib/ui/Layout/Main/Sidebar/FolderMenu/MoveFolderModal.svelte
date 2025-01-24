<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import Form from "$lib/ui/Elements/Form";
    import Modal from "$lib/ui/Elements/Modal";

    const mailboxController = new MailboxController();

    interface Props {
        folderName: string
    }

    let { folderName }: Props = $props();

    const handleMoveFolderForm = async (e: Event): Promise<void> => {
        if (!SharedStore.currentAccount) {
            alert("Current account should be selected");
            return;
        }

        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;
        const destinationFolder = target.querySelector<HTMLSelectElement>(
            'select[name="destination_folder"]',
        )!.value;

        const response = await mailboxController.moveFolder(
            SharedStore.currentAccount,
            folderName,
            destinationFolder
        );
        if(!response.success){
            alert(response.message);
        }

        target.reset();
    }
</script>

<Modal>
    <Form onsubmit={handleMoveFolderForm}>
        <div class="form-group">
            <label for="folder-name">Select Folder</label>
            <div class="input-group">
                <input type="text" name="folder_name" id="folder-name" value={folderName} disabled>
            </div>
        </div>
        <div class="form-group">
            <label for="destination-folder">Destination Folder</label>
            <div class="input-group">
                <select name="destination_folder" id="destination-folder">
                    <option value="" selected>Select Destination Folder</option>
                    {#each SharedStore.customFolders[0].result.filter((folder) => folder !== folderName) as folder}
                        <option value={folder}>{folder}</option>
                    {/each}
                </select>
            </div>
        </div>
        <div class="display:flex;justify-content:space-between:align-items:center;">
            <button type="submit" class="bg-primary">Move</button>
        </div>
    </Form>
</Modal>
