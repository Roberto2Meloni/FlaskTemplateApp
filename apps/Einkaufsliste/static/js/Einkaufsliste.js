console.log("Hello World von der Einkauflsite js");

document.addEventListener("DOMContentLoaded", function () {
  // Add loading state to buttons
  const buttons = document.querySelectorAll(".btn-custom");
  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      if (!this.href.includes("delete")) {
        const originalContent = this.innerHTML;
        this.innerHTML = '<span class="loading-spinner"></span> Laden...';
        this.style.pointerEvents = "none";

        // Reset after 2 seconds if still on page
        setTimeout(() => {
          this.innerHTML = originalContent;
          this.style.pointerEvents = "auto";
        }, 2000);
      }
    });
  });

  // Enhanced hover effects for table rows
  const rows = document.querySelectorAll(".clickable-row");
  rows.forEach((row) => {
    row.addEventListener("mouseenter", function () {
      this.style.transform = "translateX(5px)";
    });

    row.addEventListener("mouseleave", function () {
      this.style.transform = "translateX(0)";
    });
  });
});
