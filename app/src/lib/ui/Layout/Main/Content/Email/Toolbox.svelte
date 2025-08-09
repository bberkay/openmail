<script lang="ts">
    import { type Account, type Email } from "$lib/types";
    import Operations from "$lib/ui/Layout/Main/Content/Email/Toolbox/Operations.svelte";
    import Pagination from "$lib/ui/Layout/Main/Content/Email/Toolbox/Pagination.svelte";

    interface Props {
        account: Account;
        email: Email;
        currentOffset: number;
    }

    let {
        account,
        email = $bindable(),
        currentOffset = $bindable()
    }: Props = $props();
</script>

<div class="toolbox">
    <Operations
        {account}
        {email}
        {currentOffset}
    />
    <Pagination
        {account}
        bind:email
        bind:currentOffset
    />
</div>
