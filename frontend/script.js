async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    const message = input.value.trim();
    if (!message) return;

    // Show user message
    addMessage("You", message, "user");
    input.value = "";

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // IMPORTANT: markdown is parsed here
        addMessage("Assistant", data.reply, "bot");

    } catch (error) {
        addMessage("Assistant", "❌ Unable to connect to server.", "bot");
    }
}

function addMessage(sender, text, className) {
    const chatBox = document.getElementById("chat-box");

    const msgDiv = document.createElement("div");
    msgDiv.className = "message";

    // Parse markdown ONLY for bot
    if (className === "bot") {
        msgDiv.innerHTML = `
            <span class="${className}">${sender}:</span>
            <div class="markdown">${marked.parse(text)}</div>
        `;
    } else {
        msgDiv.innerHTML = `
            <span class="${className}">${sender}:</span>
            ${text}
        `;
    }

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

