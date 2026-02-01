/**
 * Template_app_v002 - Log Viewer JavaScript (HIERARCHISCH)
 * Mit hierarchischem Log-Level Filter
 */

(function () {
  "use strict";

  console.log("📋 Log-Viewer JavaScript geladen (Hierarchisch)");

  // ========================================
  // LOG-LEVEL HIERARCHIE
  // ========================================

  const LOG_LEVELS = {
    CRITICAL: 50,
    ERROR: 40,
    WARNING: 30,
    INFO: 20,
    DEBUG: 10,
  };

  // ========================================
  // FILTER FUNCTIONS
  // ========================================

  /**
   * Wendet alle Filter an und lädt die Seite neu
   */
  window.applyFilters = function () {
    const level = document.getElementById("level-filter")?.value || "";
    const limit = document.getElementById("limit-filter")?.value || "500";
    const search = document.getElementById("search-filter")?.value || "";

    console.log("🔍 Filter anwenden:", { level, limit, search });

    const params = new URLSearchParams();

    if (level) params.append("level", level);
    if (limit) params.append("limit", limit);
    if (search) params.append("search", search);

    const url = `${window.location.pathname}?${params.toString()}`;
    console.log("📍 Neue URL:", url);
    window.location.href = url;
  };

  /**
   * Filtert Logs hierarchisch basierend auf Level
   */
  function filterLogsHierarchically(selectedLevel) {
    if (!selectedLevel) {
      // Alle anzeigen
      showAllLogs();
      return;
    }

    const selectedLevelValue = LOG_LEVELS[selectedLevel];
    console.log(
      `🔽 Filter hierarchisch: ${selectedLevel} (>= ${selectedLevelValue})`,
    );

    const logRows = document.querySelectorAll(".log-row");
    let visibleCount = 0;

    logRows.forEach((row) => {
      // Finde Level aus der Zeile
      const levelBadge = row.querySelector(".level-badge");
      if (!levelBadge) return;

      const rowLevel = levelBadge.textContent.trim();
      const rowLevelValue = LOG_LEVELS[rowLevel] || 0;

      // Zeige wenn Level >= selectedLevel
      if (rowLevelValue >= selectedLevelValue) {
        row.style.display = "";
        visibleCount++;
      } else {
        row.style.display = "none";
      }
    });

    console.log(`✓ ${visibleCount} von ${logRows.length} Logs sichtbar`);
    updateEmptyState(visibleCount);
  }

  /**
   * Zeigt alle Logs
   */
  function showAllLogs() {
    console.log("👁️ Zeige alle Logs");
    const logRows = document.querySelectorAll(".log-row");
    logRows.forEach((row) => {
      row.style.display = "";
    });
    updateEmptyState(logRows.length);
  }

  /**
   * Aktualisiert "Keine Logs" Nachricht
   */
  function updateEmptyState(visibleCount) {
    const logDisplay = document.querySelector(".log-display");
    const noLogsMessage = document.querySelector(".no-logs-message");
    const logTableContainer = document.querySelector(".log-table-container");

    if (visibleCount === 0) {
      // Zeige "Keine Logs"
      if (logTableContainer) logTableContainer.style.display = "none";
      if (!noLogsMessage) {
        const emptyDiv = document.createElement("div");
        emptyDiv.className = "no-logs-message";
        emptyDiv.innerHTML = `
          <i class="bi bi-inbox"></i>
          <p>Keine Logs gefunden</p>
          <small>Mit diesem Filter wurden keine Logs gefunden.</small>
        `;
        logDisplay.appendChild(emptyDiv);
      }
    } else {
      // Verstecke "Keine Logs"
      if (logTableContainer) logTableContainer.style.display = "";
      if (noLogsMessage) noLogsMessage.remove();
    }
  }

  /**
   * Filtert Logs basierend auf Suchtext
   */
  function filterLogsBySearch(searchText) {
    if (!searchText) {
      showAllLogs();
      return;
    }

    console.log(`🔍 Suche nach: "${searchText}"`);
    const logRows = document.querySelectorAll(".log-row");
    let visibleCount = 0;

    logRows.forEach((row) => {
      const rowText = row.textContent.toLowerCase();
      const matches = rowText.includes(searchText.toLowerCase());

      if (matches) {
        row.style.display = "";
        visibleCount++;
      } else {
        row.style.display = "none";
      }
    });

    console.log(`✓ ${visibleCount} von ${logRows.length} Logs gefunden`);
    updateEmptyState(visibleCount);
  }

  /**
   * Kombinierter Filter (Level + Suche)
   */
  function applyClientSideFilters() {
    const levelFilter = document.getElementById("level-filter");
    const searchFilter = document.getElementById("search-filter");

    const selectedLevel = levelFilter?.value || "";
    const searchText = searchFilter?.value || "";

    console.log("🎯 Client-seitiger Filter:", {
      level: selectedLevel,
      search: searchText,
    });

    const logRows = document.querySelectorAll(".log-row");
    let visibleCount = 0;

    logRows.forEach((row) => {
      let shouldShow = true;

      // Level-Filter (hierarchisch)
      if (selectedLevel) {
        const levelBadge = row.querySelector(".level-badge");
        const rowLevel = levelBadge?.textContent.trim();
        const selectedLevelValue = LOG_LEVELS[selectedLevel];
        const rowLevelValue = LOG_LEVELS[rowLevel] || 0;

        if (rowLevelValue < selectedLevelValue) {
          shouldShow = false;
        }
      }

      // Such-Filter
      if (searchText && shouldShow) {
        const rowText = row.textContent.toLowerCase();
        if (!rowText.includes(searchText.toLowerCase())) {
          shouldShow = false;
        }
      }

      row.style.display = shouldShow ? "" : "none";
      if (shouldShow) visibleCount++;
    });

    console.log(`✓ ${visibleCount} von ${logRows.length} Logs sichtbar`);
    updateEmptyState(visibleCount);
  }

  /**
   * Live-Filter beim Ändern des Dropdowns
   */
  function setupLiveFiltering() {
    const levelFilter = document.getElementById("level-filter");
    const searchFilter = document.getElementById("search-filter");

    if (levelFilter) {
      levelFilter.addEventListener("change", function () {
        console.log("🔄 Level-Filter geändert:", this.value);
        applyClientSideFilters();
      });
      console.log("✓ Live-Filtering für Level aktiviert");
    }

    if (searchFilter) {
      // Live-Suche beim Tippen
      searchFilter.addEventListener("input", function () {
        applyClientSideFilters();
      });
      console.log("✓ Live-Filtering für Suche aktiviert");
    }
  }

  /**
   * Setzt alle Filter zurück
   */
  window.resetFilters = function () {
    console.log("🔄 Filter zurücksetzen");

    const levelFilter = document.getElementById("level-filter");
    const limitFilter = document.getElementById("limit-filter");
    const searchFilter = document.getElementById("search-filter");

    if (levelFilter) levelFilter.value = "";
    if (limitFilter) limitFilter.value = "500";
    if (searchFilter) searchFilter.value = "";

    // Zeige alle Logs wieder
    showAllLogs();
  };

  /**
   * Schnellfilter für bestimmtes Log-Level
   */
  window.quickFilter = function (level) {
    console.log("⚡ Schnellfilter:", level);

    const levelFilter = document.getElementById("level-filter");
    if (levelFilter) {
      levelFilter.value = level;
      applyClientSideFilters();
    }
  };

  // ========================================
  // TOAST NOTIFICATIONS
  // ========================================

  window.showLogToast = function (message, type = "info") {
    const toast = document.getElementById("log-toast-notification");

    if (!toast) {
      console.warn("⚠️ Toast-Element nicht gefunden");
      return;
    }

    const icons = {
      info: '<i class="bi bi-info-circle-fill"></i>',
      success: '<i class="bi bi-check-circle-fill"></i>',
      error: '<i class="bi bi-exclamation-triangle-fill"></i>',
      warning: '<i class="bi bi-exclamation-circle-fill"></i>',
    };

    toast.innerHTML = `${icons[type] || ""} ${message}`;
    toast.className = `toast-notification toast-${type}`;
    toast.style.display = "flex";

    setTimeout(() => {
      toast.style.display = "none";
    }, 3000);
  };

  // ========================================
  // KEYBOARD SHORTCUTS
  // ========================================

  function setupKeyboardShortcuts() {
    const searchFilter = document.getElementById("search-filter");

    if (searchFilter) {
      searchFilter.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
          console.log("⌨️ Enter gedrückt");
          applyClientSideFilters();
        }
      });
      console.log("✓ Keyboard Shortcuts aktiviert");
    }
  }

  // ========================================
  // ROW HIGHLIGHTING
  // ========================================

  function setupRowHighlighting() {
    const logRows = document.querySelectorAll(".log-row");

    logRows.forEach((row) => {
      row.addEventListener("click", function () {
        document.querySelectorAll(".log-row.highlighted").forEach((r) => {
          r.classList.remove("highlighted");
        });
        this.classList.add("highlighted");
      });
    });

    if (logRows.length > 0) {
      console.log(`✓ Row Highlighting für ${logRows.length} Zeilen aktiviert`);
    }
  }

  // ========================================
  // COPY TO CLIPBOARD
  // ========================================

  window.copyLogMessage = function (element) {
    const message = element.textContent;

    navigator.clipboard
      .writeText(message)
      .then(() => {
        window.showLogToast("Nachricht kopiert!", "success");
        console.log("📋 Kopiert:", message.substring(0, 50) + "...");
      })
      .catch((err) => {
        window.showLogToast("Fehler beim Kopieren", "error");
        console.error("❌ Clipboard Fehler:", err);
      });
  };

  // ========================================
  // STATISTICS
  // ========================================

  function showLogStatistics() {
    const logRows = document.querySelectorAll(".log-row");
    const levels = {};

    logRows.forEach((row) => {
      const levelBadge = row.querySelector(".level-badge");
      if (levelBadge) {
        const level = levelBadge.textContent.trim();
        levels[level] = (levels[level] || 0) + 1;
      }
    });

    console.log("📊 Log-Statistik (Hierarchie):");
    console.log("CRITICAL (50):", levels.CRITICAL || 0);
    console.log("ERROR    (40):", levels.ERROR || 0);
    console.log("WARNING  (30):", levels.WARNING || 0);
    console.log("INFO     (20):", levels.INFO || 0);
    console.log("DEBUG    (10):", levels.DEBUG || 0);
    console.log(`📝 Gesamt: ${logRows.length} Logs`);
  }

  // ========================================
  // INITIALIZATION
  // ========================================

  document.addEventListener("DOMContentLoaded", function () {
    console.log("🏁 Log-Viewer wird initialisiert (Hierarchisch)...");

    // Setup Features
    setupLiveFiltering();
    setupKeyboardShortcuts();
    setupRowHighlighting();

    // Show Statistics
    showLogStatistics();

    console.log("✅ Log-Viewer bereit (Hierarchisch)");
    console.log("ℹ️  Level-Filter ist hierarchisch:");
    console.log("   - INFO zeigt: CRITICAL, ERROR, WARNING, INFO");
    console.log("   - WARNING zeigt: CRITICAL, ERROR, WARNING");
    console.log("   - ERROR zeigt: CRITICAL, ERROR");
  });

  // ========================================
  // GLOBAL EXPORT
  // ========================================

  window.LogViewer = {
    applyFilters: applyClientSideFilters,
    resetFilters: window.resetFilters,
    quickFilter: window.quickFilter,
    showToast: window.showLogToast,
    copyLogMessage: window.copyLogMessage,
    showStatistics: showLogStatistics,
  };

  console.log("✅ LogViewer API verfügbar");
})();
