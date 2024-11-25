document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("usernames");
  const searchResultsList = document.getElementById("search-results-list");
  const selectedUsersList = document.getElementById("selected-users-list");
  const rsvpList = document.querySelector(".rsvp-list");

  let selectedUsers = {};

  // Fetch search results
  searchInput.addEventListener("input", function () {
    const query = this.value.trim();
    if (query.length > 2) {
      fetch(`/search-users?q=${query}`)
        .then((response) => response.json())
        .then((data) => {
          searchResultsList.innerHTML = "";
          data.forEach((user) => {
            const li = document.createElement("li");
            li.className =
              "list-group-item d-flex justify-content-between align-items-center";
            li.textContent = `${user.username} (${user.first_name} ${user.last_name})`;
            const addButton = document.createElement("button");
            addButton.className = "btn btn-primary btn-sm";
            addButton.textContent = "Add";
            addButton.onclick = function (e) {
              e.preventDefault();
              addSelectedUser(user);
              // Clear search input and search results
              searchInput.value = "";
              searchResultsList.innerHTML = "";
            };
            li.appendChild(addButton);
            searchResultsList.appendChild(li);
          });
        });
    } else {
      searchResultsList.innerHTML = "";
    }
  });

  // Add user to selected list
  function addSelectedUser(user) {
    if (selectedUsers[user.id]) return; // Prevent duplicates

    selectedUsers[user.id] = user;
    const li = document.createElement("li");
    li.className =
      "list-group-item d-flex justify-content-between align-items-center";
    li.textContent = `${user.username} (${user.first_name} ${user.last_name})`;
    li.setAttribute("data-user-id", user.id);

    const removeButton = document.createElement("button");
    removeButton.className = "btn btn-danger btn-sm";
    removeButton.textContent = "Remove";
    removeButton.onclick = function (e) {
      e.preventDefault(); // Prevent any unintended form submission
      removeSelectedUser(user.id);
    };
    li.appendChild(removeButton);
    selectedUsersList.appendChild(li);
  }

  // Remove user from selected list
  function removeSelectedUser(userId) {
    delete selectedUsers[userId];
    const userLi = selectedUsersList.querySelector(
      `[data-user-id="${userId}"]`
    );
    if (userLi) userLi.remove();
  }

  // Form submission
  document
    .getElementById("invite-users-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();

      const selectedUserIds = Object.keys(selectedUsers);

      const submitButton = document.querySelector(
        "#invite-users-form button[type='submit']"
      );
      submitButton.disabled = true;
      submitButton.textContent = "Sending...";

      if (selectedUserIds.length > 0) {
        fetch(this.action, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": this.querySelector('[name="csrfmiddlewaretoken"]')
              .value,
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({ user_ids: selectedUserIds }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.message.includes("successfully")) {
              selectedUsersList.innerHTML = "";
              selectedUsers = {};
              // Fetch updated RSVP list
              updateRsvpList();
            } else {
              alert("Error sending invitations.");
            }
          })
          .catch(() => {
            alert("Error sending invitations.");
          })
          .finally(() => {
            submitButton.disabled = false;
            submitButton.textContent = "Send invitations";
          });
      } else {
        alert("No users selected.");
      }
    });

  function updateRsvpList() {
    fetch(window.location.href)
      .then((response) => response.text())
      .then((html) => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const updatedRsvpList = doc.querySelector(".rsvp-list").innerHTML;
        rsvpList.innerHTML = updatedRsvpList;
      })
      .catch((error) => {
        console.error("Error updating RSVP list:", error);
      });
  }

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
