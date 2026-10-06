// ===============================
// SAFEHER AI - ASSISTANT
// ===============================

function addMessage(message, sender) {

    const chatBox = document.getElementById("chatBox");

    if (!chatBox) return;

    const messageDiv = document.createElement("div");

    messageDiv.className =
        sender === "user"
            ? "message user-message"
            : "message bot-message";

    messageDiv.textContent = message;

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}


function sendMessage() {

    const input = document.getElementById("messageInput");

    if (!input) return;

    const message = input.value.trim();

    if (!message) return;

    addMessage(message, "user");

    input.value = "";

    const lowerMessage = message.toLowerCase();

    let reply =
        "I'm here to help. You can use SOS, Safety Timer, Trusted Contacts, Live Location, or Nearby Help.";

    if (
        lowerMessage.includes("sos") ||
        lowerMessage.includes("emergency") ||
        lowerMessage.includes("danger")
    ) {
        reply =
            "If you are in immediate danger, use the SOS button. Your trusted contacts can receive your emergency alert and location.";
    }

    else if (
        lowerMessage.includes("timer") ||
        lowerMessage.includes("safe timer")
    ) {
        reply =
            "Safety Timer lets you set a countdown. Check in before it expires. If it expires without a check-in, an alert can be sent to your trusted contacts.";
    }

    else if (
        lowerMessage.includes("contact") ||
        lowerMessage.includes("trusted")
    ) {
        reply =
            "Open Trusted Contacts to add or manage the people who should receive your emergency alerts.";
    }

    else if (
        lowerMessage.includes("location") ||
        lowerMessage.includes("where am i")
    ) {
        reply =
            "Live Location can use your device GPS to show your current location.";
    }

    else if (
        lowerMessage.includes("help") ||
        lowerMessage.includes("police")
    ) {
        reply =
            "Use Nearby Help to find useful emergency services and nearby assistance.";
    }

    else if (
        lowerMessage.includes("hello") ||
        lowerMessage.includes("hi")
    ) {
        reply =
            "Hello! I'm SafeHer Assistant. How can I help you?";
    }

    setTimeout(function () {
        addMessage(reply, "bot");
    }, 500);
}


function sendQuickMessage(message) {

    const input = document.getElementById("messageInput");

    if (!input) return;

    input.value = message;

    sendMessage();
}


document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("messageInput");

    if (input) {
        input.addEventListener("keydown", function (event) {

            if (event.key === "Enter") {
                event.preventDefault();
                sendMessage();
            }

        });
    }

});