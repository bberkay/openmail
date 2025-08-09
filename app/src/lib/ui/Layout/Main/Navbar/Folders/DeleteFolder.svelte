<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/mailbox";
    import { type Account } from "$lib/types";
    import Form, { FormGroup } from "$lib/ui/Components/Form";
    import Modal from "$lib/ui/Components/Modal";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { show as showToast } from "$lib/ui/Components/Toast";

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
            showMessage({ title: local.error_delete_folder[DEFAULT_LANGUAGE] });
            console.error(response.message);
        } else {
            showToast({ content: "delete success" });
        }

        target.reset();
    };
</script>

<Modal>
    <Form onsubmit={handleDeleteFolderForm}>
        <FormGroup>
            <Label for="folder-name">
                {local.folder_name[DEFAULT_LANGUAGE]}
            </Label>
            <Input.Basic
                type="text"
                name="folder_name"
                id="folder-name"
                value={folderName}
                disabled
                required
            />
        </FormGroup>
        <FormGroup direction="horizontal">
            <Input.Basic
                type="checkbox"
                name="delete_subfolders"
                id="subfolders"
                required
            />
            <label for="subfolders">
                {local.delete_subfolders[DEFAULT_LANGUAGE]}
            </label>
        </FormGroup>
        <div class="modal-footer">
            <Button.Basic
                type="button"
                class="btn-inline"
                data-modal-close
            >
                <span>{local.cancel[DEFAULT_LANGUAGE]}</span>
            </Button.Basic>
            <Button.Basic
                type="submit"
                style="width:auto"
                class="btn-cta"
            >
                {local.delete[DEFAULT_LANGUAGE]}
            </Button.Basic>
        </div>
    </Form>
</Modal>
