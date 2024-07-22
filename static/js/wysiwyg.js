const DisplayMode = {
    FIXED: 'fixed',
    POPOVER: 'popover',
    TOOLTIP: 'tooltip'
};

class WYSIWYGEditor {
    #editor;
    #displayMode;
    #toolbar;
    #toolbarButtons;
    #body;
    #range;

    /**
     * @description Create a new WYSIWYG editor
     * @param {string} editorId The id of the editor element
     * @param {DisplayMode} mode The display mode of the editor
     */
    constructor(editorId, mode = DisplayMode.FIXED) {
        this.#editor = document.getElementById(editorId);
        if (!Object.values(DisplayMode).includes(mode))
            throw new Error('Invalid display mode, please use DisplayMode enum');
        this.#displayMode = mode;
    }
    
    /**
     * @description Initialize the editor
     * @returns {void}
     */
    init(){
        this.#createToolbar();
        this.#createBody();
    }
    
    /**
     * @private
     * @description Create the toolbar layout and append it to the editor
     * or the body depending on the display mode
     * @returns {void}
     */
    #createToolbar(){
        if(this.#displayMode == DisplayMode.POPOVER || this.#displayMode == DisplayMode.TOOLTIP)
            this.#createDynamicToolbar();
        else
            this.#createFixedToolbar();

        this.#toolbarButtons = this.#toolbar.querySelectorAll('button[data-command]');
        if(this.#toolbarButtons.length > 0)
            this.#createToolbarButtons();
        
        if(this.#toolbar.querySelector('.wysiwyg-toolbar-dropdown'))
            this.#createToolbarDropdowns();            
    }

    /**
     * @private
     * @description Create the fixed toolbar layout and append it to the editor
     * @returns {void}
     */
    #createFixedToolbar(){
        const currentToolbar = this.#editor.querySelector('.wysiwyg-toolbar');
        if(!currentToolbar){
            this.#editor.insertAdjacentHTML('afterbegin', '<div class="wysiwyg-toolbar wysiwyg-toolbar--fixed"></div>');
            this.#toolbar = this.#editor.querySelector('.wysiwyg-toolbar');
            this.#toolbar.innerHTML = this.#getDefaultToolbarLayout();
        }else{
            currentToolbar.classList.add('wysiwyg-toolbar--fixed');
            this.#toolbar = currentToolbar;
        }
    }

    /**
     * @private
     * @description Create the dynamic(popover or tooltip) toolbar layout and 
     * append it to the body
     * @returns {void}
     */
    #createDynamicToolbar(){
        const currentToolbar = this.#editor.querySelector('.wysiwyg-toolbar');
        if(!currentToolbar){
            this.#toolbar = document.createElement('div');
            this.#toolbar.classList.add('wysiwyg-toolbar');
            this.#toolbar.innerHTML = this.#getDefaultToolbarLayout();
        }else{
            this.#toolbar = currentToolbar;
            this.#editor.removeChild(this.#toolbar);
        }
        this.#toolbar.classList.add(`wysiwyg-toolbar--${this.#displayMode}`);
        document.body.appendChild(this.#toolbar);
    }

    /**
     * @private
     * @description This is the default toolbar layout, you can customize 
     * it(from here or .html file, for more information please
     * check the index.html from the original example) or create 
     * your own layout using the same structure as long as you keep 
     * the data-command and data-value attributes for the functionality 
     * of each button.
     * @returns {string} The default toolbar layout
     */
    #getDefaultToolbarLayout(){
        function getFontSizeDropdown(){
            return `
                <div class="wysiwyg-toolbar-dropdown">
                    <div class="wysiwyg-toolbar-dropdown-toggle">
                        <span>Normal</span>
                    </div>
                    <div class="wysiwyg-toolbar-dropdown-content">
                        <button type="button" data-command="fontSize" data-value="7">
                            <span>Huge</span>
                        </button>
                        <button type="button" data-command="fontSize" data-value="5">
                            <span>Large</span>
                        </button>
                        <button type="button" data-command="fontSize" data-value="3">
                            <span>Normal</span>
                        </button>
                        <button type="button" data-command="fontSize" data-value="1">
                            <span>Small</span>
                        </button>
                    </div>
                </div>
            `;
        }

        function getFontFamilyDropdown(){
            return `
                <div class="wysiwyg-toolbar-dropdown">
                    <div class="wysiwyg-toolbar-dropdown-toggle">
                        <span>Sans-Serif</span>
                    </div>
                    <div class="wysiwyg-toolbar-dropdown-content">
                        <button type="button" data-command="fontName" data-value="sans-serif" style="font-family:sans-serif;">
                            <span>Sans-Serif</span>
                        </button>
                        <button type="button" data-command="fontName" data-value="serif" style="font-family:serif;">
                            <span>Serif</span>
                        </button>
                        <button type="button" data-command="fontName" data-value="monospace" style="font-family:monospace;">
                            <span>Monospace</span>
                        </button>
                    </div>
                </div>
            `;
        }

        function getLetterStyleButtons(){
            return `
                <button type="button" data-command="bold" style="font-weight:bold;">
                    <span>B</span>
                </button>
                <button type="button" data-command="italic" style="font-style:italic;padding-right:10px;">
                    <span>I</span>
                </button>
                <button type="button" data-command="underline" style="text-decoration:underline;">
                    <span>U</span>
                </button>
                <button type="button" data-command="strikeThrough" style="text-decoration:line-through;">
                    <span>S</span>
                </button>
            `;
        }
        
        function getAlignmentButtons(){
            return `
                <button type="button" data-command="justifyLeft">
                    <span>L</span>
                </button>
                <button type="button" data-command="justifyCenter">
                    <span>C</span>
                </button>
                <button type="button" data-command="justifyRight">
                    <span>R</span>
                </button>
                <button type="button" data-command="justifyFull">
                    <span>J</span>
                </button>
            `;
        }

        function getIndentationButtons(){
            return `
                <button type="button" data-command="indent">
                    <span>Indent</span>
                </button>
                <button type="button" data-command="outdent">
                    <span>Outdent</span>
                </button>
            `;
        }

        function getListButtons(){
            return `
                <button type="button" data-command="insertUnorderedList">
                    <span>UL</span>
                </button>
                <button type="button" data-command="insertOrderedList">
                    <span>OL</span>
                </button>
            `;
        }

        function getTextLinkDropdown(){
            return `
                <div class="wysiwyg-toolbar-dropdown">
                    <div class="wysiwyg-toolbar-dropdown-toggle">
                        <span>Link</span>
                    </div>
                    <div class="wysiwyg-toolbar-dropdown-content">
                        <input type="url" data-command="createLink" placeholder="https://example.com">
                    </div>
                </div>
            `;
        }

        function getImageLinkDropdown(){
            return `
                <div class="wysiwyg-toolbar-dropdown">
                    <div class="wysiwyg-toolbar-dropdown-toggle">
                        <span>Image Link</span>
                    </div>
                    <div class="wysiwyg-toolbar-dropdown-content">
                        <input type="url" data-command="uploadImage" placeholder="https://example.com">
                    </div>
                </div>
            `;
        }

        function getImageUploadButton(){
            return `
                <button type="button" data-command="insertImage">
                    <span>Image</span>
                </button>
            `;
        }

        function getUnlinkButton(){
            return `
                <button type="button" data-command="unlink">
                    <span>Unlink</span>
                </button>
            `;
        }

        function getMiscButtons(){
            return `
                <button type="button" data-command="removeFormat">
                    <span>Clear</span>
                </button>
                <button type="button" data-command="undo">
                    <span>Undo</span>
                </button>
                <button type="button" data-command="redo">
                    <span>Redo</span>
                </button>
            `;
        }

        return `
            <div class="wysiwyg-toolbar-group">
                ${getFontSizeDropdown()}
                ${getFontFamilyDropdown()}
            </div>
            <div class="wysiwyg-toolbar-group">
                ${getLetterStyleButtons()}
            </div>
            <div class="wysiwyg-toolbar-group">
                ${getAlignmentButtons()}
            </div>
            <div class="wysiwyg-toolbar-group">
                ${getIndentationButtons()}
                ${getListButtons()}
            </div>
            <div class="wysiwyg-toolbar-group">
                ${getTextLinkDropdown()}
                ${getImageLinkDropdown()}
                ${getImageUploadButton()}
                ${getUnlinkButton()}
            </div>
            <div class="wysiwyg-toolbar-group">
                ${getMiscButtons()}
            </div>
        `;
    }

    /**
     * @private
     * @description Insert image(s) to the body
     * @returns {void}
     */
    #openImageDialog(){
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.multiple = true;
        input.click(); // Trigger the file upload dialog
        input.addEventListener('change', () => {
            const files = input.files;
            if (files.length === 0) return;
            new Promise((resolve) => {
                let remainingCount = files.length;
                for (const file of files) { 
                    const reader = new FileReader();
                    reader.onload = () => {
                        if (!this.#range) this.#body.focus();
                        else {
                            const selection = window.getSelection();
                            selection.removeAllRanges();
                            selection.addRange(this.#range);
                        }
                        document.execCommand('insertImage', false, reader.result);
                        remainingCount--;
                        if (remainingCount === 0)
                            resolve(files);
                    };
                    reader.readAsDataURL(file);
                }
            }).then((files) => {
                this.#body.querySelectorAll('img').forEach((image, index) => {
                    image.style.width = '100%';
                    image.addEventListener('mouseover', () => { image.title = files[index].name });
                });
                input.value = '';
            });
        });
    }

    /**
     * @private
     * @description Create the toolbar buttons and add the execCommand functionality
     * @returns {void}
     */
    #createToolbarButtons(){
        // Add the execCommand functionality to the buttons
        this.#toolbarButtons.forEach(button => {
            if(!button.getAttribute("type")) button.setAttribute('type', 'button');
            button.addEventListener("click", () => {
                if(button.dataset.command.includes('justify'))
                    this.#toolbar.querySelectorAll('[data-command^="justify"]').forEach(button => button.classList.remove('active'));
                document.execCommand(button.dataset.command, false, button.dataset.value);
                button.classList.toggle('active');
                this.#body.focus();
            });
        });
        
        const insertImageBtn = this.#toolbar.querySelector('[data-command="insertImage"]');
        if(insertImageBtn)
            insertImageBtn.addEventListener('click', async () => { this.#openImageDialog() });
    }

    /**
     * @private
     * @description Handle the dropdown input functionality
     * @param {HTMLInputElement} input The input element
     * @param {string} command The command to be executed
     * @param {function} afterClickCallback The callback function to be called after clicking the input
     * @param {function} afterExecCallback The callback function to be called after executing the command
     * @returns {void}
     */
    #handleDropdownInput(input, command, afterClickCallback = null, afterExecCallback = null){
        input.parentElement.previousElementSibling.addEventListener('click', () => {
            let selection = document.getSelection();
            if (selection.rangeCount === 0) return;
            this.#range = selection.getRangeAt(0);
            if(afterClickCallback) afterClickCallback(input, selection);
        });
        
        input.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                const selection = window.getSelection();
                if (this.#range) {
                    selection.removeAllRanges();
                    selection.addRange(this.#range);
                }else{
                    this.#body.focus();
                }

                document.execCommand(command, false, input.value);
                if(afterExecCallback) afterExecCallback(input);
            }
        });
    }

    /**
     * @private
     * @description Create the link input and add the functionality
     * @param {HTMLInputElement} input The input element
     * @returns {void}
     */
    #createLinkInput(input){
        this.#handleDropdownInput(input, 'createLink', (createLinkInput, selection) => {
            selection = selection.anchorNode.parentElement.tagName === "A" ? selection.anchorNode.parentElement.href : selection.toString();
            createLinkInput.value = selection;
        }, () => {
            this.#body.querySelectorAll('a').forEach(link => {
                link.target = '_blank';
                link.title = link.href;
                link.innerHTML = link.querySelector('span')?.innerHTML || link.innerHTML;
                link.addEventListener('click', (e) => { if(e.ctrlKey) window.open(link.href, '_blank') });
                link.addEventListener('mouseover', () => { 
                    document.addEventListener('keydown', (e) => { if(e.ctrlKey) link.style.cursor = 'pointer' });
                    document.addEventListener('keyup', () => { link.style.cursor = 'text' });
                });
                link.addEventListener('mouseout', () => { link.style.cursor = 'text' });
            });
        });
    }

    /**
     * @private
     * @description Create the image upload input and add the functionality
     * @param {HTMLInputElement} input The input element
     * @returns {void}
     */
    #createUploadImageInput(input){
        this.#handleDropdownInput(input, 'insertImage', null, () => {
            this.#body.querySelectorAll('img').forEach(image => {
                image.style.width = '100%';
                image.title = image.src;
            });
        });
    }

    /**
     * @private
     * @description Create the toolbar dropdowns and add the functionality
     * @returns {void}
     */
    #createToolbarDropdowns(){
        this.#toolbar.querySelectorAll('.wysiwyg-toolbar-dropdown-toggle').forEach(button => {
            button.addEventListener('click', () => {
                // Prevent opening multiple dropdowns at the same time
                this.#toolbar.querySelectorAll('.wysiwyg-toolbar-dropdown-content.show').forEach(dropdown => {
                    if (dropdown !== button.nextElementSibling)
                        dropdown.classList.remove('show');
                });
                
                button.nextElementSibling.classList.toggle('show');
            });
        });

        // Close the dropdown when clicking outside
        document.addEventListener('click', (event) => {
            if (!event.target.closest('.wysiwyg-toolbar-dropdown')){
                this.#toolbar.querySelectorAll('.wysiwyg-toolbar-dropdown-content').forEach(dropdown => {
                    dropdown.classList.remove('show');
                });
            }
        });

        // Close the dropdown when clicking on a button of the dropdown
        this.#toolbar.querySelectorAll(".wysiwyg-toolbar-dropdown-content button").forEach(button => {
            button.addEventListener('click', () => {
                button.parentElement.previousElementSibling.querySelector('span').innerText = button.innerText;
                button.parentElement.classList.remove('show');
            });
        });

        // Custom dropdowns
        const createLinkInput = this.#toolbar.querySelector('input[data-command="createLink"]');
        if(createLinkInput) this.#createLinkInput(createLinkInput);
        
        const uploadImageInput = this.#toolbar.querySelector('input[data-command="uploadImage"]');
        if(uploadImageInput) this.#createUploadImageInput(uploadImageInput);
    }

    /**
     * @private
     * @description Create the body layout and append it to the editor
     * @returns {void}
     */
    #createBody(){
        if(this.#displayMode == DisplayMode.POPOVER || this.#displayMode == DisplayMode.TOOLTIP)
            this.#createDynamicBody();    
        else
            this.#createFixedBody();

        // Remove whitespaces
        this.#removeEmptyNodes(this.#body);

        // Add events to the body
        this.#addBodyEvents();
    }

    /**
     * @private
     * @description Makes body suitable for fixed toolbar.
     * @returns {void}
     */
    #createFixedBody(){
        const body = this.#editor.querySelector('.wysiwyg-body');
        this.#body = body;
        if(!this.#body){
            this.#body = document.createElement('div');
            this.#body.classList.add('wysiwyg-body');
            this.#editor.appendChild(this.#body);
        }
        this.#body.setAttribute('contenteditable', true);
        this.#body.innerHTML = this.#body.innerHTML.replace(/\s+/g, ' ').trim();
    }

    /**
     * @private
     * @description Makes body suitable for dynamic(tooltip or popover) 
     * toolbar.
     * @returns {void}
     */
    #createDynamicBody(){
        const body = this.#editor.querySelector('.wysiwyg-body');
        if(body) this.#editor.removeChild(body);
        this.#body = this.#editor;
        if(body) this.#body.innerHTML = body.innerHTML.trim();
        this.#body.classList.add('wysiwyg-body');
        this.#body.setAttribute('contenteditable', true);  
    }

    /**
     * @private
     * @description Update the toolbar button state when the selection changes
     * @returns {void}
     */
    #makeToolbarReactiveToSelection(){
        document.addEventListener('selectionchange', (event) => {
            if(this.#body !== document.activeElement) return;
            this.#toolbarButtons.forEach(button => {
                button.classList.toggle('active', document.queryCommandState(button.dataset.command));
            });

            // If the selection is empty, hide the toolbar
            if(
                this.#displayMode == DisplayMode.TOOLTIP 
                && !this.#toolbar.contains(event.target) 
                && (document.getSelection().toString() === '' || document.getSelection().rangeCount === 0)
            )
                this.#toolbar.style.display = 'none';
        });
    }

    /**
     * @private
     * @description Hide the toolbar when the body is blurred(if toolbar isn't fixed)
     * @returns {void}
     */
    #hideToolbarOnBlur(){
        this.#body.addEventListener('blur', () => {
            document.addEventListener('click', (event) => {
                if (!this.#body.contains(event.target) && !this.#toolbar.contains(event.target))
                    this.#toolbar.style.display = 'none';
            });
        });
    }
    
    /**
     * @private
     * @description Show the toolbar when the body is focused
     */
    #showToolbarOnFocus(){
        this.#body.addEventListener('focus', () => {
            this.#toolbar.style.display = 'block';
            this.#toolbar.style.top = `${this.#body.offsetTop - this.#toolbar.offsetHeight}px`;
            this.#toolbar.style.left = `${this.#body.offsetLeft}px`;
        });
    }

    /**
     * @private
     * @description Show the toolbar when selecting text
     * @returns {void}
     */
    #showToolbarOnSelection(){
        this.#body.addEventListener('mouseup', () => {
            const selection = document.getSelection();
            if (selection.toString() !== '' && selection.rangeCount > 0) {
                this.#toolbar.style.display = 'block';
                const selectionRect = selection.getRangeAt(0).getBoundingClientRect();
                this.#toolbar.style.top = `${selectionRect.top + window.scrollY - this.#toolbar.offsetHeight}px`;
                this.#toolbar.style.left = `${selectionRect.left + window.scrollX}px`;
            }
        });
    }

    /**
     * @private
     * @description Insert the link when user paste the URL over the selected text
     * @returns {void}
     */
    #insertLinkOnPasteEvent(){
        this.#body.addEventListener('paste', (event) => {
            const url = (event.clipboardData).getData('text');
            if (url.match(/^https?:\/\/.+/)){
                document.execCommand('createLink', false, url);
                event.preventDefault(); // Prevent pasting the URL as text
                this.#body.querySelectorAll('a').forEach(link => {
                    link.target = '_blank';
                    link.title = link.href;
                    link.innerHTML = link.querySelector('span')?.innerHTML || link.innerHTML;
                    link.addEventListener('click', (e) => { if(e.ctrlKey) window.open(link.href, '_blank') });
                    link.addEventListener('mouseover', () => { 
                        document.addEventListener('keydown', (e) => { if(e.ctrlKey) link.style.cursor = 'pointer' });
                        document.addEventListener('keyup', () => { link.style.cursor = 'text' });
                    });
                    link.addEventListener('mouseout', () => { link.style.cursor = 'text' });
                });
            }
        });
    }

    /**
     * @private
     * @description Add necessary events to the body
     * @returns {void}
     */
    #addBodyEvents(){
        this.#makeToolbarReactiveToSelection();

        if(this.#displayMode != DisplayMode.FIXED)
            this.#hideToolbarOnBlur();
        
        if(this.#displayMode == DisplayMode.POPOVER)
           this.#showToolbarOnFocus();
        
        if(this.#displayMode == DisplayMode.TOOLTIP)
            this.#showToolbarOnSelection();
        
        // Events for the body.
        this.#insertLinkOnPasteEvent();
    }
    
    /**
     * @private
     * @description Remove empty nodes from the given node and 
     * its children
     * @param {HTMLElement} node
     * @returns {void}
     */
    #removeEmptyNodes(node) {
        for (let i = 0; i < node.childNodes.length; i++) {
            if (node.childNodes[i].nodeType === 3 && node.childNodes[i].nodeValue.trim() === '')
                node.removeChild(node.childNodes[i]);
            else if (node.childNodes[i].nodeType === 1)
                this.#removeEmptyNodes(node.childNodes[i]);
        }
    }

    /**
     * @description Get the content of the body's innerText
     * @returns {string}
     */
    getTextContent(){
        return this.#body.innerText;
    }

    /**
     * @description Get the content of the body's innerHTML
     * @returns {string}
     */
    getHTMLContent(){
        const iframeContent = this.#body.querySelector('iframe')?.contentWindow.document.body.outerHTML;
        return this.#body.innerHTML.replace("<iframe>", "").replace("</iframe>", "") + (iframeContent ? "<iframe>" + iframeContent + "</iframe>" : "");
    }

    /**
     * @description Add content to the body
     * @param {string} text The content to be added
     * @example editor.addContent('<p>Hello World</p>');
     * @example editor.addContent('Hello World');
     * @returns {void}
     */
    addHTMLContent(text){
        this.#body.innerHTML += text;
    }

    /**
     * @description Add text content to the body
     * @param {string} text The text content to be added
     * @example editor.addTextContent('Hello World');
     * @returns {void}
     */
    addTextContent(text){
        this.#body.innerText += text;
    }

    /**
     * @description Set the content of the body(override the existing content)
     * @param {string} text The content to be set
     * @example editor.setContent('<p>Hello World</p>');
     * @example editor.setContent('Hello World');
     * @returns {void}
     */
    setHTMLContent(text){
        this.#body.innerHTML = text;
    }

    /**
     * @description Set the text content of the body(override the existing content)
     * @param {string} text The text content to be set
     * @example editor.setTextContent('Hello World');
     * @returns {void}
     */
    setTextContent(text){
        this.#body.innerText = text;
    }

    /**
     * @description Add full HTML content to the body(does not override the existing content)
     * @param {string} html The full HTML content to be added
     * @example editor.addFullHTML('<html><body><p>Hello World</p></body></html>');
     * @returns {void}
     */
    addFullHTMLPage(html){
        let iframe = document.createElement('iframe');
        this.#body.appendChild(document.createElement('br'));
        this.#body.appendChild(iframe);
        iframe = iframe.contentWindow ? iframe.contentWindow.document : iframe.document;
        iframe.open();
        iframe.writeln(html);
        iframe.close();
        iframe.querySelector('body').setAttribute('contenteditable', true);
    }

    /**
     * @description Clear the content of the body
     * @returns {void}
     */
    clearContent(){
        this.#body.innerHTML = '';
    }
    
    /**
     * @description Run a function when the content changes
     * @param {function} callback The function to be called when the content changes
     * @example editor.onChange((content) => { console.log(content) });
     * @returns {void}
     */
    onChange(callback){
        const observer = new MutationObserver(() => {
            callback(this.getHTMLContent());
        });

        observer.observe(this.#body, {
            childList: true,
            subtree: true,
            characterData: true
        });

        this.#toolbarButtons.forEach(button => {
            button.addEventListener('click', () => {
                callback(this.getHTMLContent());
            });
        });
    }
}
    