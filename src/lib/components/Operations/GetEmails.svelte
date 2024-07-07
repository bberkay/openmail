<section class="get-emails">
    <div class="card">
        <form id="get-emails-form">
            <div class="form-group">
                <label for="email_address">Email Address</label>
                <input type="email" name="email_address" id="email_address" required>
            </div>
            <div class="form-group">
                <label for="folder">Folder</label>
                <select name="folder_name" id="folder_name"></select>
            </div>
            <div class="form-group">
                <label for="search">Search</label>
                <div class="input-group">
                    <input type="text" name="search" id="search">
                    <button type="button">⇅</button>
                </div>
            </div>
            <input type="hidden" name="operation" value="get-emails">
            <button type="submit">Get Emails</button>
        </form>
    </div>
</section>
