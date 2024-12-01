document.addEventListener("DOMContentLoaded", function () {
  // Event RSVP form
  const searchInput = document.getElementById("usernames");
  const searchResultsList = document.getElementById("search-results-list");
  const selectedUsersList = document.getElementById("selected-users-list");

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

  // Invite users form
  const inviteForm = document.getElementById("invite-users-form");
  // Form submission
  if (inviteForm) {
    inviteForm.addEventListener("submit", function (e) {
      e.preventDefault(); // Stops the page from reloading
      const submitButton = inviteForm.querySelector("button[type='submit']");
      const selectedUserIds = Object.keys(selectedUsers);
      if (selectedUserIds.length > 0) {
        submitButton.textContent = "Sending...";
        submitButton.disabled = true;

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
              updateRsvpList(eventPk); // Update RSVP dynamically

              selectedUsersList.innerHTML = "";
            } else {
              alert("Error sending invitations.");
            }
          })
          .catch((error) => {
            console.error("Error in fetch:", error);
            alert("Error sending invitations.");
          })
          .finally(() => {
            submitButton.textContent = "Send invitations";
            submitButton.disabled = false;
          });
      } else {
        alert("No users selected.");
      }
    });
  } else {
    console.error("Invite form not found.");
  }

  // Update RSVP list dynamically
  function updateRsvpList(eventPk) {
    // Show a loading spinner
    const rsvpContainer = document.querySelector(".rsvp-list");
    rsvpContainer.innerHTML = "<p>Loading...</p>";

    fetch(`/events/${eventPk}/update-rsvp-list/`)
      .then((response) => response.json())
      .then((data) => {
        // Replace RSVP list content with the updated HTML
        rsvpContainer.innerHTML = data.html;
      })
      .catch((error) => {
        console.error("Error updating RSVP list:", error);
        rsvpContainer.innerHTML =
          '<p class="text-danger">Failed to load RSVPs.</p>';
      });
  }

  // Task modal

  const taskModal = new bootstrap.Modal(document.getElementById("taskModal"));
  const modalTitle = document.getElementById("taskModalLabel");
  const modalForm = document.getElementById("taskForm");
  const modalFormContent = document.getElementById("modalFormContent");

  // Open the modal programmatically when a button is clicked
  document.querySelectorAll("[data-task-url]").forEach((button) => {
    button.addEventListener("click", function () {
      const taskUrl = button.getAttribute("data-task-url");
      const isEdit = button.hasAttribute("data-task-id");
      const taskModalElement = document.querySelector("#taskModal");

      modalTitle.textContent = isEdit ? "Edit task" : "Create task";

      // Fetch the form and open the modal
      fetch(taskUrl)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Error fetching the form: ${response.statusText}`);
          }
          return response.json();
        })
        .then((data) => {
          modalFormContent.innerHTML = data.html;
          modalForm.action = taskUrl;
          taskModalElement.style.display = "block";
          taskModalElement.removeAttribute("aria-hidden");
        })
        .catch((error) => {
          console.error("Error loading the form:", error);
          modalFormContent.innerHTML = `<p class="text-danger">Failed to load the form. Please try again later.</p>`;
        });
    });
  });

  // Handle form submission
  modalForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const formData = new FormData(modalForm);

    const taskModalElement = document.querySelector("#taskModal");
    const eventPk = taskModalElement.getAttribute("data-event-pk");

    fetch(modalForm.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          if (eventPk) {
            // Reload the task list
            fetch(`/events/${eventPk}/tasks/reload/`)
              .then((response) => response.json())
              .then((reloadData) => {
                const taskList = document.querySelector(".task-list");
                if (taskList) {
                  taskList.innerHTML = reloadData.html; // Replace the task list content
                }
                taskModalElement.style.display = "none";
                taskModalElement.removeAttribute("aria-hidden");
                const backdrop = document.querySelector(".modal-backdrop");
                if (backdrop) {
                  backdrop.style.display = "none";
                }
              })
              .catch((error) => {
                console.error("Error reloading task list:", error);
              });
          } else {
            console.error("Event PK not found on modal.");
          }
        } else {
          // Render form with validation errors
          modalFormContent.innerHTML = data.html;
        }
      })
      .catch((error) => {
        console.error("Error submitting the form:", error);
        modalFormContent.innerHTML = `<p class="text-danger">An error occurred. Please try again.</p>`;
      });
  });

  // Close modal programmatically
  document
    .getElementById("closeModalButton")
    .addEventListener("click", function () {
      const taskModalElement = document.querySelector("#taskModal");
      taskModalElement.style.display = "none";
      taskModalElement.removeAttribute("aria-hidden");
    });

  // Delete event confirmation
  document
    .getElementById("deleteButton")
    .addEventListener("click", function (e) {
      if (!confirm("Are you sure you want to delete this event?")) {
        e.preventDefault();
      }
    });

  // Handle delete task forms
  document.querySelectorAll(".delete-task-form").forEach((form) => {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      const url = form.action;
      const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
      const eventPk = form.getAttribute("data-event-pk");

      if (confirm("Are you sure you want to delete this task?")) {
        fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              // Reload the page if the task is successfully deleted
              location.reload();
            } else {
              alert("Failed to delete the task.");
            }
          })
          .catch((error) => {
            console.error("Error deleting task:", error);
            alert("An error occurred. Please try again.");
          });
      }
    });
  });
});
