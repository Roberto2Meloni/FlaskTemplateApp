/**
 * Template_app_v002 - Log Viewer JavaScript (HIERARCHISCH)
 * Mit hierarchischem Log-Level Filter (rein client-seitig)
 */

// ========================================
// AUTO-REFRESH STATE
// ========================================

let autoRefreshInterval = null;
const AUTO_REFRESH_MS = 5000; // 5 Sekunden

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
   * Kombinierter Filter (Level + Suche)
   * Filtert nur im DOM - kein Server-Request
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
   * Aktualisiert "Keine Logs" Nachricht
   */
  function updateEmptyState(visibleCount) {
    const logDisplay = document.querySelector(".log-display");
    const noLogsMessage = document.querySelector(".no-logs-message");
    const logTableContainer = document.querySelector(".log-table-container");

    if (visibleCount === 0) {
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
      if (logTableContainer) logTableContainer.style.display = "";
      if (noLogsMessage) noLogsMessage.remove();
    }
  }

  // ========================================
  // REFRESH LOGS (API Call)
  // ========================================
  // ========================================
  // AUTO-REFRESH TOGGLE
  // ========================================

  function toggleAutoRefresh() {
    const button = document.getElementById("auto-refresh-btn");
    const icon = button?.querySelector("i");
    const statusText = button?.querySelector("span");

    if (autoRefreshInterval) {
      // --- AUS ---
      clearInterval(autoRefreshInterval);
      autoRefreshInterval = null;

      if (icon) icon.className = "bi bi-play-circle";
      if (statusText) statusText.textContent = "Aus";
      if (button) button.classList.remove("auto-refresh-active");

      console.log("⏸️ Auto-Refresh gestoppt");
      window.showLogToast("Auto-Refresh gestoppt", "info");
    } else {
      // --- EIN ---
      refreshLogs(); // Sofort einmal laden
      autoRefreshInterval = setInterval(refreshLogs, AUTO_REFRESH_MS);

      if (icon) icon.className = "bi bi-pause-circle";
      if (statusText) statusText.textContent = "Ein";
      if (button) button.classList.add("auto-refresh-active");

      console.log("▶️ Auto-Refresh gestartet (alle 5s)");
      window.showLogToast("Auto-Refresh aktiv (5s)", "success");
    }
  }

  async function refreshLogs() {
    const limitFilter = document.getElementById("limit-filter");
    const limit = limitFilter?.value || "500";

    console.log("🔄 Logs neu laden, Limit:", limit);

    // URL mit Limit-Parameter bauen
    const url = `${API_GET_LOGS}?limit=${limit}`;

    try {
      const response = await fetch(url, {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.message || "Unbekannter Fehler");
      }

      console.log(`✓ ${data.count} Logs empfangen`);

      // Tabelle neu aufbauen
      rebuildLogTable(data.logs);

      // Statistik-Anzeige aktualisieren
      updateLogStats(data);

      // Client-Filter erneut anwenden
      applyClientSideFilters();

      // Row-Highlighting neu installieren
      setupRowHighlighting();

      window.showLogToast(`${data.count} Logs geladen`, "success");
    } catch (error) {
      console.error("❌ Fehler beim Laden:", error);
      window.showLogToast("Fehler beim Laden der Logs", "error");
    }
  }

  /**
   * Baut die Log-Tabelle mit neuen Daten neu auf
   */
  function rebuildLogTable(logs) {
    const tbody = document.querySelector(".log-table tbody");

    if (!tbody) {
      console.error("❌ tbody nicht gefunden");
      return;
    }

    // Leeren
    tbody.innerHTML = "";

    // Neue Zeilen bauen
    logs.forEach((log) => {
      const level = log.level || "UNKNOWN";
      const levelLower = level.toLowerCase();

      // Icon je nach Level
      let icon = '<i class="bi bi-question-circle-fill"></i>';
      if (level === "ERROR" || level === "CRITICAL") {
        icon = '<i class="bi bi-exclamation-triangle-fill"></i>';
      } else if (level === "WARNING") {
        icon = '<i class="bi bi-exclamation-circle-fill"></i>';
      } else if (level === "INFO") {
        icon = '<i class="bi bi-info-circle-fill"></i>';
      } else if (level === "DEBUG") {
        icon = '<i class="bi bi-bug-fill"></i>';
      }

      const tr = document.createElement("tr");
      tr.className = `log-row log-level-${levelLower}`;
      tr.innerHTML = `
        <td class="log-timestamp">${log.timestamp || "N/A"}</td>
        <td class="log-level">
          <span class="level-badge level-${levelLower}">
            ${icon} ${level}
          </span>
        </td>
        <td class="log-logger">${log.logger || "N/A"}</td>
        <td class="log-message" onclick="copyLogMessage(this)" 
            style="cursor: pointer" title="Klicken zum Kopieren">
          ${log.message || "Keine Nachricht"}
        </td>
      `;

      tbody.appendChild(tr);
    });

    console.log(`✓ ${logs.length} Zeilen in Tabelle eingefügt`);
  }

  /**
   * Aktualisiert die Statistik-Anzeige im Header
   */
  function updateLogStats(data) {
    const filteredLines = document.querySelector(
      ".stat-item:nth-child(2) .stat-value",
    );
    if (filteredLines) {
      filteredLines.textContent = data.filtered_lines || data.count;
    }
  }

  // ========================================
  // RESET & QUICK FILTER
  // ========================================

  window.resetFilters = function () {
    console.log("🔄 Filter zurücksetzen");

    const levelFilter = document.getElementById("level-filter");
    const limitFilter = document.getElementById("limit-filter");
    const searchFilter = document.getElementById("search-filter");

    if (levelFilter) levelFilter.value = "";
    if (limitFilter) limitFilter.value = "500";
    if (searchFilter) searchFilter.value = "";

    applyClientSideFilters();
  };

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

    setupKeyboardShortcuts();
    setupRowHighlighting();
    showLogStatistics();

    // Auto-Refresh standardmässig starten
    toggleAutoRefresh();

    console.log("✅ Log-Viewer bereit (Hierarchisch)");
  });

  function initLogViewer() {
    const searchFilter = document.getElementById("search-filter");
    if (searchFilter) {
      searchFilter.addEventListener("keypress", function (e) {
        if (e.key === "Enter") applyLogFilters();
      });
    }
  }

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
    refreshLogs: refreshLogs,
    toggleAutoRefresh: toggleAutoRefresh,
  };

  console.log("✅ LogViewer API verfügbar");
})();
