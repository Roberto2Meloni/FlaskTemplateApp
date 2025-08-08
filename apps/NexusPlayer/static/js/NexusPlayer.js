document.addEventListener("DOMContentLoaded", function () {
  // Hamburger Menu Funktionalität
  const hamburgerMenu = document.getElementById("hamburgerMenu");
  const navigation = document.getElementById("navigation");

  if (hamburgerMenu && navigation) {
    hamburgerMenu.addEventListener("click", function () {
      navigation.classList.toggle("collapsed");

      // Icon ändern
      const icon = hamburgerMenu.querySelector("i");
      if (navigation.classList.contains("collapsed")) {
        icon.className = "bi bi-chevron-right";
      } else {
        icon.className = "bi bi-list";
      }
    });
  }
});
