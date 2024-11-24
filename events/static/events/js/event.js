document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("usernames").addEventListener(
    "input",
    debounce(function () {
      const query = this.value;

      // Trigger search only if the query length is more than 1 character
      if (query.length < 2) {
        return; // Do nothing if the query is less than 2 characters
      }

      fetch(`/search-users/?q=${query}`)
        .then((response) => response.json())
        .then((data) => {
          const list = document.getElementById("search-results-list");
          list.innerHTML = ""; // Clear previous results

          // Check if there are results
          if (data.length > 0) {
            data.forEach((user) => {
              const userItem = document.createElement("li");
              userItem.textContent = `${user.username} - ${user.first_name} ${user.last_name}`;

              // Add a button to select the user
              const selectButton = document.createElement("button");
              selectButton.textContent = "Add";
              selectButton.type = "button";
              selectButton.addEventListener("click", function () {
                console.log("Button Add is clicked");
                if (!isUserSelected(user.id)) {
                  addUserToSelectedList(
                    user.id,
                    user.username,
                    user.first_name,
                    user.last_name
                  );
                  list.innerHTML = "";
                } else {
                  alert("This user is already added.");
                }
              });
              userItem.appendChild(selectButton);
              list.appendChild(userItem);
            });
          } else {
            const noResultsItem = document.createElement("li");
            noResultsItem.textContent = "No users found.";
            list.appendChild(noResultsItem);
          }
        });
    }, 300)
  );

  document
    .getElementById("search-user-form")
    .addEventListener("submit", function (event) {
      event.preventDefault(); // Prevent the default form submission behavior

      const usernamesField = document.getElementById("usernames");
      const selectedUsersList = document.getElementById("selected-users-list");

      // Gather the selected usernames
      const selectedUsernames = selectedUsers.map((user) => user.username);

      if (selectedUsernames.length === 0) {
        alert("No users selected!");
        return; // Don't proceed if no users are selected
      }

      console.log("Sending data to:", this.action);
      console.log("Usernames:", selectedUsernames);

      // Send the data via fetch
      fetch(this.action, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ usernames: selectedUsernames }),
      })
        .then((response) => {
          if (response.ok) {
            console.log("Response status:", response.status);
            return response.json();
          }
          throw new Error("Failed to send invitations.");
        })
        .then((data) => {
          console.log("Response data:", data);
          alert(data.message || "Invitations sent successfully!");

          // Clear the selected users list
          selectedUsers = [];
          selectedUsersList.innerHTML = "";
          usernamesField.value = "";
        })
        .catch((error) => {
          console.error("Fetch error:", error);
          alert("Error sending invitations. Please try again.");
        });
    });

  const taskModal = document.getElementById("taskModal");
  const modalTitle = document.getElementById("taskModalLabel");
  const modalForm = document.getElementById("taskForm");
  const modalFormContent = document.getElementById("modalFormContent");

  // Event listener for showing the modal
  taskModal.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    const isEdit = button.getAttribute("data-task-id") !== null;
    const taskUrl = button.getAttribute("data-task-url");

    // Set modal title based on whether it is creating or editing
    modalTitle.textContent = isEdit ? "Edit Task" : "Create Task";

    // Fetch the form HTML and inject it into the modal
    fetch(taskUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Error fetching the form: ${response.statusText}`);
        }
        return response.json(); // Expect JSON response with 'html'
      })
      .then((data) => {
        modalFormContent.innerHTML = data.html; // Inject form HTML into modal
        modalForm.action = taskUrl; // Update form action URL
      })
      .catch((error) => {
        console.error("Error loading the form:", error);
        modalFormContent.innerHTML = `<p class="text-danger">Failed to load the form. Please try again later.</p>`;
      });
  });

  modalForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const formData = new FormData(modalForm);

    fetch(modalForm.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Close the modal and reload the page or update the task list dynamically
          taskModal.querySelector('[data-bs-dismiss="modal"]').click();
          window.location.reload(); // Reload the page (or implement dynamic task list update)
        } else {
          // Render form with errors
          modalFormContent.innerHTML = data.html;
        }
      })
      .catch((error) => {
        console.error("Error submitting the form:", error);
        modalFormContent.innerHTML = `<p class="text-danger">An error occurred. Please try again.</p>`;
      });
  });
});

let selectedUsers = [];

function isUserSelected(userId) {
  return selectedUsers.some((user) => user.id === userId);
}

function addUserToSelectedList(userId, username, firstName, lastName) {
  const selectedUsersList = document.getElementById("selected-users-list");

  // Create the selected user item
  const selectedUserItem = document.createElement("li");
  selectedUserItem.textContent = `${username} - ${firstName} ${lastName}`;

  // Add a remove button to each selected user
  const removeButton = document.createElement("button");
  removeButton.textContent = "Remove";
  removeButton.type = "button";
  removeButton.addEventListener("click", function () {
    selectedUserItem.remove();
    removeUserFromSelectedList(userId); // Remove user from the selected list
  });

  selectedUserItem.appendChild(removeButton);
  selectedUsersList.appendChild(selectedUserItem);

  // Add the user to the selectedUsers array
  selectedUsers.push({ id: userId, username });

  const searchField = document.getElementById("usernames");
  searchField.value = "";
  searchField.focus();
}

function removeUserFromSelectedList(userId) {
  selectedUsers = selectedUsers.filter((user) => user.id !== userId);
}

function debounce(func, delay) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), delay);
  };
}

// Helper function to retrieve the CSRF token
function getCSRFToken() {
  return document.querySelector("[name=csrfmiddlewaretoken]").value;
}
