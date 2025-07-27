function openAddServiceWindow() {
    const width = 600;
    const height = 700;
  
    const left = (screen.width / 2) - (width / 2);
    const top = (screen.height / 2) - (height / 2);
  
    window.open(
      "/add_service_form",
      "Add Service",
      `width=${width},height=${height},top=${top},left=${left},resizable=yes`
    );
  }