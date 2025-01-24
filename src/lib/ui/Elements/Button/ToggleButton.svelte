<script lang="ts">
    interface Props {
        opened: boolean;
        onclick?: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        [attribute: string]: unknown;
    }

    let {
        opened,
        onclick = undefined,
        ...attributes
    }: Props = $props();

    const OPENED_CONTENT = "▾";
    const CLOSED_CONTENT = "▸";

    let status = $state(opened);
    let content = $derived(status ? OPENED_CONTENT : CLOSED_CONTENT);

    const toggle = async (e: Event): Promise<void> => {
        const btn = e.target as HTMLButtonElement;
        status = !status;
        btn.classList.toggle("opened", status);

        if (onclick)
            await onclick(e);
    }
</script>

<button {...attributes} type="button" onclick={toggle}>{content}</button>
