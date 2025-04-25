<script lang="ts">
    import { combine } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import { getRangePaginationTemplate } from "$lib/templates";

    interface Props {
        total: number;
        onChange: (((selectedPage: number) => void) | ((selectedPage: number) => Promise<void>));
        range: number;
        startAt?: number;
        [attribute: string]: unknown;
    }

    let {
        total,
        onChange,
        range,
        startAt = 1,
        ...attributes
    }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let current = $state(Math.max(1, startAt));

    const prev = async () => {
        await onChange(current - range);
        current -= range;
    };

    const next = async () => {
        await onChange(current + range);
        current += range;
    };
</script>

<div
    class={combine("pagination", additionalClass)}
    {...restAttributes}
>
    <Button.Action
        type="button"
        class="btn-inline"
        disabled={current <= range}
        onclick={prev}
    >
        <Icon name="prev" />
    </Button.Action>
    <small>
        {getRangePaginationTemplate(
            current.toString(),
            (current - 1 + range).toString(),
            total.toString(),
        )}
    </small>
    <Button.Action
        type="button"
        class="btn-inline"
        disabled={current >= total}
        onclick={next}
    >
        <Icon name="next" />
    </Button.Action>
</div>

<style>
    :global {
        .pagination {
            display: flex;
            flex-direction: row;
            gap: var(--spacing-2xs);
            align-items: end;
            justify-content: center;
        }
    }
</style>
