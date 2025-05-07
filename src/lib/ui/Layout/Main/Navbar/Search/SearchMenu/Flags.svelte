<script lang="ts">
    import * as Select from "$lib/ui/Components/Select";
    import Label from "$lib/ui/Components/Label";
    import Badge from "$lib/ui/Components/Badge";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { Mark, type SearchCriteria } from "$lib/types";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";

    interface Props {
        searchCriteria: SearchCriteria
    }

    let {
        searchCriteria = $bindable()
    }: Props = $props();

    const addIncludedFlag = (flag: string) => {
        if (!searchCriteria.included_flags) searchCriteria.included_flags = [];
        if (searchCriteria.excluded_flags?.includes(flag))
            searchCriteria.excluded_flags =
                searchCriteria.excluded_flags.filter(
                    (excluded_flag) => excluded_flag !== flag,
                );
        searchCriteria.included_flags.push(flag);
    };

    const addExcludedFlag = (flag: string) => {
        if (!searchCriteria.excluded_flags) searchCriteria.excluded_flags = [];
        if (searchCriteria.included_flags?.includes(flag))
            searchCriteria.included_flags =
                searchCriteria.included_flags.filter(
                    (included_flag) => included_flag !== flag,
                );
        searchCriteria.excluded_flags.push(flag);
    };
</script>

<FormGroup>
    <Label>{local.flags[DEFAULT_LANGUAGE]}</Label>
    <FormGroup direction="horizontal">
        <FormGroup class="flag-group">
            <FormGroup>
                <Label for="included-flags">{local.included_flags[DEFAULT_LANGUAGE]}</Label>
                <Select.Root
                    id="included-flags"
                    class="flag-select"
                    onchange={addIncludedFlag}
                    resetAfterSelect={true}
                    placeholder="Flag"
                >
                    {#each Object.entries(Mark) as mark}
                        <Select.Option value={mark[1]} content={mark[0]} />
                    {/each}
                </Select.Root>
            </FormGroup>
            <div class="tags">
                {#if searchCriteria.included_flags}
                    {#each searchCriteria.included_flags as included_flag}
                        <Badge
                            content={included_flag}
                            righticon="close"
                            onclick={() => {
                                searchCriteria.included_flags =
                                    searchCriteria.included_flags!.filter(
                                        (flag) => flag !== included_flag,
                                    );
                            }}
                        />
                    {/each}
                {/if}
            </div>
        </FormGroup>
        <FormGroup class="flag-group">
            <FormGroup>
                <Label for="excluded-flags">{local.excluded_flags[DEFAULT_LANGUAGE]}</Label>
                <Select.Root
                    id="excluded-flags"
                    class="flag-select"
                    onchange={addExcludedFlag}
                    resetAfterSelect={true}
                    placeholder="Flag"
                >
                    {#each Object.entries(Mark) as mark}
                        <Select.Option value={mark[1]} content={mark[0]} />
                    {/each}
                </Select.Root>
            </FormGroup>
            <div class="tags">
                {#if searchCriteria.excluded_flags}
                    {#each searchCriteria.excluded_flags as excluded_flag}
                        <Badge
                            content={excluded_flag}
                            righticon="close"
                            onclick={() => {
                                searchCriteria.excluded_flags =
                                    searchCriteria.excluded_flags!.filter(
                                        (flag) => flag !== excluded_flag,
                                    );
                            }}
                        />
                    {/each}
                {/if}
            </div>
        </FormGroup>
    </FormGroup>
</FormGroup>

<style>
    :global {
        .search-menu{
            & .flag-group {
                width: 100%;

                & label + .form-group-horizontal {
                    gap: var(--spacing-md);
                }

                & .flag-select {
                    width: 100%;

                    & .options-container {
                        height: 150px;
                    }
                }
            }
        }
    }
</style>
