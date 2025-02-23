<script lang="ts">
    interface Props {
        text?: string;
    }

    let {
        text = "Loading"
    }: Props = $props();
</script>

<span>
    <small class="loader"></small> {text}
</span>

<style>
    .loader {
        border: 2px solid #2a2a2a;
        border-radius: 50%;
        border-top: 2px solid #fff;
        width: 10px;
        height: 10px;
        -webkit-animation: spin 2s linear infinite;
        animation: spin 2s linear infinite;
        display: inline-block;
        margin-right: 5px;
    }

    @-webkit-keyframes spin {
        0% { -webkit-transform: rotate(0deg); }
        100% { -webkit-transform: rotate(360deg); }
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
