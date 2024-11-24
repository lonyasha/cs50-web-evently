// Fetch messages dynamically for a specific chat
async function updateChatContent(chatId) {
  const response = await fetch(`/api/chats/${chatId}/messages/`);
  const data = await response.json();

  // Update warning if present
  const warningDiv = document.querySelector(`#chat-${chatId} .chat-warning`);
  if (data.warning) {
    if (warningDiv) {
      warningDiv.innerText = data.warning;
    } else {
      const newWarning = document.createElement("div");
      newWarning.className = "chat-warning";
      newWarning.innerText = data.warning;
      document.getElementById(`messages-${chatId}`).before(newWarning);
    }
  } else if (warningDiv) {
    warningDiv.remove(); // Remove warning if no longer applicable
  }

  // Update messages
  const messagesDiv = document.getElementById(`messages-${chatId}`);
  messagesDiv.innerHTML = data.messages
    .map(
      (msg) =>
        `<p><strong>${msg.user}:</strong> ${msg.message} <em>${msg.created_at}</em></p>`
    )
    .join("");
}

// Periodically refresh chat content
function startChatUpdates(chatId) {
  setInterval(() => updateChatContent(chatId), 5000); // Refresh every 5 seconds
}

// Initialize updates for all chats on the page
function initializeDynamicUpdates(chats) {
  chats.forEach((chat) => {
    startChatUpdates(chat.id);
  });
}

// Fetch chats and initialize everything
async function fetchChats() {
  const response = await fetch("/api/events/<pk>/chats/");
  const chats = await response.json();
  initializeChats(chats);
  initializeDynamicUpdates(chats); // Start periodic updates for all chats
}

// Initialize tabs and chat containers dynamically
function initializeChats(chats) {
  const tabsContainer = document.getElementById("tabs");
  const chatContents = document.getElementById("chat-contents");

  chats.forEach((chat, index) => {
    // Create a tab for each chat
    const tab = document.createElement("button");
    tab.className = "tab";
    tab.innerText = chat.name;
    tab.dataset.chatId = chat.id;
    if (index === 0) tab.classList.add("active"); // Set first tab as active
    tabsContainer.appendChild(tab);

    // Create chat container
    const chatContainer = document.createElement("div");
    chatContainer.className = "chat-container";
    chatContainer.id = `chat-${chat.id}`;
    if (index === 0) chatContainer.classList.add("active"); // Set first chat container as active
    chatContainer.innerHTML = `
          ${
            chat.warning
              ? `<div class="chat-warning">${chat.warning}</div>`
              : ""
          }
          <div class="messages" id="messages-${chat.id}">
              ${chat.messages
                .map(
                  (msg) =>
                    `<p><strong>${msg.user}:</strong> ${msg.message} <em>${msg.created_at}</em></p>`
                )
                .join("")}
          </div>
          <div class="message-input">
              <textarea id="message-input-${
                chat.id
              }" rows="3" placeholder="Type your message..."></textarea>
              <button onclick="sendMessage(${chat.id})">Send</button>
          </div>
      `;
    chatContents.appendChild(chatContainer);
  });

  // Add event listener for tab switching
  tabsContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains("tab")) {
      // Deactivate all tabs and chat containers
      document
        .querySelectorAll(".tab")
        .forEach((tab) => tab.classList.remove("active"));
      document
        .querySelectorAll(".chat-container")
        .forEach((chat) => chat.classList.remove("active"));

      // Activate selected tab and corresponding chat container
      e.target.classList.add("active");
      const chatId = e.target.dataset.chatId;
      document.getElementById(`chat-${chatId}`).classList.add("active");
    }
  });
}

// Send a message
async function sendMessage(chatId) {
  const messageInput = document.getElementById(`message-input-${chatId}`);
  const messageText = messageInput.value.trim();
  if (messageText) {
    const response = await fetch(`/api/chats/${chatId}/messages/add/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ message: messageText }),
    });
    if (response.ok) {
      const messagesDiv = document.getElementById(`messages-${chatId}`);
      messagesDiv.innerHTML += `<p><strong>You:</strong> ${messageText}</p>`;
      messagesDiv.scrollTop = messagesDiv.scrollHeight; // Auto-scroll to bottom
      messageInput.value = ""; // Clear the input
    }
  }
}

// Utility function to get CSRF token
function getCSRFToken() {
  const cookies = document.cookie.split(";");
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === "csrftoken") return value;
  }
  return "";
}

// Fetch chats on page load
fetchChats();
