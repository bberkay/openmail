<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Select from "$lib/components/Elements/Select.svelte";
    import Option from "$lib/components/Elements/Option.svelte";
    import Modal from "$lib/components/Elements/Modal.svelte";
    import Form from "$lib/components/Elements/Form.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";

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
        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;

        const response = await mailboxController.createFolder(folderName, parentFolderName || undefined);
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
                <Select placeholder="Select Parent Folder" value={parentFolderName || undefined} onchange={handleParentFolder}>
                    {#each SharedStore.customFolders[0].result as customFolder}
                        <Option value={customFolder}>{customFolder}</Option>
                    {/each}
                </Select>
            </div>
        </div>
        <div class="display:flex;justify-content:space-between:align-items:center;">
            <button type="submit" class="bg-primary">Create</button>
        </div>
    </Form>
</Modal>
