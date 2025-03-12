<script lang="ts">
    import * as Input from "$lib/ui/Elements/Input";
    import Icon from "$lib/ui/Elements/Icon";

    interface Props {
        name?: string;
        id?: string;
        placeholder?: string;
        autocomplete?: string;
        required?: boolean;
        [attribute: string]: unknown;
    }

    let {
        name = "password",
        id = "password",
        placeholder = "Password",
        autocomplete="new-password",
        required=true,
        ...attributes
    }: Props  = $props();
</script>

<Input.WithButton
    {...attributes}
    type="password"
    {name}
    {id}
    {placeholder}
    {autocomplete}
    {required}
>
    <Icon name="eye-icon" class="open" />
    <Icon name="eye-closed" class="closed" />
</Input.WithButton>
