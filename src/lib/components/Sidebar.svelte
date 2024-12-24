<script lang="ts">
    import { onMount } from 'svelte';
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder } from '$lib/types';

    onMount(() => {
    });
</script>

<div class = "card">
    <div style="border-bottom:1px solid dimgrey;">
        <h3>Open Mail</h3>
    </div>
    <div>
        <div>
            <button class = "bg-primary" style="width:100%;padding:7x;margin:10px 0;">New Message +</button>
        </div>
        <div style="border-bottom:1px solid dimgrey;">
            {#each Object.values(Folder) as folder}
                <div class="folder">
                    <button class = "inline" style="flex-grow:1;">{folder}</button>
                </div>
            {/each}
        </div>
    </div>
    <div style="margin-top:20px;">
        <div style="border-bottom:1px solid dimgrey;display:flex;align-items:center;justify-content:space-between;padding:10px 0;">
            <span>Folders ▾</span>
            <button class = "bg-primary">+</button>
        </div>
        {#each SharedStore.folders[0].result as folder}
            <div class="folder">
                <button class="inline">▸</button>
                <button class="inline" style="flex-grow:1;">{folder}</button>
                <button class="inline hover">⋮</button>
            </div>
        {/each}
    </div>
</div>

<style>
    .folder{
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        border-radius: 0;
        background-color: rgb(36, 36, 36);
        border-bottom: 1px solid rgb(70, 70, 70);

        & button{
            text-align: left;
            padding:7px 8px;

            &:hover{
                background-color: rgb(50, 50, 50);
            }

            &:active{
                background-color: rgb(70, 70, 70);

                &.hover{
                    background-color: rgb(70, 70, 70);
                }
            }

            &.hover{
                padding-left:8px;
                padding-right:8px;
                margin-right: 5px;

                &:hover{
                    background-color: #727272;
                }

                &:active{
                    background-color: #868686;
                }
            }
        }

        &:hover{
            background-color: rgb(50, 50, 50);

            & .hover{
                opacity: 1;
            }
        }

        & .hover{
            opacity: 0;
            transition: opacity 0.1s ease-in-out;
        }

        &:last-child{
            border-bottom: none;
        }
    }
</style>
