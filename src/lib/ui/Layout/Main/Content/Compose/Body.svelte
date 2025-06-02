<script lang="ts">
    import { local } from "$lib/locales";
    import {
        DEFAULT_LANGUAGE,
    } from "$lib/constants";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { onDestroy, onMount } from "svelte";
    import { WYSIWYGEditor } from "@bberkay/wysiwygeditor";
    import { getReplyTemplate, getForwardTemplate } from "$lib/templates";
    import {
        escapeHTML,
    } from "$lib/utils";
    import type { OriginalMessageContext } from "$lib/types";
    import { triggerDraftChange } from "../Compose.svelte";

    interface Props {
        editor?: WYSIWYGEditor;
        originalMessageContext?: OriginalMessageContext;
    }

    let {
        editor = $bindable(),
        originalMessageContext
    }: Props = $props();

    onMount(() => {
        editor = new WYSIWYGEditor("body");
        editor.init();
        editor.onChange = () => {
            triggerDraftChange();
        };

        if (originalMessageContext) {
            const getBodyTemplate =
                originalMessageContext.composeType == "reply"
                    ? getReplyTemplate
                    : getForwardTemplate;
            editor.addFullHTMLPage(
                getBodyTemplate(
                    escapeHTML(originalMessageContext.sender || ""),
                    escapeHTML(originalMessageContext.receivers || ""),
                    originalMessageContext.subject || "",
                    originalMessageContext.body || "",
                    originalMessageContext.date || "",
                ),
            );
        }
    });

    onDestroy(() => {
        if (editor) editor.clear();
    })
</script>

<FormGroup>
    <Label for="body">{local.body[DEFAULT_LANGUAGE]}</Label>
    <div id="body"></div>
</FormGroup>

<style>
    :global {
        .compose {
            #body {
                margin-top: var(--spacing-xs);
            }
        }
    }
</style>
