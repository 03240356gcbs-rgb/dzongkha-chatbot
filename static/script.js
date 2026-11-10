
// ==========================================
// DZONGKHA AI CHATBOT - FRONTEND JAVASCRIPT
// ==========================================

// Conversation memory
let conversationHistory = [];

// Get HTML elements
const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

const newChatButton = document.getElementById("newChatButton");
const clearChatButton = document.getElementById("clearChatButton");

let isLoading = false;


// ==========================================
// DISPLAY A MESSAGE
// ==========================================

function displayMessage(text, sender) {

    const message = document.createElement("div");

    message.className = `message ${sender}`;

    // Prevent HTML injection
    message.textContent = text;

    chatBox.appendChild(message);

    chatBox.scrollTop = chatBox.scrollHeight;

    return message;
}


// ==========================================
// DISPLAY LOADING MESSAGE
// ==========================================

function showLoading() {

    const loading = document.createElement("div");

    loading.className = "loading";
    loading.id = "loadingMessage";

    loading.textContent = "Dzongkha AI is thinking...";

    chatBox.appendChild(loading);

    chatBox.scrollTop = chatBox.scrollHeight;
}


// ==========================================
// REMOVE LOADING MESSAGE
// ==========================================

function removeLoading() {

    const loading = document.getElementById("loadingMessage");

    if (loading) {
        loading.remove();
    }
}


// ==========================================
// SEND MESSAGE TO FASTAPI BACKEND
// ==========================================

async function sendMessage(message) {

    message = message.trim();

    if (!message || isLoading) {
        return;
    }

    isLoading = true;

    sendButton.disabled = true;
    userInput.disabled = true;

    // Remove welcome screen
    const welcome = document.getElementById("welcomeScreen");

    if (welcome) {
        welcome.remove();
    }

    // Display English question
    displayMessage(message, "user");

    // Clear input
    userInput.value = "";

    // Show loading indicator
    showLoading();

    try {

        // Send request to FastAPI
        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                // Send previous English conversation
                history: conversationHistory

            })

        });

        // Read server response
        const data = await response.json();

        removeLoading();

        if (!response.ok) {

            throw new Error(
                data.detail || "Unable to generate an answer."
            );

        }

        if (!data.response) {

            throw new Error(
                "The AI returned an empty Dzongkha response."
            );

        }

        if (!data.english_response) {

            throw new Error(
                "The English answer was not returned by the backend."
            );

        }

        // Display Dzongkha answer
        displayMessage(data.response, "bot");

        // ==================================
        // SAVE ENGLISH CONVERSATION HISTORY
        // ==================================

        conversationHistory.push(

            {
                role: "user",
                content: message
            },

            {
                role: "assistant",
                content: data.english_response
            }

        );

        // Keep only the latest 10 messages
        conversationHistory = conversationHistory.slice(-10);

    }

    catch (error) {

        removeLoading();

        console.error("Chatbot Error:", error);

        displayMessage(
            "Connection error: " + error.message,
            "error"
        );

    }

    finally {

        isLoading = false;

        sendButton.disabled = false;
        userInput.disabled = false;

        userInput.focus();

        chatBox.scrollTop = chatBox.scrollHeight;

    }

}


// ==========================================
// HANDLE SEND BUTTON
// ==========================================

chatForm.addEventListener("submit", function(event) {

    event.preventDefault();

    sendMessage(userInput.value);

});


// ==========================================
// NEW CHAT
// ==========================================

function newChat() {

    if (isLoading) return;

    // Reset conversation memory
    conversationHistory = [];

    // Restore welcome screen
    chatBox.innerHTML = `

        <div class="welcome" id="welcomeScreen">

            <div class="welcome-icon">
                རྫོང་ཁ
            </div>

            <h2>How can I help you today?</h2>

            <p>
                Ask your questions in English.
                Your AI assistant will answer in Dzongkha.
            </p>

            <div class="suggestions">

                <button class="suggestion-btn"
                    data-prompt="What is artificial intelligence?">
                    What is AI?
                </button>

                <button class="suggestion-btn"
                    data-prompt="Explain machine learning in simple terms.">
                    Explain machine learning
                </button>

                <button class="suggestion-btn"
                    data-prompt="Why is education important?">
                    Importance of education
                </button>

            </div>

        </div>

    `;

    userInput.value = "";
    userInput.focus();

}


// ==========================================
// CLEAR CHAT
// ==========================================

function clearChat() {

    if (isLoading) return;

    // Clear conversation history
    conversationHistory = [];

    // Remove all messages
    chatBox.innerHTML = "";

    userInput.value = "";
    userInput.focus();

}


// ==========================================
// BUTTON EVENTS
// ==========================================

newChatButton.addEventListener("click", newChat);

clearChatButton.addEventListener("click", clearChat);


// ==========================================
// SUGGESTED QUESTIONS
// ==========================================

chatBox.addEventListener("click", function(event) {

    const button = event.target.closest("[data-prompt]");

    if (!button || isLoading) return;

    const question = button.dataset.prompt;

    sendMessage(question);

});


// ==========================================
// INITIALIZATION
// ==========================================

console.log("Dzongkha AI Chatbot frontend loaded.");

userInput.focus();
