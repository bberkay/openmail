<script lang="ts">
    import { onMount } from "svelte";
    import { makeSizeHumanReadable, combine } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    interface Props {
        [attribute: string]: unknown;
    }

    let { ...attributes }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let files: FileList | null | undefined = $state();
    let fileUploaderWrapper: HTMLElement;
    let fileInput: HTMLInputElement;
    let dropArea: HTMLElement;

    // Event listeners
    onMount(() => {
        fileInput = fileUploaderWrapper.querySelector(".file-input") as HTMLInputElement;

        ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
            dropArea.addEventListener(eventName, (e: Event) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ["dragenter", "dragover"].forEach((eventName) => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.add("dragging")
            }, false);
        });

        ["dragleave", "drop"].forEach((eventName) => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.remove("dragging")
            }, false);
        });

        // Dropping
        dropArea.addEventListener("drop", addFile, false);
    });

    const addFile = (e: InputEvent | DragEvent) => {
        e.preventDefault();
        const targetFiles = (e.target as HTMLElement).tagName == "INPUT"
            ? (e.target as HTMLInputElement).files
            : (e as DragEvent).dataTransfer!.files;
        const dt = new DataTransfer();
		[...(targetFiles ?? []), ...(files ?? [])].forEach(file => dt.items.add(file));
        files = dt.files;
        fileInput.files = files;
    }

    const removeFile = (index: number) => {
        const dt = new DataTransfer();
        Array.from(files ?? []).forEach((file, i) => i !== index && dt.items.add(file));
        files = dt.files;
        fileInput.files = files;
    };
</script>

<div
    bind:this={fileUploaderWrapper}
    class={combine("file-uploader-container", additionalClass)}
    {...restAttributes}
>
    <div class="file-upload-area">
        <label class="upload-btn">
            {local.upload_file[DEFAULT_LANGUAGE]}
            <Input.Basic
                type="file"
                class="file-input"
            />
        </label>
        <div
            class="file-drop-area"
            bind:this={dropArea}
            onclick={() => fileInput.click()}
            onkeydown={() => fileInput.click()}
            role="button"
            tabindex="0"
        >
            <span class="file-msg">{local.drop_files_here[DEFAULT_LANGUAGE]}</span>
        </div>
    </div>
    <div class="file-list">
        {#if files}
            {#each Array.from(files) as file, index}
                <div class="file-item">
                    <div class="file-name">{file.name}</div>
                    <div class="file-size">
                        {makeSizeHumanReadable(file.size)}
                    </div>
                    <Button.Basic
                        type="button"
                        class="btn-inline"
                        onclick={() => removeFile(index)}
                    >
                        {local.remove[DEFAULT_LANGUAGE]}
                    </Button.Basic>
                </div>
            {/each}
        {/if}
    </div>
</div>

<style>
    :global {
        .file-upload-container {
            max-width: var(--container-md);

            & .file-upload-area {
                display: flex;
                align-items: center;
                width: 100%;
            }

            & .upload-btn {
                display: inline-block;
                flex-shrink: 0;

                & .file-input {
                    display: none;
                }
            }

            & .file-drop-area {
                border: 1px dashed var(--color-border);
                border-radius: var(--radius-sm);
                border-top-left-radius: 0;
                border-bottom-left-radius: 0;
                background-color: var(--color-border-subtle);
                color: var(--color-text-secondary);
                font-size: var(--font-size-sm);
                padding: var(--spacing-xs) var(--spacing-md);
                cursor: pointer;
                transition:
                    background-color var(--transition-normal),
                    border-color var(--transition-normal);
                flex-grow: 1;
                display: flex;
                align-items: center;

                &.dragging {
                    border-color: var(--color-border-drop-area);
                    background-color: var(--color-bg-drop-area);
                }
            }

            & .file-list {
                margin-top: var(--spacing-md);
                gap: var(--spacing-xs);

                & .file-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: var(--spacing-xs) var(--spacing-sm);
                    border-radius: var(--radius-sm);
                    font-size: var(--font-size-xs);

                    & .file-name {
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        flex: 1;
                        margin-right: var(--spacing-xs);
                        margin-top: calc(var(--font-size-xs) / 4);
                    }

                    & .file-size {
                        color: var(--color-text-secondary);
                        margin-right: 15px;
                        margin-top: calc(var(--font-size-xs) / 4);
                    }
                }
            }
        }
    }
</style>
