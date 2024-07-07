<script lang="ts">
    export let email: { 
        from: string, 
        date: string, 
        to: string, 
        subject: string, 
        body: string, 
        flags: string 
    } = { 
        from: "someone@mail.com",
        date: "2021-09-01",
        to: "me@mail.com",
        subject: "Most Important Email",
        body: "Lorem ipsum dolor sit amet consectetur adipisicing elit. Illo, illum. Odio beatae, aperiam cupiditate", 
        flags: "Seen" 
    };
</script>

<section class="card">
    <div class="email-header">
        <h2>Email</h2>
        <hr>
        <div class="email-operations">
            <div class="flag-operations">
                <button>Read</button>
                <button>Star</button>
                <select>
                    <option value="">Move To Folder</option>
                </select>
                <button>Delete</button>
            </div>
            <div class="answer-operations">
                <button>Reply</button>
                <button>Forward</button>
            </div>
        </div>
    </div>
    <hr>
    <div class="email-content">
        <div class="tags">
            <!-- Flags -->
        </div>
        <div id="subject">
            <h3>{email.subject}</h3>
            <p>From: {email.from}</p>
            <p>To: {email.to}</p>
            <p>Date: {email.date}</p>
        </div>
        <div id="body">
            <p>{email.body}</p>
        </div>
        <div id="attachments">
            
        </div>
    </div>
</section>

<style>
    .email-operations{
        display: flex;
        justify-content:space-between;
        align-items: center;

        & .flag-operations, & .answer-operations{
            display: flex;
            align-items: center;
        }
    }

    .email-content{
        & .tags {
            & button{
                display: none;
            }
        }
    }
</style>