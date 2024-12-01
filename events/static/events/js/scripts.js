document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".toggle-completion-btn");

  buttons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      const url = this.href;

      fetch(url, {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => {
          if (response.redirected) {
            // If the response is a redirect, reload the page
            location.href = response.url;
          } else {
            // Alternatively, reload the page
            location.reload();
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("Failed to toggle task completion.");
        });
    });
  });
});
