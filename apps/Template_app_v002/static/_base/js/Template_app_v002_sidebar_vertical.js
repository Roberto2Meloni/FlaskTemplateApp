/**
 * App Sidebar Navigation - FIXED
 * Problem: Content wurde nicht angezeigt
 * Lösung: Korrekter Selector für Content-Area
 */

(function () {
  "use strict";

  const APP_NAME = window.location.pathname.split("/")[1] || "app";

  console.log(`=== ${APP_NAME} Sidebar Navigation gestartet ===`);

  // ========================================
  // HAMBURGER MENU
  // ========================================
  function initHamburgerMenu() {
    const hamburgerMenu = document.getElementById("hamburgerMenu");
    const navigation = document.getElementById("navigation");

    if (hamburgerMenu && navigation) {
      hamburgerMenu.addEventListener("click", function () {
        navigation.classList.toggle("collapsed");
        const icon = hamburgerMenu.querySelector("i");
        if (navigation.classList.contains("collapsed")) {
          icon.className = "bi bi-chevron-right";
        } else {
          icon.className = "bi bi-list";
        }
      });
    }
  }

  // ========================================
  // AKTIVEN LINK SETZEN
  // ========================================
  function setActiveLinkByURL() {
    const currentURL = window.location.pathname;
    const navLinks = document.querySelectorAll("#navigation .nav-link");
    const linksInfo = [];

    navLinks.forEach((link) => {
      linksInfo.push({
        href: link.getAttribute("href"),
        page: link.dataset.page,
        parentLi: link.closest(".list"),
      });
    });

    let matchingLink = linksInfo.find((info) => info.href === currentURL);

    if (
      !matchingLink &&
      (currentURL === "/" || currentURL.endsWith(`/${APP_NAME}`))
    ) {
      matchingLink = linksInfo.find((info) => info.page === "dashboard");
    }

    if (matchingLink) {
      linksInfo.forEach((info) => info.parentLi.classList.remove("active"));
      matchingLink.parentLi.classList.add("active");
      console.log(`✓ Aktiv: ${matchingLink.page}`);
    }
  }

  // ========================================
  // ADMIN-BEREICH
  // ========================================
  function setAdminActiveLinks() {
    const currentURL = window.location.pathname;

    const mainNavLinks = document.querySelectorAll("#navigation .nav-link");
    mainNavLinks.forEach((link) => {
      const parentLi = link.closest(".list");
      parentLi.classList.remove("active");

      if (link.dataset.page === "app_settings") {
        parentLi.classList.add("active");
      }
    });

    const adminSidebar = document.getElementById("navigation-admin");
    if (!adminSidebar) return;

    const adminNavLinks = document.querySelectorAll(
      "#navigation-admin .nav-link-admin",
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
      (info) => info.href === currentURL,
    );

    if (matchingAdminLink) {
      adminLinksInfo.forEach((info) =>
        info.parentLi.classList.remove("active"),
      );
      matchingAdminLink.parentLi.classList.add("active");
      console.log(`✓ Admin aktiv: ${matchingAdminLink.page}`);
    } else if (adminLinksInfo.length > 0) {
      adminLinksInfo.forEach((info) =>
        info.parentLi.classList.remove("active"),
      );
      adminLinksInfo[0].parentLi.classList.add("active");
    }
  }

  // ========================================
  // DYNAMISCHES LADEN - FIXED!
  // ========================================
  async function loadContentDynamically(url, page) {
    console.log(`\n→ Lade dynamisch: ${page}`);

    // WICHTIG: Korrekte Content-Area finden!
    // Die Area ist INNERHALB von .main-content
    const contentArea = document.querySelector(".main-content .app-content");

    if (!contentArea) {
      console.error("❌ .app-content nicht gefunden!");
      console.log("Verfügbare Elemente:", {
        mainContent: !!document.querySelector(".main-content"),
        appContent: !!document.querySelector(".app-content"),
      });
      window.location.href = url;
      return;
    }

    try {
      const response = await fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const html = await response.text();

      // WICHTIG: Nur den Content ersetzen, nicht die gesamte Seite!
      contentArea.innerHTML = html;

      // Update aktiven Link
      document.querySelectorAll("#navigation .nav-link").forEach((link) => {
        const parentLi = link.closest(".list");
        if (link.dataset.page === page) {
          parentLi.classList.add("active");
        } else {
          parentLi.classList.remove("active");
        }
      });

      console.log(`✓ Geladen: ${page}`);
    } catch (error) {
      console.error("❌ Fehler beim Laden:", error);
      window.location.href = url;
    }
  }

  async function loadAdminContentDynamically(url, page) {
    console.log(`\n→ Lade Admin-Content: ${page}`);

    const contentArea = document.getElementById("admin-content-area");

    if (!contentArea) {
      console.error("❌ #admin-content-area nicht gefunden!");
      window.location.href = url;
      return;
    }

    try {
      const response = await fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const html = await response.text();
      contentArea.innerHTML = html;

      document
        .querySelectorAll("#navigation-admin .nav-link-admin")
        .forEach((link) => {
          const parentLi = link.closest(".list");
          if (link.dataset.page === page) {
            parentLi.classList.add("active");
          } else {
            parentLi.classList.remove("active");
          }
        });

      console.log(`✓ Admin geladen: ${page}`);
    } catch (error) {
      console.error("❌ Fehler beim Laden:", error);
      window.location.href = url;
    }
  }

  // ========================================
  // EVENT LISTENERS
  // ========================================
  function setupMainNavigation() {
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
          console.log("→ Admin-Seite, normale Navigation");
          window.location.href = url;
          return;
        }

        loadContentDynamically(url, page);
        history.pushState({ page, url, isAdmin: false }, "", url);
      });
    });
  }

  function setupAdminNavigation() {
    const adminNavLinks = document.querySelectorAll(
      "#navigation-admin .nav-link-admin",
    );

    adminNavLinks.forEach((link) => {
      if (link.dataset.listenerInstalled === "true") return;
      link.dataset.listenerInstalled = "true";

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

        loadAdminContentDynamically(url, page);
        history.pushState({ page, url, isAdmin: true }, "", url);
      });
    });
  }

  // ========================================
  // BROWSER NAVIGATION
  // ========================================
  function setupBrowserNavigation() {
    window.addEventListener("popstate", function (event) {
      console.log("\n← Zurück/Vor Button");

      if (event.state && event.state.page && event.state.url) {
        if (event.state.isAdmin) {
          loadAdminContentDynamically(event.state.url, event.state.page);
        } else {
          loadContentDynamically(event.state.url, event.state.page);
        }
      } else {
        window.location.reload();
      }
    });
  }

  // ========================================
  // INITIALISIERUNG
  // ========================================
  document.addEventListener("DOMContentLoaded", function () {
    console.log(`🏁 ${APP_NAME}: Sidebar initialisiert`);

    // Hamburger Menu
    initHamburgerMenu();

    // Aktiven Link setzen
    if (window.location.pathname.includes("/app_settings")) {
      setAdminActiveLinks();
      setupAdminNavigation();
    } else {
      setActiveLinkByURL();
    }

    // Event Listeners
    setupMainNavigation();
    setupBrowserNavigation();

    console.log("✓ Sidebar Navigation bereit");
  });
})();
