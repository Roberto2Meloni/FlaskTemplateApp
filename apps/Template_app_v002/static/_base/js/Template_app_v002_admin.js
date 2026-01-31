/**
 * App Admin Functions
 * Dynamisch - Config, Sockets, Tasks, Logs
 */

(function () {
  "use strict";

  // App-Name aus URL
  const APP_NAME = window.location.pathname.split("/")[1] || "app";
  const API_BASE = `/${APP_NAME}/admin`;

  console.log(`📋 ${APP_NAME} Admin Functions geladen`);

  // ========================================
  // UTILITIES
  // ========================================

  function showToast(message, type = "info") {
    const toast =
      document.getElementById("statusMessage") ||
      document.getElementById("toast-notification");

    if (!toast) {
      console.warn("Toast-Element nicht gefunden");
      return;
    }

    const icons = {
      success: "check-circle",
      error: "exclamation-circle",
      info: "info-circle",
    };

    toast.innerHTML = `<i class="bi bi-${icons[type]}"></i>${message}`;
    toast.className = `status-message ${type}`;
    toast.style.display = "flex";

    setTimeout(() => {
      toast.style.display = "none";
    }, 3000);
  }

  // ========================================
  // CONFIG FUNCTIONS
  // ========================================

  function initConfigForm() {
    const form = document.getElementById("configForm");
    if (!form) return;

    const resetBtn = document.getElementById("resetBtn");
    const saveBtn = document.getElementById("saveBtn");

    // Store original values
    const originalValues = {};
    form.querySelectorAll("input:not([readonly])").forEach((input) => {
      originalValues[input.id] =
        input.type === "checkbox" ? input.checked : input.value;
    });

    // Reset
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        Object.keys(originalValues).forEach((id) => {
          const input = document.getElementById(id);
          if (input) {
            if (input.type === "checkbox") {
              input.checked = originalValues[id];
            } else {
              input.value = originalValues[id];
            }
          }
        });
        showToast("Änderungen zurückgesetzt", "success");
      });
    }

    // Submit
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      saveBtn.disabled = true;
      saveBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Speichert...';

      try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });

        const result = await response.json();

        if (result.success) {
          showToast("Konfiguration erfolgreich gespeichert!", "success");

          // Update original values
          form.querySelectorAll("input:not([readonly])").forEach((input) => {
            originalValues[input.id] =
              input.type === "checkbox" ? input.checked : input.value;
          });
        } else {
          showToast(
            "Fehler: " + (result.message || "Unbekannter Fehler"),
            "error",
          );
        }
      } catch (error) {
        showToast("Fehler beim Speichern: " + error.message, "error");
      } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="bi bi-save"></i> Speichern';
      }
    });
  }

  // ========================================
  // SOCKET FUNCTIONS
  // ========================================

  async function refreshSocketList() {
    const refreshBtn = document.getElementById("refreshBtn");
    if (!refreshBtn) return;

    refreshBtn.disabled = true;
    const originalHTML = refreshBtn.innerHTML;
    refreshBtn.innerHTML =
      '<i class="bi bi-arrow-clockwise loading"></i> Lädt...';

    try {
      const response = await fetch(`${API_BASE}/api_get_sockets`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      const result = await response.json();

      if (result.success) {
        updateSocketTable(result.sockets);

        const totalElement = document.getElementById("totalConnections");
        if (totalElement) totalElement.textContent = result.total;

        showToast("Socket-Liste aktualisiert", "success");
      } else {
        showToast("Fehler: " + result.message, "error");
      }
    } catch (error) {
      showToast("Fehler beim Aktualisieren: " + error.message, "error");
    } finally {
      refreshBtn.disabled = false;
      refreshBtn.innerHTML = originalHTML;
    }
  }

  async function disconnectAllSockets() {
    if (!confirm("Möchten Sie wirklich ALLE Socket-Verbindungen trennen?")) {
      return;
    }

    const btn = document.getElementById("disconnectAllBtn");
    if (!btn) return;

    btn.disabled = true;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Trenne...';

    try {
      const response = await fetch(`${API_BASE}/api_disconnect_all_sockets`, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      const result = await response.json();

      if (result.success) {
        showToast(result.message, "success");
        setTimeout(() => refreshSocketList(), 1000);
      } else {
        showToast("Fehler: " + result.message, "error");
      }
    } catch (error) {
      showToast("Fehler: " + error.message, "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalHTML;
    }
  }

  async function disconnectSocket(sid, btnElement) {
    if (!confirm("Diese Socket-Verbindung trennen?")) {
      return;
    }

    const row = document.querySelector(`tr[data-sid="${sid}"]`);

    btnElement.disabled = true;
    const originalHTML = btnElement.innerHTML;
    btnElement.innerHTML = '<i class="bi bi-hourglass-split"></i>';

    try {
      const response = await fetch(`${API_BASE}/api_disconnect_socket/${sid}`, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      const result = await response.json();

      if (result.success) {
        showToast("Verbindung getrennt", "success");

        if (row) {
          row.style.opacity = "0";
          setTimeout(() => {
            row.remove();

            const totalElement = document.getElementById("totalConnections");
            if (totalElement) {
              const currentTotal = parseInt(totalElement.textContent);
              totalElement.textContent = currentTotal - 1;
            }

            // Empty State check
            if (
              document.querySelectorAll("#socketsTableBody tr").length === 0
            ) {
              setTimeout(() => refreshSocketList(), 500);
            }
          }, 300);
        }
      } else {
        showToast("Fehler: " + result.message, "error");
        btnElement.disabled = false;
        btnElement.innerHTML = originalHTML;
      }
    } catch (error) {
      showToast("Fehler: " + error.message, "error");
      btnElement.disabled = false;
      btnElement.innerHTML = originalHTML;
    }
  }

  function updateSocketTable(sockets) {
    const tbody = document.getElementById("socketsTableBody");
    const container = document.querySelector(".sockets-content");

    if (sockets.length === 0) {
      if (container) {
        container.innerHTML = `
          <div class="empty-state">
            <i class="bi bi-plug"></i>
            <h5>Keine aktiven Verbindungen</h5>
            <p>Aktuell sind keine Socket-Verbindungen für diese App aktiv.</p>
          </div>
        `;
      }
      return;
    }

    if (!tbody) {
      // Erstelle Tabelle
      if (container) {
        container.innerHTML = `
          <div class="sockets-table-wrapper">
            <table class="sockets-table">
              <thead>
                <tr>
                  <th><i class="bi bi-person"></i> Benutzer</th>
                  <th><i class="bi bi-fingerprint"></i> Socket ID</th>
                  <th><i class="bi bi-clock"></i> Verbunden seit</th>
                  <th><i class="bi bi-gear"></i> Aktionen</th>
                </tr>
              </thead>
              <tbody id="socketsTableBody"></tbody>
            </table>
          </div>
        `;
      }
    }

    const newTbody = document.getElementById("socketsTableBody");
    if (newTbody) {
      newTbody.innerHTML = generateSocketRows(sockets);
    }
  }

  function generateSocketRows(sockets) {
    return sockets
      .map(
        (socket) => `
      <tr data-sid="${socket.sid}">
        <td>
          <div class="user-info">
            <i class="bi bi-person-circle user-icon"></i>
            <span class="username">${socket.username}</span>
            ${
              socket.user_id
                ? '<span class="user-badge authenticated">Auth</span>'
                : '<span class="user-badge guest">Gast</span>'
            }
          </div>
        </td>
        <td><code class="socket-id">${socket.sid.substring(0, 16)}...</code></td>
        <td><span class="timestamp">${socket.connected_at}</span></td>
        <td>
          <button 
            class="btn-icon btn-disconnect" 
            onclick="AppAdmin.disconnectSocket('${socket.sid}', this)"
            title="Verbindung trennen">
            <i class="bi bi-x-circle"></i>
          </button>
        </td>
      </tr>
    `,
      )
      .join("");
  }

  function initSocketAdmin() {
    const refreshBtn = document.getElementById("refreshBtn");
    const disconnectAllBtn = document.getElementById("disconnectAllBtn");

    if (refreshBtn) {
      refreshBtn.addEventListener("click", refreshSocketList);
    }

    if (disconnectAllBtn) {
      disconnectAllBtn.addEventListener("click", disconnectAllSockets);
    }

    // Auto-refresh (30 Sekunden)
    const socketsContainer = document.querySelector(".sockets-container");
    if (socketsContainer) {
      setInterval(() => {
        if (!document.hidden) {
          refreshSocketList();
        }
      }, 30000);
    }
  }

  // ========================================
  // TASK FUNCTIONS
  // ========================================

  async function pauseTask(taskId) {
    try {
      const response = await fetch(`${API_BASE}/api_pause_task/${taskId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      const data = await response.json();

      if (data.success) {
        showToast(data.message, "success");
        updateTaskUI(taskId, false);
      } else {
        showToast(data.message, "error");
      }
    } catch (error) {
      showToast("Fehler beim Pausieren des Tasks", "error");
    }
  }

  async function resumeTask(taskId) {
    try {
      const response = await fetch(`${API_BASE}/api_resume_task/${taskId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      const data = await response.json();

      if (data.success) {
        showToast(data.message, "success");
        updateTaskUI(taskId, true);
      } else {
        showToast(data.message, "error");
      }
    } catch (error) {
      showToast("Fehler beim Fortsetzen des Tasks", "error");
    }
  }

  async function runTask(taskId) {
    try {
      showToast("Task wird ausgeführt...", "info");

      const response = await fetch(`${API_BASE}/api_run_task/${taskId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      const data = await response.json();

      if (data.success) {
        showToast(data.message, "success");
      } else {
        showToast(data.message, "error");
      }
    } catch (error) {
      showToast("Fehler beim Ausführen des Tasks", "error");
    }
  }

  function updateTaskUI(taskId, isActive) {
    const row = document.querySelector(`tr[data-task-id="${taskId}"]`);
    if (!row) return;

    const statusCell = row.querySelector(".task-status");
    if (statusCell) {
      statusCell.innerHTML = isActive
        ? '<span class="status-badge status-active"><i class="bi bi-check-circle-fill"></i> Aktiv</span>'
        : '<span class="status-badge status-paused"><i class="bi bi-pause-circle-fill"></i> Pausiert</span>';
    }

    const btnPause = row.querySelector(".btn-pause");
    const btnResume = row.querySelector(".btn-resume");

    if (btnPause) btnPause.style.display = isActive ? "inline-block" : "none";
    if (btnResume) btnResume.style.display = isActive ? "none" : "inline-block";
  }

  async function refreshTasks() {
    showToast("Tasks werden aktualisiert...", "info");
    window.location.reload();
  }

  function initTaskManagement() {
    const taskTable = document.querySelector(".task-table");
    if (!taskTable) return;

    // Auto-refresh (30 Sekunden)
    setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/api_get_tasks`);
        const data = await response.json();

        if (data.success) {
          data.tasks.forEach((task) => {
            const row = document.querySelector(`tr[data-task-id="${task.id}"]`);
            if (row) {
              const nextRunCell = row.querySelector(".task-next-run");
              if (nextRunCell) nextRunCell.textContent = task.next_run;
            }
          });
        }
      } catch (error) {
        console.error("Auto-refresh error:", error);
      }
    }, 30000);
  }

  // ========================================
  // LOG FUNCTIONS
  // ========================================

  function applyLogFilters() {
    const level = document.getElementById("level-filter")?.value;
    const limit = document.getElementById("limit-filter")?.value;
    const search = document.getElementById("search-filter")?.value;

    const params = new URLSearchParams();
    if (level) params.append("level", level);
    if (limit) params.append("limit", limit);
    if (search) params.append("search", search);

    window.location.href = `${window.location.pathname}?${params.toString()}`;
  }

  function resetLogFilters() {
    window.location.href = window.location.pathname;
  }

  function quickLogFilter(level) {
    const levelFilter = document.getElementById("level-filter");
    if (levelFilter) {
      levelFilter.value = level;
      applyLogFilters();
    }
  }

  function downloadLogs() {
    showToast("Logs werden vorbereitet...", "info");

    const logRows = document.querySelectorAll(".log-row");
    let content = "";

    logRows.forEach((row) => {
      const timestamp = row.querySelector(".log-timestamp")?.textContent || "";
      const level = row.querySelector(".level-badge")?.textContent.trim() || "";
      const logger = row.querySelector(".log-logger")?.textContent || "";
      const message = row.querySelector(".log-message")?.textContent || "";

      content += `${timestamp} - ${logger} - ${level} - ${message}\n`;
    });

    const blob = new Blob([content], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${APP_NAME}_logs_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    showToast("Logs heruntergeladen!", "success");
  }

  function initLogViewer() {
    const searchFilter = document.getElementById("search-filter");
    if (searchFilter) {
      searchFilter.addEventListener("keypress", function (e) {
        if (e.key === "Enter") applyLogFilters();
      });
    }
  }

  // ========================================
  // INITIALISIERUNG
  // ========================================

  document.addEventListener("DOMContentLoaded", function () {
    console.log(`🏁 ${APP_NAME}: Admin Functions initialisiert`);

    // Init basierend auf Seite
    initConfigForm();
    initSocketAdmin();
    initTaskManagement();
    initLogViewer();

    console.log("✓ Admin Functions bereit");
  });

  // ========================================
  // GLOBAL EXPORT
  // ========================================

  window.AppAdmin = {
    // Config
    showToast,

    // Sockets
    refreshSocketList,
    disconnectAllSockets,
    disconnectSocket,

    // Tasks
    pauseTask,
    resumeTask,
    runTask,
    refreshTasks,

    // Logs
    applyLogFilters,
    resetLogFilters,
    quickLogFilter,
    downloadLogs,
  };
})();
