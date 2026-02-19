// BasicChat.js - KORRIGIERTE VERSION mit Benutzerinformationen
console.log("Socket IO JS geladen");

// === GLOBALE VARIABLEN ===
let isConnected = false;
let currentChatRoom = null;

// === SOCKET.IO INTEGRATION ===
function initializeSocketIO() {
  if (typeof io === "undefined") {
    console.error("❌ Socket.IO nicht verfügbar!");
    return;
  }

  console.log("🔌 Initialisiere Socket.IO...");
  try {
    socket = io();
    setupSocketEvents();
  } catch (error) {
    console.error("❌ Socket.IO Fehler:", error);
  }
}

function setupSocketEvents() {
  // === BASIS VERBINDUNGS-EVENTS ===
  socket.on("connect", () => {
    console.log("✅ Socket.IO verbunden!");
    isConnected = true;
  });

  socket.on("disconnect", () => {
    console.log("❌ Socket.IO getrennt");
    isConnected = false;
    currentChatRoom = null;
    currentChatInfo = null;
  });

  socket.on("connect_error", (error) => {
    console.error("❌ Verbindungsfehler:", error);
  });
}

// === INITIALISIERUNG ===
document.addEventListener("DOMContentLoaded", function () {
  console.log("🏁 DOM bereit - SocketIO geladen");
  initializeSocketIO();
});

// ========================================
// SOCKET ADMIN FUNKTIONEN
// ========================================

/**
 * Aktualisiert die Socket-Liste
 * @param {string} apiUrl - URL zum Abrufen der Socket-Liste
 */
async function refreshSocketList(apiUrl) {
  const refreshBtn = document.getElementById("refreshBtn");
  const totalConnections = document.getElementById("totalConnections");

  if (!refreshBtn) {
    console.error("refreshBtn nicht gefunden");
    return;
  }

  // Button deaktivieren und Loading-State
  refreshBtn.disabled = true;
  const originalHTML = refreshBtn.innerHTML;
  refreshBtn.innerHTML =
    '<i class="bi bi-arrow-clockwise loading"></i> Lädt...';

  try {
    const response = await fetch(apiUrl, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const result = await response.json();

    if (result.success) {
      updateSocketTable(result.sockets);
      if (totalConnections) {
        totalConnections.textContent = result.total;
      }
      showStatus("Socket-Liste aktualisiert", "success");
      console.log(
        "✅ Socket-Liste aktualisiert:",
        result.total,
        "Verbindungen",
      );
    } else {
      showStatus("Fehler: " + result.message, "error");
      console.error("❌ API-Fehler:", result.message);
    }
  } catch (error) {
    console.error("❌ Fetch-Fehler:", error);
    showStatus("Fehler beim Aktualisieren: " + error.message, "error");
  } finally {
    refreshBtn.disabled = false;
    refreshBtn.innerHTML = originalHTML;
  }
}

/**
 * Trennt alle Socket-Verbindungen
 * @param {string} apiUrl - URL zum Trennen aller Sockets
 */
async function disconnectAllSockets(apiUrl) {
  if (!confirm("Möchten Sie wirklich ALLE Socket-Verbindungen trennen?")) {
    return;
  }

  const disconnectAllBtn = document.getElementById("disconnectAllBtn");

  if (!disconnectAllBtn) {
    console.error("disconnectAllBtn nicht gefunden");
    return;
  }

  // Button deaktivieren
  disconnectAllBtn.disabled = true;
  const originalHTML = disconnectAllBtn.innerHTML;
  disconnectAllBtn.innerHTML =
    '<i class="bi bi-hourglass-split"></i> Trenne...';

  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const result = await response.json();

    if (result.success) {
      showStatus(result.message, "success");
      console.log("✅ Alle Sockets getrennt:", result.disconnected);

      // Aktualisiere Liste nach 1 Sekunde
      const container = document.querySelector(".sockets-container");
      if (container && container.dataset.apiList) {
        setTimeout(() => refreshSocketList(container.dataset.apiList), 1000);
      }
    } else {
      showStatus("Fehler: " + result.message, "error");
      console.error("❌ API-Fehler:", result.message);
    }
  } catch (error) {
    console.error("❌ Disconnect-All-Fehler:", error);
    showStatus("Fehler: " + error.message, "error");
  } finally {
    disconnectAllBtn.disabled = false;
    disconnectAllBtn.innerHTML = originalHTML;
  }
}

/**
 * Trennt eine einzelne Socket-Verbindung
 * @param {string} apiUrlTemplate - URL-Template mit __SID__ Platzhalter
 * @param {string} sid - Socket ID
 * @param {HTMLElement} btnElement - Button-Element das geklickt wurde
 */
async function disconnectSocket(apiUrlTemplate, sid, btnElement) {
  if (!confirm("Diese Socket-Verbindung trennen?")) {
    return;
  }

  const row = document.querySelector(`tr[data-sid="${sid}"]`);
  const totalConnections = document.getElementById("totalConnections");

  // Button deaktivieren
  btnElement.disabled = true;
  const originalHTML = btnElement.innerHTML;
  btnElement.innerHTML = '<i class="bi bi-hourglass-split"></i>';

  try {
    const url = apiUrlTemplate.replace("__SID__", sid);
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const result = await response.json();

    if (result.success) {
      showStatus("Verbindung getrennt", "success");
      console.log("✅ Socket getrennt:", sid);

      // Fade out und entfernen
      if (row) {
        row.style.opacity = "0";
        setTimeout(() => {
          row.remove();

          // Update Counter
          if (totalConnections) {
            const currentTotal = parseInt(totalConnections.textContent);
            totalConnections.textContent = currentTotal - 1;
          }

          // Prüfe ob noch Verbindungen da sind
          const remainingRows = document.querySelectorAll(
            "#socketsTableBody tr",
          );
          if (remainingRows.length === 0) {
            // Lade Liste neu für Empty State
            const container = document.querySelector(".sockets-container");
            if (container && container.dataset.apiList) {
              setTimeout(
                () => refreshSocketList(container.dataset.apiList),
                500,
              );
            }
          }
        }, 300);
      }
    } else {
      showStatus("Fehler: " + result.message, "error");
      console.error("❌ API-Fehler:", result.message);
      btnElement.disabled = false;
      btnElement.innerHTML = originalHTML;
    }
  } catch (error) {
    console.error("❌ Disconnect-Fehler:", error);
    showStatus("Fehler: " + error.message, "error");
    btnElement.disabled = false;
    btnElement.innerHTML = originalHTML;
  }
}

// ========================================
// HELPER FUNCTIONS
// ========================================

function updateSocketTable(sockets) {
  const socketsTableBody = document.getElementById("socketsTableBody");
  const socketsContent = document.querySelector(".sockets-content");

  if (sockets.length === 0) {
    // Zeige Empty State
    if (socketsContent) {
      socketsContent.innerHTML = `
        <div class="empty-state">
          <i class="bi bi-plug"></i>
          <h5>Keine aktiven Verbindungen</h5>
          <p>Aktuell sind keine Socket-Verbindungen für diese App aktiv.</p>
        </div>
      `;
    }
    return;
  }

  // Wenn kein Table Body existiert, erstelle Table
  if (!socketsTableBody) {
    if (socketsContent) {
      socketsContent.innerHTML = `
        <div class="sockets-table-wrapper">
          <table class="sockets-table" id="socketsTable">
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
    // Hole neue Referenz
    const newTableBody = document.getElementById("socketsTableBody");
    if (!newTableBody) return;
    newTableBody.innerHTML = generateSocketRows(sockets);
  } else {
    // Update existierende Tabelle
    socketsTableBody.innerHTML = generateSocketRows(sockets);
  }
}

function generateSocketRows(sockets) {
  // Hole API-URL aus Container für onclick
  const container = document.querySelector(".sockets-container");
  const apiDisconnect = container ? container.dataset.apiDisconnect : "";

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
        <td>
          <code class="socket-id">${socket.sid.substring(0, 16)}...</code>
        </td>
        <td>
          <span class="timestamp">${socket.connected_at}</span>
        </td>
        <td>
          <button 
            class="btn-icon btn-disconnect" 
            onclick="disconnectSocket('${apiDisconnect}', '${
              socket.sid
            }', this)"
            title="Verbindung trennen"
          >
            <i class="bi bi-x-circle"></i>
          </button>
        </td>
      </tr>
    `,
    )
    .join("");
}

function showStatus(message, type) {
  const statusMessage = document.getElementById("statusMessage");
  if (!statusMessage) return;

  const icons = {
    success: "check-circle",
    error: "exclamation-circle",
    info: "info-circle",
  };

  statusMessage.innerHTML = `<i class="bi bi-${icons[type]}"></i>${message}`;
  statusMessage.className = "status-message " + type;
  statusMessage.style.display = "flex";

  setTimeout(() => {
    statusMessage.style.display = "none";
  }, 3000);
}

// ========================================
// AUTO-REFRESH (optional)
// ========================================
document.addEventListener("DOMContentLoaded", function () {
  const container = document.querySelector(".sockets-container");

  if (container && container.dataset.apiList) {
    console.log("✅ Socket Admin: Auto-Refresh aktiviert (30s)");

    setInterval(() => {
      if (!document.hidden) {
        console.log("🔄 Auto-Refresh Socket-Liste");
        refreshSocketList(container.dataset.apiList);
      }
    }, 30000);
  }
});
