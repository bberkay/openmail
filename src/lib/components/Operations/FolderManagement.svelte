<script lang="ts">
    function showFolderManagementForm(formId: string): void {
        document.querySelector('.folder-management-form.active')!.classList.remove('active');
        document.querySelector(`#${formId}`)!.classList.add('active');
    }
</script>

<section class="folder-management">
    <div class="folder-management-buttons card">
        <button on:click={() => showFolderManagementForm("create-folder-form")}>Create Folder</button>
        <button on:click={() => showFolderManagementForm("rename-folder-form")}>Rename Folder</button>
        <button on:click={() => showFolderManagementForm("delete-folder-form")}>Delete Folder</button>
        <button on:click={() => showFolderManagementForm("move-folder-form")}>Move Folder</button>
    </div>
    <div class="card">
        <form class = "folder-management-form active" id="create-folder-form">
            <div class="form-group">
                <label for="folder_name">Folder Name</label>
                <input type="text" name="folder_name" id="folder_name" required>
            </div>
            <div class="form-group">
                <label for="parent_folder">Parent Folder</label>
                <select name="parent_folder" id="parent_folder"></select>
            </div>
            <input type="hidden" name="operation" value="create-folder">
            <button type="submit">Create</button>
        </form>
        <form class = "folder-management-form" id="rename-folder-form">
            <div class="form-group">
                <label for="folder_name">Folder Name</label>
                <select name="folder_name" id="folder_name" required></select>
            </div>
            <div class="form-group">
                <label for="new_folder_name">New Folder Name</label>
                <input type="text" name="new_folder_name" id="new_folder_name" required>
            </div>
            <input type="hidden" name="operation" value="rename-folder">
            <button type="submit">Rename</button>
        </form>
        <form class = "folder-management-form" id="delete-folder-form">
            <div class="form-group">
                <label for="folder_name">Folder</label>
                <select name="folder_name" id="folder_name"></select>
            </div>
            <input type="hidden" name="operation" value="delete-folder">
            <button type="submit">Delete</button>
        </form>
        <form class = "folder-management-form" id="move-folder-form">
            <label for="folder_name">Source Folder</label>
            <select name="folder_name" id="folder_name" required></select>
            <label for="destination_folder">Destination Folder</label>
            <select name="destination_folder" id="destination_folder" required></select>
            <input type="hidden" name="operation" value="move-folder">
            <button type="submit">Move</button>
        </form>
    </div>
</section>

<style>
    .folder-management-form{
        display: none;

        &.active{
            display: flex;
        }
    }
</style>