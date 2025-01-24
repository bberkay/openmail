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

    const handleDeleteFolderForm = async (e: Event): Promise<void> => {
        if (!SharedStore.currentAccount) {
            alert("Current account should be selected");
            return;
        }

        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;
        const subfolders = target.querySelector<HTMLInputElement>(
            'input[name="subfolders"]',
        )!.checked;

        const response = await mailboxController.deleteFolder(
            SharedStore.currentAccount,
            folderName,
            subfolders
        );
        if(!response.success){
            alert(response.message);
        }

        target.reset();
    }
</script>

<Modal>
    <Form onsubmit={handleDeleteFolderForm}>
        <div class="form-group">
            <label for="folder-name">Folder Name</label>
            <input
                type="text"
                name="folder_name"
                id="folder-name"
                placeholder="My New Folder"
                value={folderName}
                disabled
                required
            />
        </div>
        <div class="form-group">
            <label for="subfolders">Delete Subfolders</label>
            <input
                type="checkbox"
                name="subfolders"
                id="subfolders"
            />
        </div>
        <div class="display:flex;justify-content:space-between:align-items:center;">
            <button type="submit" class="bg-primary">Delete</button>
        </div>
    </Form>
</Modal>
