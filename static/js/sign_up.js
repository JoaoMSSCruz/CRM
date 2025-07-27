document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("togglePassword");
    const passwordField = document.getElementById("password");
  
    toggle.addEventListener("click", () => {
      const isPassword = passwordField.type === "password";
      passwordField.type = isPassword ? "text" : "password";
      toggle.textContent = isPassword ? "🙈" : "👁️";
    });
  
  
    const form = document.getElementById("signUpForm");
  
    form.addEventListener("submit", (event) => {  
  
      event.preventDefault();
  
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      fetch("/receive_sign_up", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username: username, password: password })
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === "success") {
          alert("Successful sign up!");
          window.location.href = "/";
        } else {
          alert("Failed to sign up, Username already in use!");
          // Limpa os campos manualmente
          document.getElementById("username").value = "";
          document.getElementById("password").value = "";
        }
      });
    });
  });
  