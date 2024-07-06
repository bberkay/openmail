<div id="folder-management-form">
    <div class="folder-management-buttons">
        <button id="create-folder-button">Create Folder</button>
        <button id="rename-folder-button">Rename Folder</button>
        <button id="delete-folder-button">Delete Folder</button>
        <button id="move-folder-button">Move Folder</button>
    </div>
    <form id="create-folder-form">
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
    <form id="rename-folder-form">
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
    <form id="delete-folder-form">
        <div class="form-group">
            <label for="folder_name">Folder</label>
            <select name="folder_name" id="folder_name"></select>
        </div>
        <input type="hidden" name="operation" value="delete-folder">
        <button type="submit">Delete</button>
    </form>
    <form id="move-folder-form">
        <label for="folder_name">Source Folder</label>
        <select name="folder_name" id="folder_name" required></select>
        <label for="destination_folder">Destination Folder</label>
        <select name="destination_folder" id="destination_folder" required></select>
        <input type="hidden" name="operation" value="move-folder">
        <button type="submit">Move</button>
    </form>
</div>