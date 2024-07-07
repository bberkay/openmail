<script lang="ts">
    export let email: {
        from: string,
        date: string,
        to: string,
        subject: string,
        body: string,
        flags: string
    } = {
        from: "From",
        date: "03/03/2021",
        to: "someone@mail.com",
        subject: "Subject",
        body: "Body",
        flags: ""
    };
</script>

<div class="inbox-item" data-flags={email.flags}>
    <h3>{email.from}</h3>
    <small>
        <span>{email.date}</span> &lt;<span>{email.to}</span>&gt;
    </small>
    <br>
    <small>{email.subject}</small>
    <br>
    <small>{email.body}</small>
</div>

<style>
    .inbox-item{
        border: none;
        padding: 1rem 0.5rem;
        margin-bottom: 0.1rem;
        cursor: pointer;
        background-color: #414040;
        
        &[data-flags*="Seen"], &[data-flags*="seen"]{
           background-color: #2c2c2c;
        }
        
        &[data-flags*="Flagged"], &[data-flags*="flagged"]{
            background-color: #f8f3c7;
            color: #121212;

            &:hover{
                background-color: #f8f4d4;
            }
        }
        
        &:hover{
            filter: brightness(1.1);
        }

        &:active{
            filter: brightness(1);
        }
    }
</style>