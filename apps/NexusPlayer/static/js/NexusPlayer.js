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

  // KORRIGIERTE FUNKTIONALITÄT: Aktive Navigation
  // 1. Alle Menüelemente finden (sowohl upper_items als auch lower_items)
  const allMenuItems = document.querySelectorAll(
    ".upper_items .list, .lower_items .list"
  );

  // 2. Den "Zurück zu Apps" Link ausschließen, da das ein echter Navigationslink ist
  const menuItems = [];
  allMenuItems.forEach(function (item) {
    const linkText = item.querySelector(".list_element").textContent.trim();
    // "Zurück zu Apps" ausschließen, da das zu einer anderen Seite führt
    if (linkText !== "Zurück zu Apps") {
      menuItems.push(item);
    }
  });

  // 3. Für jedes relevante Menüelement einen Event Listener hinzufügen
  menuItems.forEach(function (menuItem) {
    // Den Link im Menüelement finden
    const link = menuItem.querySelector("a");

    if (link) {
      link.addEventListener("click", function (event) {
        // 4. Verhindern, dass der Link aufgerufen wird (da alle "#" sind)
        event.preventDefault();

        // 5. Von ALLEN relevanten Menüelementen die "active" Klasse entfernen
        menuItems.forEach(function (item) {
          item.classList.remove("active");
        });

        // 6. Dem angeklickten Menüelement die "active" Klasse hinzufügen
        menuItem.classList.add("active");

        // Optional: In der Konsole anzeigen, was angeklickt wurde
        const elementName = menuItem.querySelector(".list_element").textContent;
      });
    }
  });
});
