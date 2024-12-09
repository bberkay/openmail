<script lang="ts">
    import { fly } from 'svelte/transition';

    let { message, type } = $props();
    let show: boolean = $state(true);
</script>

{#if show}
    <div class = "alert alert--{type}" transition:fly={{y: 200, duration: 500}}>
        <span id="alert-message">{message}</span>
        <button id="alert-close" onclick={() => (show = false)}>X</button>
    </div>
{/if}

<style>
    .alert{
        padding: 10px;
        margin: 10px;
        border-radius: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: absolute;
        top: 2.5rem;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 350px;
        z-index: 1000;
        box-shadow: 0 0 10px #000000;

        & button{
            cursor: pointer;
            padding-left: 7px;
            padding-right: 7px;
        }

        & span{
            margin-top: 5px;
        }
    }

    .alert--danger{
        background-color: #922626;
        color: #f5f5f5;
    }

    .alert--success{
        background-color: #3c865b;
        color: #f5f5f5;
    }
</style>
