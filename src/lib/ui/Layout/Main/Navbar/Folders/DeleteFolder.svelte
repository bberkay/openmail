<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account } from "$lib/types";
    import Form, { FormGroup } from "$lib/ui/Components/Form";
    import Modal from "$lib/ui/Components/Modal";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import { show as showMessage } from "$lib/ui/Components/Message";

    interface Props {
        folderName: string;
    }

    let { folderName }: Props = $props();

    const handleDeleteFolderForm = async (e: Event): Promise<void> => {
        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;
        const delete_subfolders = target.querySelector<HTMLInputElement>(
            'input[name="delete_subfolders"]',
        )!.checked;

        const response = await MailboxController.deleteFolder(
            SharedStore.currentAccount as Account,
            folderName,
            delete_subfolders,
        );
        if (!response.success) {
            showMessage({ content: "Error while deleting folder." });
            console.error(response.message);
        }

        target.reset();
    };
</script>

<Modal>
    <Form onsubmit={handleDeleteFolderForm}>
        <div>
            <FormGroup>
                <Label for="folder-name">Folder Name</Label>
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
                <label for="subfolders">Delete Subfolders</label>
                <Input.Basic
                    type="checkbox"
                    name="delete_subfolders"
                    id="subfolders"
                    required
                />
            </FormGroup>
            <Button.Basic type="submit">Delete</Button.Basic>
        </div>
    </Form>
</Modal>
