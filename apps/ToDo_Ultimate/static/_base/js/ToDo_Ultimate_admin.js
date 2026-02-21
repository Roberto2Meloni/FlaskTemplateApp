/**
 * ToDo_Ultimate - Admin Core
 *
 * Zuständig NUR für:
 * - Toast Notifications (global)
 * - Socket-Tabelle (Refresh, Disconnect, Accordion)
 *
 * Ausgelagert:
 * - Socket Verbindung / Ping / Pong → socketio.js
 * - Config                          → admin_config.js
 * - Tasks                           → admin_task.js
 * - Logs                            → admin_logview.js
 */

(function () {
  "use strict";

  const APP_NAME = window.location.pathname.split("/")[1] || "app";
  const API_BASE = `/${APP_NAME}/admin`;

  console.log(`📋 ${APP_NAME} Admin Core geladen`);

  // ========================================
  // TOAST (Global)
  // ========================================

  function showToast(message, type = "info") {
    const toast = document.getElementById("toast-notification");
    if (!toast) {
      console.warn("Toast nicht gefunden");
      return;
    }

    const icons = {
      success:
        '<i class="bi bi-check-circle-fill" style="color:#28a745;font-size:20px;"></i>',
      error:
        '<i class="bi bi-x-circle-fill" style="color:#dc3545;font-size:20px;"></i>',
      info: '<i class="bi bi-info-circle-fill" style="color:#3498db;font-size:20px;"></i>',
    };
    toast.innerHTML = `${icons[type]}<span>${message}</span>`;
    toast.className = `toast-notification ${type} show`;
    setTimeout(() => toast.classList.remove("show"), 3000);
  }

  // ========================================
  // ACCORDION
  // ========================================

  function initSocketTestAccordion() {
    const header = document.querySelector(".test-card-header");
    const body = document.getElementById("testSectionBody");
    const icon = document.getElementById("testSectionChevron");

    if (!header || !body) return;

    body.style.display = "none";
    header.style.cursor = "pointer";
    header.style.userSelect = "none";

    header.addEventListener("click", function () {
      const isOpen = body.style.display !== "none";
      body.style.display = isOpen ? "none" : "block";
      if (icon)
        icon.className = isOpen ? "bi bi-chevron-down" : "bi bi-chevron-up";
    });

    console.log("✓ Accordion initialisiert");
  }

  // ========================================
  // SOCKET ADMIN
  // ========================================

  async function refreshSocketList() {
    const btn = document.getElementById("refreshBtn");
    const origHTML = btn ? btn.innerHTML : null;
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Lädt...';
    }

    try {
      const res = await fetch(`${API_BASE}/api_get_sockets`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result = await res.json();

      if (result.success) {
        updateSocketTable(result.sockets);
        const totalEl = document.getElementById("totalConnections");
        if (totalEl) totalEl.textContent = result.total;
        showToast("Socket-Liste aktualisiert", "success");
      } else {
        showToast("Fehler: " + result.message, "error");
      }
    } catch (e) {
      showToast("Fehler: " + e.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origHTML;
      }
    }
  }

  async function disconnectAllSockets() {
    if (!confirm("Möchten Sie wirklich ALLE Socket-Verbindungen trennen?"))
      return;

    const btn = document.getElementById("disconnectAllBtn");
    const origHTML = btn ? btn.innerHTML : null;
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Trenne...';
    }

    try {
      const res = await fetch(`${API_BASE}/api_disconnect_all_sockets`, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const result = await res.json();
      if (result.success) {
        showToast(result.message, "success");
        setTimeout(() => refreshSocketList(), 1000);
      } else {
        showToast("Fehler: " + result.message, "error");
      }
    } catch (e) {
      showToast("Fehler: " + e.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origHTML;
      }
    }
  }

  async function disconnectSocket(sid, btnElement) {
    if (!confirm("Diese Socket-Verbindung trennen?")) return;

    const row = document.querySelector(`tr[data-sid="${sid}"]`);
    const origHTML = btnElement.innerHTML;
    btnElement.disabled = true;
    btnElement.innerHTML = '<i class="bi bi-hourglass-split"></i>';

    try {
      const res = await fetch(`${API_BASE}/api_disconnect_socket/${sid}`, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const result = await res.json();

      if (result.success) {
        showToast("Verbindung getrennt", "success");
        if (row) {
          row.style.opacity = "0";
          row.style.transition = "opacity 0.3s";
          setTimeout(() => {
            row.remove();
            const totalEl = document.getElementById("totalConnections");
            if (totalEl)
              totalEl.textContent = Math.max(
                0,
                parseInt(totalEl.textContent) - 1,
              );
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
        btnElement.innerHTML = origHTML;
      }
    } catch (e) {
      showToast("Fehler: " + e.message, "error");
      btnElement.disabled = false;
      btnElement.innerHTML = origHTML;
    }
  }

  function updateSocketTable(sockets) {
    const container = document.querySelector(".sockets-content");
    if (!container) return;

    if (!sockets || sockets.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon"><i class="bi bi-plug"></i></div>
          <h5>Keine aktiven Verbindungen</h5>
          <p>Aktuell sind keine Socket-Verbindungen für diese App aktiv.</p>
          <button class="btn btn-primary" onclick="AppAdmin.refreshSocketList()">
            <i class="bi bi-arrow-clockwise"></i> Aktualisieren
          </button>
        </div>`;
      return;
    }

    let tbody = document.getElementById("socketsTableBody");
    if (!tbody) {
      container.innerHTML = `
        <div class="sockets-table-card">
          <div class="table-header">
            <h5><i class="bi bi-table"></i> Verbindungsdetails</h5>
          </div>
          <div class="sockets-table-wrapper">
            <table class="sockets-table" id="socketsTable">
              <thead>
                <tr>
                  <th><i class="bi bi-person-fill"></i> Benutzer</th>
                  <th><i class="bi bi-fingerprint"></i> Socket ID</th>
                  <th><i class="bi bi-clock-history"></i> Verbunden seit</th>
                  <th class="text-center"><i class="bi bi-gear-fill"></i> Aktionen</th>
                </tr>
              </thead>
              <tbody id="socketsTableBody"></tbody>
            </table>
          </div>
          <div class="table-footer">
            <div class="showing-info">
              Zeige <strong id="visibleCount">0</strong> Verbindungen
            </div>
          </div>
        </div>`;
      tbody = document.getElementById("socketsTableBody");
    }

    if (tbody) {
      tbody.innerHTML = sockets
        .map(
          (s) => `
        <tr data-sid="${s.sid}" data-type="${s.user_id ? "auth" : "guest"}">
          <td>
            <div class="user-cell">
              <div class="user-avatar">
                <i class="bi bi-person-circle ${s.user_id ? "text-primary" : "text-secondary"}"></i>
              </div>
              <div class="user-info">
                <div class="username">${s.username}</div>
                <div class="user-meta">
                  ${
                    s.user_id
                      ? `<span class="badge badge-success"><i class="bi bi-shield-check"></i> Auth</span>
                       <span class="user-id">ID: ${s.user_id}</span>`
                      : `<span class="badge badge-secondary"><i class="bi bi-person"></i> Gast</span>`
                  }
                </div>
              </div>
            </div>
          </td>
          <td>
            <div class="socket-id-cell">
              <code class="socket-id">${s.sid.substring(0, 12)}...</code>
              <button class="copy-btn"
                onclick="navigator.clipboard.writeText('${s.sid}').then(() => AppAdmin.showToast('SID kopiert', 'success'))"
                title="Kopieren">
                <i class="bi bi-clipboard"></i>
              </button>
            </div>
          </td>
          <td>
            <div class="timestamp-cell">
              <i class="bi bi-calendar3"></i>
              <span>${s.connected_at}</span>
            </div>
          </td>
          <td class="text-center">
            <div class="action-buttons">
              <button class="btn-action btn-danger"
                onclick="AppAdmin.disconnectSocket('${s.sid}', this)"
                title="Verbindung trennen">
                <i class="bi bi-x-circle"></i>
              </button>
            </div>
          </td>
        </tr>
      `,
        )
        .join("");

      const countEl = document.getElementById("visibleCount");
      if (countEl) countEl.textContent = sockets.length;
    }
  }

  // ========================================
  // INITIALISIERUNG
  // ========================================

  function initSocketAdmin() {
    const socketsContainer = document.querySelector(".sockets-container");
    if (!socketsContainer) return;

    initSocketTestAccordion();

    const refreshBtn = document.getElementById("refreshBtn");
    const disconnectAllBtn = document.getElementById("disconnectAllBtn");
    if (refreshBtn) refreshBtn.addEventListener("click", refreshSocketList);
    if (disconnectAllBtn)
      disconnectAllBtn.addEventListener("click", disconnectAllSockets);

    // Beim Laden sofort aktualisieren
    setTimeout(() => refreshSocketList(), 800);

    // Auto-Refresh alle 30s
    setInterval(() => {
      if (!document.hidden) refreshSocketList();
    }, 30000);

    console.log("✓ Socket Admin initialisiert");
  }

  document.addEventListener("DOMContentLoaded", function () {
    console.log(`🏁 ${APP_NAME}: Admin Core initialisiert`);
    initSocketAdmin();
    console.log("✓ Admin Core bereit");
  });

  // ========================================
  // GLOBAL EXPORT
  // ========================================

  window.AppAdmin = {
    showToast,
    refreshSocketList,
    disconnectAllSockets,
    disconnectSocket,
    updateSocketTable,
  };
})();
