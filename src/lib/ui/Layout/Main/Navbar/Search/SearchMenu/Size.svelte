<script lang="ts">
    import * as Input from "$lib/ui/Components/Input";
    import * as Select from "$lib/ui/Components/Select";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { Size, type SearchCriteria } from "$lib/types";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { adjustSizes, concatValueAndUnit, convertSizeToBytes } from "$lib/utils";
    import { onMount } from "svelte";

    interface Props {
        searchCriteria: SearchCriteria,
    }

    let {
        searchCriteria = $bindable()
    }: Props = $props();


    let largerThanInput: HTMLInputElement | undefined = $state();
    let smallerThanInput: HTMLInputElement | undefined = $state();
    let largerThanUnit: Size | undefined = $state();
    let smallerThanUnit: Size | undefined = $state();

    function updateSizes() {
        if (!largerThanInput || !smallerThanInput)
            return;

        if (smallerThanInput.value && smallerThanUnit) {
            searchCriteria.smaller_than = convertSizeToBytes(
                concatValueAndUnit(smallerThanInput.value, smallerThanUnit),
            );
        }
        if (largerThanInput.value && largerThanUnit) {
            searchCriteria.larger_than = convertSizeToBytes(
                concatValueAndUnit(largerThanInput.value, largerThanUnit),
            );
        }
    }

    const setLargerThanUnit = (selectedLargerThanUnit: string) => {
        largerThanUnit = selectedLargerThanUnit as Size;
        updateSizes();
    };

    const setSmallerThanUnit = (selectedSmallerThanUnit: string) => {
        smallerThanUnit = selectedSmallerThanUnit as Size;
        updateSizes();
    };

    const setEnteredSize = (e: Event): void => {
        if (!smallerThanUnit || !largerThanUnit
            || !largerThanInput || !smallerThanInput) return;

        const adjustedSizes = adjustSizes(
            [Number(smallerThanInput.value), smallerThanUnit],
            [Number(largerThanInput.value), largerThanUnit],
        );

        smallerThanInput.value = adjustedSizes[0][0].toString();
        smallerThanUnit = adjustedSizes[0][1] as Size;

        largerThanInput.value = adjustedSizes[1][0].toString();
        largerThanUnit = adjustedSizes[1][1] as Size;
        updateSizes();
    };
</script>

<FormGroup>
    <Label>{local.size[DEFAULT_LANGUAGE]}</Label>
    <FormGroup direction="horizontal">
        <FormGroup>
            <Label for="larger-than">{local.larger_than[DEFAULT_LANGUAGE]}</Label>
            <FormGroup direction="horizontal" class="size-group">
                <Input.Basic
                    bind:element={largerThanInput}
                    type="number"
                    id="larger-than"
                    placeholder={local.larger_than_placeholder[DEFAULT_LANGUAGE]}
                    onkeydown={setEnteredSize}
                />
                <Select.Root
                    placeholder={Size.KB}
                    value={largerThanUnit}
                    onchange={setLargerThanUnit}
                >
                    {#each Object.entries(Size) as size}
                        <Select.Option
                            value={size[0]}
                            content={size[1]}
                        />
                    {/each}
                </Select.Root>
            </FormGroup>
        </FormGroup>
        <FormGroup>
            <Label for="smaller-than">{local.smaller_than[DEFAULT_LANGUAGE]}</Label>
            <FormGroup direction="horizontal" class="size-group">
                <Input.Basic
                    bind:element={smallerThanInput}
                    type="number"
                    id="smaller-than"
                    placeholder={local.smaller_than_placeholder[DEFAULT_LANGUAGE]}
                    onkeydown={setEnteredSize}
                />
                <Select.Root
                    placeholder={Size.MB}
                    value={smallerThanUnit}
                    onchange={setSmallerThanUnit}
                >
                    {#each Object.entries(Size) as size}
                        <Select.Option
                            value={size[0]}
                            content={size[1]}
                        />
                    {/each}
                </Select.Root>
            </FormGroup>
        </FormGroup>
    </FormGroup>
</FormGroup>

<style>
    :global {
        .modal-like-body{
            & .size-group {
                align-items: end;
                font-size: var(--font-size-xs);
                gap: var(--spacing-sm);
            }
        }
    }
</style>
