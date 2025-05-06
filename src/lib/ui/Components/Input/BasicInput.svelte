<script lang="ts">
    import { combine } from "$lib/utils";

    interface Props {
        group?: string[] | undefined;
        value?: string;
        element?: HTMLInputElement;
        [attribute: string]: unknown;
    }

    let {
        group = $bindable(undefined),
        value = $bindable(undefined),
        element = $bindable(undefined),
        ...attributes
    }: Props  = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    const handleChange = ({ target }: any) => {
        /* Related issue about bind:group
        with nested components: github.com/sveltejs/svelte/issues/2308 */
        if (!group) return;
		const { value, checked } = target;
		if (checked) group.push(value);
		else group = group.filter(v => v !== value);
	}
</script>

{#if restAttributes["type"] === "checkbox"}
    <!-- input type will be (mostly) "checkbox" -->
    <input
        bind:this={element}
        {value}
        checked={group?.includes(value as string)}
        onchange={handleChange}
        class={combine("input", additionalClass)}
        {...restAttributes}
    />
{:else}
    <input
        bind:this={element}
        bind:value
        class={combine("input", additionalClass)}
        {...restAttributes}
    />
{/if}

<style>
    :global{
        .input{
            width: 100%;
            padding: var(--spacing-sm) var(--spacing-2xs);
            border: none;
            border-bottom: 1px solid var(--color-border);
            background-color: transparent;
            color: var(--color-text-primary);
            transition: all var(--transition-fast) var(--ease-default);

            &:focus {
                outline: none;
                border-color: var(--color-text-primary);
            }

            &[type="email"] {
                will-change: transform;
            }

            &[type="checkbox"] {
                padding: 0;
                appearance: none;
                -webkit-appearance: none;
                width: var(--font-size-md);
                height: var(--font-size-md);
                border-radius: var(--radius-sm);
                background-color: transparent;
                border: 1px solid var(--color-border);
                cursor: pointer;
                position: relative;

                &:checked {
                    background-color: var(--color-text-primary);

                    &::after {
                        content: "";
                        position: absolute;
                        top: calc(var(--font-size-md) / 8);
                        left: calc(var(--font-size-md) / 3);
                        width: calc(var(--font-size-md) / 5);
                        height: calc(var(--font-size-md) / 2);
                        border: solid var(--color-bg-primary);
                        border-width: 0 calc(var(--font-size-md) / 8) calc(var(--font-size-md) / 8) 0;
                        transform: rotate(45deg);
                    }
                }
            }
        }

        .input + .muted{
            margin-left: calc(var(--spacing-2xs) / 2);
            margin-top: var(--spacing-xs);
        }
    }
</style>
