document.getElementById("clientForm").addEventListener("submit", function(e) {
    e.preventDefault();
  
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    data.active = formData.has("active");
  
    fetch("/add_client", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(response => {
      if (response.status === "success") {
        alert("Client added successfully!");
        window.opener.location.reload();  // Atualiza a lista de clientes
        window.close();                   // Fecha o popup
      } else {
        alert("Error adding client: " + (response.message || "Unknown error"));
      }
    });
  });
  