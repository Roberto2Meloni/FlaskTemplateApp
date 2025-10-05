// Globale Variable für den aktuellen Pfad
document.addEventListener("DOMContentLoaded", function () {
  // Hamburger Menu Funktionalität (unverändert)
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

  // Navigation mit AJAX (erweitert)
  const allMenuItems = document.querySelectorAll(
    ".upper_items .list, .lower_items .list"
  );

  const menuItems = [];
  allMenuItems.forEach(function (item) {
    const linkText = item.querySelector(".list_element").textContent.trim();
    if (linkText !== "Zurück zu Apps") {
      menuItems.push(item);
    }
  });

  menuItems.forEach(function (menuItem) {
    const link = menuItem.querySelector("a");

    if (link) {
      link.addEventListener("click", function (event) {
        event.preventDefault();

        menuItems.forEach(function (item) {
          item.classList.remove("active");
        });

        menuItem.classList.add("active");

        // NEU: Seite laden
        const elementName = menuItem
          .querySelector(".list_element")
          .textContent.trim();

        if (elementName === "Dashboard") {
          loadPage(url_dashboard);
        } else if (elementName === "Slot Maschine") {
          loadPage(url_slot_maschine).then(() => {
            if (typeof window.initSlotMachine === "function") {
              window.initSlotMachine(); // ← Ruft updateDisplay() auf
            }
          });
          console.log("Slot Maschine geklickt mit url " + url_slot_maschine);
        } else if (elementName === "Admin") {
          console.log("Admin geklickt mit url " + url_app_settings);
          loadPage(url_app_settings);
        }
      });
    }
  });
});

function loadPage(url) {
  return fetch(url)
    .then((response) => response.text())
    .then((html) => {
      document.querySelector(".app-content").innerHTML = html;
      // Warte einen kurzen Moment damit der DOM aktualisiert wird
      return new Promise((resolve) => setTimeout(resolve, 10));
    });
}
