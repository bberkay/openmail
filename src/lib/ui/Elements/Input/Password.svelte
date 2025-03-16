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

    const togglePassword = (e: Event) => {
        const input = e.target as HTMLInputElement;
        const eyeOpen = input.closest("input-group")!
            .querySelector('[name="eye-open"]') as HTMLElement;
        const eyeClosed = input.closest("input-group")!
            .querySelector('[name="eye-closed"]') as HTMLElement;
        if (input.getAttribute("type") == "text") {
            input.setAttribute("type", "password");
            eyeOpen.classList.remove("hidden");
            eyeClosed.classList.add("hidden");
        } else {
            input.setAttribute("type", "text");
            eyeOpen.classList.add("hidden");
            eyeClosed.classList.remove("hidden");
        }
    }
</script>

<Input.Group>
    <Icon name="search" />
    <Input.Basic
        {...attributes}
        type="password"
        onclick={togglePassword}
        {name}
        {id}
        {placeholder}
        {autocomplete}
        {required}
    />
    <Icon name="eye-open" />
    <Icon name="eye-closed" class="hidden" />
</Input.Group>
