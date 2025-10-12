document.addEventListener("DOMContentLoaded", function () {
  console.log("=== Template_app_v001 JavaScript gestartet ===");

  // ========================================
  // HAMBURGER MENU
  // ========================================
  const hamburgerMenu = document.getElementById("hamburgerMenu");
  const navigation = document.getElementById("navigation");
  if (hamburgerMenu && navigation) {
    hamburgerMenu.addEventListener("click", function () {
      navigation.classList.toggle("collapsed");
      const icon = hamburgerMenu.querySelector("i");
      navigation.classList.contains("collapsed")
        ? (icon.className = "bi bi-chevron-right")
        : (icon.className = "bi bi-list");
    });
  }

  // ========================================
  // FUNKTION: Aktiven Link setzen (Hauptnav)
  // ========================================
  function setActiveLinkByURL() {
    console.log("\n--- setActiveLinkByURL() (Hauptnavigation) ---");

    const currentURL = window.location.pathname;
    console.log("Aktuelle URL:", currentURL);

    const navLinks = document.querySelectorAll("#navigation .nav-link");
    const linksInfo = [];

    navLinks.forEach((link) => {
      linksInfo.push({
        href: link.getAttribute("href"),
        page: link.dataset.page,
        text:
          link.querySelector(".list_element")?.textContent.trim() ||
          "Unbekannt",
        parentLi: link.closest(".list"),
      });
    });

    let matchingLink = linksInfo.find(
      (linkInfo) => linkInfo.href === currentURL
    );

    // Spezialfall: Root → Dashboard
    if (
      !matchingLink &&
      (currentURL === "/" || currentURL.endsWith("/Template_app_v001"))
    ) {
      matchingLink = linksInfo.find(
        (linkInfo) => linkInfo.page === "dashboard"
      );
    }

    if (matchingLink) {
      linksInfo.forEach((linkInfo) =>
        linkInfo.parentLi.classList.remove("active")
      );
      matchingLink.parentLi.classList.add("active");
      console.log(`✓ Hauptnav: "${matchingLink.text}" aktiv`);
    }

    console.log("--- Ende setActiveLinkByURL() ---\n");
  }

  // ========================================
  // FUNKTION: Aktive Links im Admin setzen
  // ========================================
  function setAdminActiveLinks() {
    const currentURL = window.location.pathname;
    const mainNavLinks = document.querySelectorAll("#navigation .nav-link");
    const mainLinksInfo = [];

    mainNavLinks.forEach((link) => {
      mainLinksInfo.push({
        page: link.dataset.page,
        parentLi: link.closest(".list"),
      });
    });

    // ALLE Hauptnav-Links deaktivieren
    mainLinksInfo.forEach((linkInfo) => {
      linkInfo.parentLi.classList.remove("active");
    });

    // NUR Admin-Button aktivieren
    const adminButton = mainLinksInfo.find(
      (linkInfo) => linkInfo.page === "app_settings"
    );
    if (adminButton) {
      adminButton.parentLi.classList.add("active");
    }

    // Admin-Sidebar
    const adminSidebar = document.getElementById("navigation-admin");

    if (!adminSidebar) {
      console.log("  ✗ Admin-Sidebar nicht gefunden!");
      return;
    }

    const adminNavLinks = document.querySelectorAll(
      "#navigation-admin .nav-link-admin"
    );
    const adminLinksInfo = [];

    adminNavLinks.forEach((link) => {
      adminLinksInfo.push({
        href: link.getAttribute("href"),
        page: link.dataset.page,
        parentLi: link.closest(".list"),
      });
    });

    const matchingAdminLink = adminLinksInfo.find(
      (linkInfo) => linkInfo.href === currentURL
    );

    if (matchingAdminLink) {
      adminLinksInfo.forEach((linkInfo) => {
        linkInfo.parentLi.classList.remove("active");
      });
      matchingAdminLink.parentLi.classList.add("active");
      console.log(`  ✓ Admin-Sidebar: "${matchingAdminLink.page}" aktiv`);
    } else {
      if (adminLinksInfo.length > 0) {
        adminLinksInfo.forEach((linkInfo) =>
          linkInfo.parentLi.classList.remove("active")
        );
        adminLinksInfo[0].parentLi.classList.add("active");
      }
    }
  }

  // ========================================
  // FUNKTION: Admin Event Listener installieren
  // WICHTIG: Diese Funktion wird jedes Mal aufgerufen!
  // ========================================
  function installAdminEventListeners() {
    console.log("\n→ Installiere Admin Event Listeners");

    const adminNavLinks = document.querySelectorAll(
      "#navigation-admin .nav-link-admin"
    );

    if (adminNavLinks.length === 0) {
      console.log("  ✗ Keine Admin-Links gefunden");
      return;
    }

    adminNavLinks.forEach((link) => {
      const linkText = link.querySelector(".list_element")?.textContent.trim();

      // Markiere Link als "bereits behandelt"
      if (link.dataset.listenerInstalled === "true") {
        return;
      }

      link.dataset.listenerInstalled = "true";

      link.addEventListener("click", function (event) {
        // console.log(`\n🖱️ Admin-Klick: ${linkText}`);

        if (
          event.ctrlKey ||
          event.metaKey ||
          event.shiftKey ||
          event.button !== 0
        ) {
          // console.log("  → Spezialklick, Browser übernimmt");
          return;
        }

        event.preventDefault();
        // console.log("  ✓ preventDefault() - Admin-Seite lädt NICHT neu");

        const url = this.getAttribute("href");
        const page = this.dataset.page;

        loadAdminContentDynamically(url, page);
        history.pushState({ page: page, url: url, isAdmin: true }, "", url);
        console.log(`  ✓ Admin-URL aktualisiert: ${url}`);
      });

      console.log(`  ✓ ${linkText} - Event Listener installiert`);
    });
  }

  // ========================================
  // FUNKTION: Dynamisches Laden (Normal)
  // ========================================
  async function loadContentDynamically(url, page) {
    console.log(`\n→ Lade dynamisch: ${page}`);

    const contentArea = document.querySelector(".app-content");

    if (!contentArea) {
      window.location.href = url;
      return;
    }

    try {
      const response = await fetch(url, {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const html = await response.text();
      contentArea.innerHTML = html;

      const navLinks = document.querySelectorAll("#navigation .nav-link");
      navLinks.forEach((link) => {
        const parentLi = link.closest(".list");
        if (link.dataset.page === page) {
          parentLi.classList.add("active");
        } else {
          parentLi.classList.remove("active");
        }
      });

      console.log(`✓ ${page} geladen`);
    } catch (error) {
      console.error("Fehler beim Laden:", error);
      window.location.href = url;
    }
  }

  // ========================================
  // FUNKTION: Dynamisches Laden (Admin)
  // ========================================
  async function loadAdminContentDynamically(url, page) {
    // console.log(`\n→ Lade Admin-Content dynamisch: ${page}`);
    const contentArea = document.getElementById("admin-content-area");

    if (!contentArea) {
      console.log("✗ Kein admin-content-area gefunden");
      window.location.href = url;
      return;
    }

    try {
      const response = await fetch(url, {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const html = await response.text();
      contentArea.innerHTML = html;

      const adminNavLinks = document.querySelectorAll(
        "#navigation-admin .nav-link-admin"
      );
      adminNavLinks.forEach((link) => {
        const parentLi = link.closest(".list");
        if (link.dataset.page === page) {
          parentLi.classList.add("active");
        } else {
          parentLi.classList.remove("active");
        }
      });

      // console.log(`✓ Admin-Content ${page} geladen`);
    } catch (error) {
      console.error("Fehler beim Laden:", error);
      window.location.href = url;
    }
  }

  // ========================================
  // BEIM LADEN: Aktiven Link setzen
  // ========================================
  if (!window.location.pathname.includes("/app_settings")) {
    // console.log("→ Normale Seite erkannt");
    setActiveLinkByURL();
  } else {
    // console.log("→ Admin-Bereich erkannt");
    setAdminActiveLinks();
    // WICHTIG: Event Listeners für Admin installieren
    installAdminEventListeners();
  }

  // ========================================
  // Event Listener: Hauptnavigation
  // ========================================
  const navLinks = document.querySelectorAll("#navigation .nav-link");

  navLinks.forEach((link) => {
    link.addEventListener("click", function (event) {
      if (
        event.ctrlKey ||
        event.metaKey ||
        event.shiftKey ||
        event.button !== 0
      ) {
        return;
      }

      event.preventDefault();

      const url = this.getAttribute("href");
      const page = this.dataset.page;

      if (page === "app_settings") {
        console.log("  → Admin-Seite, normale Navigation");
        window.location.href = url;
        return;
      }

      loadContentDynamically(url, page);
      history.pushState({ page: page, url: url, isAdmin: false }, "", url);
    });
  });

  // ========================================
  // Zurück/Vor Button Support
  // ========================================
  window.addEventListener("popstate", function (event) {
    // console.log("\n← Zurück/Vor Button");

    if (event.state && event.state.page && event.state.url) {
      if (event.state.isAdmin) {
        // console.log("  → Admin-Seite wird geladen");
        loadAdminContentDynamically(event.state.url, event.state.page);
      } else {
        // console.log("  → Normale Seite wird geladen");
        loadContentDynamically(event.state.url, event.state.page);
      }
    } else {
      window.location.reload();
    }
  });

  console.log("\n=== Initialisierung abgeschlossen ===\n");
});
