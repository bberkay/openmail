<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/mailbox";
    import { type Account } from "$lib/types";
    import Form, { FormGroup } from "$lib/ui/Components/Form";
    import Modal from "$lib/ui/Components/Modal";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { show as showToast } from "$lib/ui/Components/Toast";

    interface Props {
        parentFolderName?: string;
    }

    let { parentFolderName }: Props = $props();

    let customFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.folders[
                  (SharedStore.currentAccount as Account).email_address
              ].custom
            : [],
    );

    const handleCreateFolderForm = async (e: Event): Promise<void> => {
        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;

        const response = await MailboxController.createFolder(
            SharedStore.currentAccount as Account,
            folderName,
            parentFolderName || undefined,
        );
        if (!response.success) {
            showMessage({ title: local.error_create_folder[DEFAULT_LANGUAGE] });
            console.error(response.message);
        } else {
            showToast({ content: "create success" });
        }

        target.reset();
    };

    const handleParentFolder = (selectedOption: string) => {
        parentFolderName = selectedOption;
    };
</script>

<Modal>
    <Form onsubmit={handleCreateFolderForm}>
        <FormGroup>
            <Label for="folder-name">
                {local.folder_name[DEFAULT_LANGUAGE]}
            </Label>
            <Input.Basic
                type="text"
                name="folder_name"
                id="folder-name"
                placeholder={local.new_folder_placeholde[DEFAULT_LANGUAGE]}
                required
            />
        </FormGroup>
        <FormGroup>
            <Label for="parent-folder">
                {local.parent_folder[DEFAULT_LANGUAGE]}
            </Label>
            <Select.Root
                id="parent-folder"
                onchange={handleParentFolder}
                placeholder={local.select_parent_folder[DEFAULT_LANGUAGE]}
                value={parentFolderName || undefined}
                disabled={!!parentFolderName}
                style="width:100%"
            >
                {#each customFolders as customFolder}
                    <Select.Option
                        value={customFolder}
                        content={customFolder}
                    />
                {/each}
            </Select.Root>
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
                {local.create[DEFAULT_LANGUAGE]}
            </Button.Basic>
        </div>
    </Form>
</Modal>
