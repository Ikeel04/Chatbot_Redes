const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const chatWindow = document.getElementById("chat-window");

const sessionId = crypto.randomUUID();

function appendMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = `bubble ${sender}`;
    bubble.textContent = text;
    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, "usuario");
    input.value = "";

    // TODO: manejar estado de "escribiendo..." mientras responde el backend
    const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message }),
    });
    const data = await res.json();
    appendMessage(data.response, "bot");
});
