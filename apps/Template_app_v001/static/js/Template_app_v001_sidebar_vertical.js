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

  // Aktiven Link markieren
  function setActiveLink(page) {
    const allMenuItems = document.querySelectorAll(
      ".upper_items .list, .lower_items .list"
    );

    allMenuItems.forEach((item) => {
      const link = item.querySelector("a");
      if (link && link.dataset.page === page) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });
  }

  // Content laden ohne Seite neu zu laden
  async function loadContent(url, page) {
    const contentArea = document.querySelector(".app-content");

    try {
      // Ruft die content-Route auf (nicht die normale Route)
      const response = await fetch(`/Template_app_v001/content/${page}`);
      if (!response.ok) throw new Error("Fehler beim Laden");

      const html = await response.text();
      contentArea.innerHTML = html;

      setActiveLink(page);

      // Spezielle Initialisierung für bestimmte Seiten
      if (
        page === "slot_maschine" &&
        typeof window.initSlotMachine === "function"
      ) {
        window.initSlotMachine();
      }
    } catch (error) {
      console.error("Fehler beim Laden:", error);
      contentArea.innerHTML = "<p>Fehler beim Laden des Inhalts.</p>";
    }
  }

  // Event Listener für Navigation Links
  const navLinks = document.querySelectorAll(".nav-link");

  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      // Nur bei normalem Linksklick abfangen
      // Rechtsklick, Strg+Klick, Cmd+Klick etc. durchlassen für "In neuem Tab öffnen"
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) {
        return; // Standard-Verhalten beibehalten - Seite wird normal geöffnet
      }

      // Normaler Linksklick - verhindern und dynamisch laden
      e.preventDefault();

      const url = this.getAttribute("href");
      const page = this.dataset.page;

      // Content laden
      loadContent(url, page);

      // URL aktualisieren ohne Seite neu zu laden
      history.pushState({ page: page }, "", url);
    });
  });

  // Browser Zurück/Vor Buttons unterstützen
  window.addEventListener("popstate", function (e) {
    if (e.state && e.state.page) {
      const page = e.state.page;
      loadContent(window.location.pathname, page);
    } else {
      // Fallback: Seite neu laden wenn kein State vorhanden
      window.location.reload();
    }
  });

  // Initialen aktiven Link setzen basierend auf aktueller URL
  const currentPath = window.location.pathname;
  const pathParts = currentPath.split("/");
  const currentPage = pathParts[pathParts.length - 1] || "dashboard";

  setActiveLink(currentPage);

  // Initial State setzen
  history.replaceState({ page: currentPage }, "", currentPath);
});
