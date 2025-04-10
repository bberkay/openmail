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
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    interface Props {
        folderName: string;
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

        const response = await MailboxController.renameFolder(
            SharedStore.currentAccount as Account,
            folderPath,
            newFolderName
        );
        if (!response.success) {
            showMessage({ content: local.error_rename_folder[DEFAULT_LANGUAGE] });
            console.error(response.message);
        }

        target.reset();
    };
</script>

<Modal>
    <Form onsubmit={handleRenameFolderForm}>
        <div>
            <FormGroup>
                <Label for="folder-name">{local.folder_name[DEFAULT_LANGUAGE]}</Label>
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
                <Label for="new-folder-name">{local.new_folder_name[DEFAULT_LANGUAGE]}</Label>
                <Input.Basic
                    type="text"
                    name="new_folder_name"
                    id="new-folder-name"
                    placeholder={local.new_folder_placeholde[DEFAULT_LANGUAGE]}
                    required
                />
            </FormGroup>
            <Button.Basic type="submit">{local.rename[DEFAULT_LANGUAGE]}</Button.Basic>
        </div>
    </Form>
</Modal>
