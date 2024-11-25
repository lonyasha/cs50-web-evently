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
  messagesDiv.innerHTML = renderMessages(data.messages, currentUser);
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
  const response = await fetch("/api/chats/");
  const chats = await response.json();
  console.log(chats);
  initializeChats(chats);
  initializeDynamicUpdates(chats); // Start periodic updates for all chats
}

// Initialize tabs and chat containers dynamically
function initializeChats(chats) {
  const tabsContainer = document.getElementById("tabs");
  const chatContents = document.getElementById("chat-contents");
  let activeChatId = null;

  // Find the chat ID matching the event_pk (if provided)
  if (activeEventPk) {
    const matchingChat = chats.find(
      (chat) => chat.event_pk.toString() === activeEventPk
    );
    if (matchingChat) {
      activeChatId = matchingChat.id;
    }
  }

  chats.forEach((chat, index) => {
    // Create a tab for each chat
    const tab = document.createElement("button");
    tab.className = "list-group-item list-group-item-action";
    tab.innerText = chat.name;
    tab.href = "#";
    tab.dataset.chatId = chat.id;
    if (activeChatId ? chat.id === activeChatId : index === 0) {
      tab.classList.add("active"); // Set the active tab
    }
    tabsContainer.appendChild(tab);

    // Create chat container
    const chatContainer = document.createElement("div");
    chatContainer.className = "chat-container";
    chatContainer.id = `chat-${chat.id}`;
    if (activeChatId ? chat.id === activeChatId : index === 0) {
      chatContainer.classList.add("active"); // Set the active chat container
    }
    chatContainer.innerHTML = `
      ${chat.warning ? `<div class="chat-warning">${chat.warning}</div>` : ""}
      <div class="messages py-3 px-2" id="messages-${chat.id}">
          ${renderMessages(chat.messages, currentUser)}
      </div>
      <div class="message-input mt-3">
          <textarea id="message-input-${
            chat.id
          }" class="form-control" rows="3" placeholder="Type your message..."></textarea>
          <button class="btn btn-primary mt-2 float-end" onclick="sendMessage(${
            chat.id
          })">Send</button>
      </div>
      `;
    chatContents.appendChild(chatContainer);
  });

  // Add event listener for tab switching
  tabsContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains("list-group-item")) {
      // Deactivate all tabs and chat containers
      document
        .querySelectorAll(".list-group-item")
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
    const messagesDiv = document.getElementById(`messages-${chatId}`);

    // Generate a temporary optimistic message ID
    const tempId = `temp-${Date.now()}`;

    // Optimistically update the UI with Bootstrap classes
    const tempMessage = `
      <div id="${tempId}" class="d-flex flex-column align-items-end mb-2">
      <div class="text-muted small">${formatTimestamp(Date.now())}</div>
        <div class="message-bubble message-sender">
          ${messageText}
        </div>
      </div>`;
    messagesDiv.innerHTML += tempMessage;
    messagesDiv.scrollTop = messagesDiv.scrollHeight; // Auto-scroll to bottom
    messageInput.value = ""; // Clear the input immediately

    // Send the message to the server
    const response = await fetch(`/api/chats/${chatId}/messages/add/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ message: messageText }),
    });

    // Handle server errors
    if (!response.ok) {
      // Remove the optimistic message if the request fails
      alert("Failed to send the message. Please try again.");
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

function renderMessages(messages, currentUser) {
  return messages
    .map((msg) => {
      if (msg.user === currentUser) {
        // Current user's message (right-aligned, no username)
        return `
         <div class="d-flex flex-column align-items-end mb-2">
         <div class="text-muted small">${formatTimestamp(msg.created_at)}</div>
           <div class="message-bubble message-sender">
             ${msg.message}
           </div>
         </div>`;
      } else {
        // Other user's message (left-aligned, with username)
        return `
         <div class="d-flex flex-column align-items-start mb-2">
            <div><strong>${
              msg.user
            } </strong><span class="text-muted small">${formatTimestamp(
          msg.created_at
        )}</span></div>
            <div class="message-bubble message-receiver">
              ${msg.message}
            </div>
            
         </div>`;
      }
    })
    .join("");
}

function formatTimestamp(timestamp) {
  const date = new Date(timestamp); // Convert the timestamp into a Date object
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0"); // Add leading zero to month
  const day = String(date.getDate()).padStart(2, "0"); // Add leading zero to day
  const hours = String(date.getHours()).padStart(2, "0"); // Add leading zero to hours
  const minutes = String(date.getMinutes()).padStart(2, "0"); // Add leading zero to minutes
  return `${year}-${month}-${day} ${hours}:${minutes}`; // Format: YYYY-MM-DD HH:mm
}

// Fetch chats on page load
fetchChats();
