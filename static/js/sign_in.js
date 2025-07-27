document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("togglePassword");
  const passwordField = document.getElementById("password");

  toggle.addEventListener("click", () => {
    const isPassword = passwordField.type === "password";
    passwordField.type = isPassword ? "text" : "password";
    toggle.textContent = isPassword ? "🙈" : "👁️";
  });


  const form = document.getElementById("signInForm");

  form.addEventListener("submit", (event) => {  

    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    fetch("/receive_sign_in", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username: username, password: password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "success") {
        alert("Successful Sign in!");
        window.location.href = "/selection_menu";
      } else {
        alert("Failed Sign in! Verify your credentials!");
        document.getElementById("password").value = "";
      }
    });
  });
});
