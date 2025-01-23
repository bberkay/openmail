<script lang="ts">
    interface Props {
        text: string;
    }

    let {
        text = "Loading"
    }: Props = $props();
</script>

<span>
    <small class="loader"></small> {text}
</span>
