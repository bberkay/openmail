<script lang="ts">
    import { MailboxController } from "$lib/controllers/MailboxController";
    import Form from "$lib/components/Elements/Form.svelte";
    import Modal from "$lib/components/Elements/Modal.svelte";

    const mailboxController = new MailboxController();

    interface Props {
        folderName: string
    }

    let { folderName }: Props = $props();

    const handleRenameFolderForm = async (e: Event): Promise<void> => {
        const target = e.target as HTMLFormElement;
        const folderPath = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;
        let newFolderName = target.querySelector<HTMLSelectElement>(
            'input[name="new_folder_name"]',
        )!.value;

        const response = await mailboxController.renameFolder(folderPath, newFolderName);
        if(!response.success){
            alert(response.message);
        }

        target.reset();
    }
</script>

<Modal>
    <Form onsubmit={handleRenameFolderForm}>
        <div class="form-group">
            <label for="folder-name">Folder Name</label>
            <input
                type="text"
                name="folder_name"
                id="folder-name"
                value={folderName}
                disabled
                required
            />
        </div>
        <div class="form-group">
            <label for="new-folder-name">New Folder Name</label>
            <div class="input-group">
                <input
                    type="text"
                    name="new_folder_name"
                    id="new-folder-name"
                    placeholder="New Folder Name"
                    required
                />
            </div>
        </div>
        <div class="display:flex;justify-content:space-between:align-items:center;">
            <button type="submit" class="bg-primary">Rename</button>
        </div>
    </Form>
</Modal>
