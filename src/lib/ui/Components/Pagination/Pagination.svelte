<script lang="ts">
    import { range, combine } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";

    interface Props {
        total: number;
        onChange: (((selectedPage: number) => void) | ((selectedPage: number) => Promise<void>));
        startAt?: number;
        showMax?: number;
        [attribute: string]: unknown;
    }

    let {
        total,
        onChange,
        startAt = 1,
        showMax = 5,
        ...attributes
    }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let current = $state(Math.max(1, startAt));
    let pages = $derived.by(() => {
        if (total < showMax)
            return range(1, total + 1, 1);

        const middle = Math.floor(showMax / 2)
        const rangeStart = Math.max(
            1,
            Math.min(total - showMax + 1, current - middle),
        );
        const rangeEnd = Math.min(total, current + middle + 1);
        if (rangeEnd - rangeStart < showMax) {
            return range(
                  rangeStart,
                  rangeEnd + showMax - (rangeEnd - rangeStart),
                  1,
              )
        } else {
            return range(rangeStart, rangeEnd, 1)
        }
    });

    const onChangeWrapper = async (e: Event) => {
        const target = e.target as HTMLElement;
        const value = Number(target.getAttribute("data-value"));
        await onChange(value);
        current = value;
    };

    const prev = async () => {
        await onChange(current - 1);
        current -= 1;
    };

    const next = async () => {
        await onChange(current + 1);
        current += 1;
    };

    const prevAll = async () => {
        await onChange(1);
        current = 1;
    };

    const nextAll = async () => {
        await onChange(total);
        current = total;
    };
</script>

<div
    class={combine("pagination", additionalClass)}
    {...restAttributes}
>
    <Button.Basic
        class="btn-outline btn-sm arrow-button"
        onclick={prev}
        disabled={current <= 1}
    >
        <Icon name="prev" />
    </Button.Basic>
    {#if pages[0] > 1}
        <Button.Basic
            class="btn-outline btn-sm"
            onclick={prevAll}
        >
            {1}
        </Button.Basic>
        {#if pages[0] > 2}
            <span>...</span>
        {/if}
    {/if}
    {#each pages as value}
        <Button.Basic
            class="btn-outline btn-sm"
            onclick={onChangeWrapper}
            data-value={value}
        >
            {value}
        </Button.Basic>
    {/each}
    {#if pages[pages.length - 1] < total}
        {#if pages[pages.length - 1] < total - 1}
            <span>...</span>
        {/if}
        <Button.Basic
            class="btn-outline btn-sm"
            onclick={nextAll}
        >
            {total}
        </Button.Basic>
    {/if}
    <Button.Basic
        class="btn-outline btn-sm arrow-button"
        onclick={next}
        disabled={current >= total}
    >
        <Icon name="next" />
    </Button.Basic>
</div>

<style>
    :global {
        .pagination {
            display: flex;
            flex-direction: row;
            gap: var(--spacing-2xs);
            align-items: end;
            justify-content: center;

            & .arrow-button {
                padding: var(--spacing-xs) var(--spacing-2xs);
            }
        }
    }
</style>
