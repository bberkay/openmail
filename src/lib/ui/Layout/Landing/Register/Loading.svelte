<script lang="ts">
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { Spinner } from "$lib/ui/Components/Loader";
</script>

<h3>
    <Spinner/>
    {local.connecting_to_accounts[DEFAULT_LANGUAGE]}
</h3>
