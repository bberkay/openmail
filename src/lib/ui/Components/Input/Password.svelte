<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import Icon from "$lib/ui/Components/Icon";

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
        const inputGroup = (e.target as HTMLInputElement).closest(".input-group")!;
        const input = inputGroup.querySelector("input") as HTMLInputElement;
        const eyeOpen = input.querySelector('[name="eye-open"]') as HTMLElement;
        const eyeClosed = input.querySelector('[name="eye-closed"]') as HTMLElement;
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
    <Input.Basic
        {...attributes}
        type="password"
        {name}
        {id}
        {placeholder}
        {autocomplete}
        {required}
    />
    <Button.Basic
        type="button"
        onclick={togglePassword}
    >
        <Icon name="eye-open" />
        <Icon name="eye-closed" class="hidden" />
    </Button.Basic>
</Input.Group>
