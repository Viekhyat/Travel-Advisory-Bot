function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === "") return;

    // Display the user message
    displayMessage(userInput, "user");

    // Disable the input and button to simulate bot thinking
    document.getElementById('user-input').disabled = true;
    document.getElementById('send-button').disabled = true;

    // Display a thinking message
    const thinkingMessage = "Bot is thinking...";
    displayMessage(thinkingMessage, "bot");

    // Simulate a loading state
    setTimeout(() => {
        // Remove the thinking message
        const chatBox = document.getElementById('chat-box');
        const thinkingElements = chatBox.getElementsByClassName('thinking');
        while (thinkingElements.length > 0) {
            thinkingElements[0].remove();
        }

        // Send the message to the Flask backend running on port 5000
        fetch('http://localhost:8075/chat', {   // Make sure this points to port 5000
            method: 'POST',
            body: JSON.stringify({ message: userInput }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Display the chatbot's reply
            displayMessage(data.reply, "bot");

            // Re-enable input and button after the bot responds
            document.getElementById('user-input').disabled = false;
            document.getElementById('send-button').disabled = false;
        })
        .catch(error => {
            console.error("Error:", error);
            displayMessage("Oops! Something went wrong.", "bot");
            document.getElementById('user-input').disabled = false;
            document.getElementById('send-button').disabled = false;
        });

        // Clear the input field
        document.getElementById('user-input').value = '';  
    }, 1000);  // Simulate bot delay of 1 second
}

function displayMessage(message, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;
    
    // If the message is the thinking message, add a special class
    if (message === "Bot is thinking...") {
        messageElement.className += ' thinking';
    }
    
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;  // Scroll to the bottom
}

function toggleSendButton() {
    const userInput = document.getElementById('user-input').value;
    const sendButton = document.getElementById('send-button');
    sendButton.disabled = userInput.trim() === "";
}

document.getElementById('user-input').addEventListener('keypress', handleKeyPress);