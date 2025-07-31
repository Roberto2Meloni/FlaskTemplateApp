// Sidebar Toggle Funktionalität - Mobile + Desktop
document.addEventListener("DOMContentLoaded", function () {
  // Elemente finden
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebar-toggle"); // Desktop
  const mobileToggle = document.getElementById("mobile-toggle"); // Mobile
  const sidebarOverlay = document.getElementById("sidebar-overlay");

  // Prüfen ob Mobile oder Desktop
  function isMobile() {
    return window.innerWidth <= 768;
  }

  // Toggle Sidebar Funktion
  function toggleSidebar() {
    const isCurrentlyCollapsed = sidebar.classList.contains("collapsed");

    if (isMobile()) {
      // MOBILE: collapsed = sichtbar, nicht collapsed = versteckt
      sidebar.classList.toggle("collapsed");

      // Mobile Toggle Button Animation
      if (mobileToggle) {
        mobileToggle.classList.toggle("active");
      }

      // Overlay NUR auf Mobile
      if (sidebarOverlay) {
        sidebarOverlay.classList.toggle("active");
      }

      // Body-Scroll verhindern wenn Sidebar offen
      if (!isCurrentlyCollapsed) {
        // Wird sichtbar
        document.body.style.overflow = "hidden";
      } else {
        // Wird versteckt
        document.body.style.overflow = "auto";
      }
    } else {
      // DESKTOP: collapsed = schmal, nicht collapsed = normal
      sidebar.classList.toggle("collapsed");

      // Desktop Toggle Button Animation
      if (sidebarToggle) {
        sidebarToggle.classList.toggle("active");
      }

      // KEIN Overlay auf Desktop
      if (sidebarOverlay) {
        sidebarOverlay.classList.remove("active");
      }

      // Body-Scroll immer normal auf Desktop
      document.body.style.overflow = "auto";
    }

    console.log(
      "Sidebar toggled - Mobile:",
      isMobile(),
      "Collapsed:",
      sidebar.classList.contains("collapsed")
    );
  }

  // Click Event für Desktop Hamburger-Button
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", function (event) {
      event.preventDefault();
      toggleSidebar();
    });
  }

  // Click Event für Mobile Toggle-Button
  if (mobileToggle) {
    mobileToggle.addEventListener("click", function (event) {
      event.preventDefault();
      toggleSidebar();
    });
  }

  // Click Event für Overlay - NUR auf Mobile
  if (sidebarOverlay) {
    sidebarOverlay.addEventListener("click", function () {
      if (isMobile()) {
        toggleSidebar();
      }
    });
  }

  // ESC-Taste zum Schließen
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      if (isMobile()) {
        // Auf Mobile: Schließen wenn sichtbar
        if (sidebar.classList.contains("collapsed")) {
          toggleSidebar();
        }
      } else {
        // Auf Desktop: Ausklappen wenn collapsed
        if (sidebar.classList.contains("collapsed")) {
          toggleSidebar();
        }
      }
    }
  });

  // Window Resize Handler - Responsive Verhalten
  window.addEventListener("resize", function () {
    const wasMobile = document.body.dataset.wasMobile === "true";
    const nowMobile = isMobile();

    if (wasMobile !== nowMobile) {
      // Gerätewechsel: Alles zurücksetzen
      sidebar.classList.remove("collapsed");

      // Beide Toggle-Buttons zurücksetzen
      if (sidebarToggle) {
        sidebarToggle.classList.remove("active");
      }
      if (mobileToggle) {
        mobileToggle.classList.remove("active");
      }

      if (sidebarOverlay) {
        sidebarOverlay.classList.remove("active");
      }

      document.body.style.overflow = "auto";
      document.body.dataset.wasMobile = nowMobile.toString();
    }
  });

  // Initial state
  document.body.dataset.wasMobile = isMobile().toString();

  // Aktiven Link highlighten
  const sidebarLinks = document.querySelectorAll(
    ".sidebar-link:not(.sidebar-toggle)"
  );

  sidebarLinks.forEach((link) => {
    link.addEventListener("click", function (event) {
      if (this.getAttribute("href") === "#") {
        event.preventDefault();
      }

      // Aktiven Link markieren
      sidebarLinks.forEach((l) => l.classList.remove("active"));
      this.classList.add("active");

      // Auf Mobile: Sidebar nach Link-Klick schließen
      if (isMobile() && sidebar.classList.contains("collapsed")) {
        setTimeout(() => {
          toggleSidebar();
        }, 200);
      }

      const linkText = this.querySelector(".sidebar-text")?.textContent;
      console.log("Link geklickt:", linkText);
    });
  });

  // Initialer aktiver Link (Dashboard)
  if (sidebarLinks.length > 0) {
    sidebarLinks[0].classList.add("active");
  }

  console.log("Sidebar JavaScript geladen - Initial Mobile:", isMobile());
  console.log("Mobile Toggle gefunden:", !!mobileToggle);
  console.log("Desktop Toggle gefunden:", !!sidebarToggle);
});
