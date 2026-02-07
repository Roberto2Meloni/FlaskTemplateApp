/**
 * Template_app_v002 - Socket.IO Integration
 * EINFACHE VERSION - Funktionen im globalen Scope für onclick
 */

console.log("🔌 Template_app_v002 Socket.IO wird initialisiert");

// ========================================
// GLOBALE VARIABLEN
// ========================================

let socket = null;
let isConnected = false;

// App-Name aus Meta-Tag oder Attribut
// const APP_NAME =
//   document.querySelector('meta[name="app-name"]')?.content ||
//   document.querySelector("[data-app-name]")?.dataset.appName ||
//   "Template_app_v002";

console.log(`📱 Socket App: ${APP_NAME}`);

// ========================================
// SOCKET INITIALISIERUNG
// ========================================

function initializeSocket() {
  console.log("🔌 Initialisiere globale Socket.IO Verbindung...");

  if (typeof io === "undefined") {
    console.error("❌ Socket.IO Library nicht gefunden!");
    return null;
  }

  try {
    socket = io();

    // Basis Events
    socket.on("connect", () => {
      console.log("✅ Socket.IO verbunden! (SID:", socket.id + ")");
      isConnected = true;
      updateConnectionStatus(true, socket.id);

      // Bei App registrieren
      socket.emit(`${APP_NAME}_connect`, {
        timestamp: new Date().toISOString(),
        page: window.location.pathname,
      });
    });

    socket.on("disconnect", (reason) => {
      console.log("❌ Socket.IO getrennt:", reason);
      isConnected = false;
      updateConnectionStatus(false, null);
    });

    socket.on("connect_error", (error) => {
      console.error("❌ Verbindungsfehler:", error);
      updateConnectionStatus(false, null);
    });

    // App-spezifische Events
    socket.on(`${APP_NAME}_connected`, (data) => {
      console.log("✅ Bei App registriert:", data);
      addLogEntry("success", `Verbunden: ${data.message || "Erfolgreich"}`);
    });

    socket.on(`${APP_NAME}_pong`, (data) => {
      console.log("🏓 Pong empfangen:", data);
      addLogEntry(
        "info",
        `Pong empfangen - ${data.active_connections || "?"} Verbindungen`,
      );
      updateLastPing();
    });

    console.log(`✅ ${APP_NAME}: Registriere Socket-Events`);

    // Socket global verfügbar machen
    window.socket = socket;
    window.isSocketConnected = () => isConnected;

    return socket;
  } catch (error) {
    console.error("❌ Socket Initialisierung fehlgeschlagen:", error);
    return null;
  }
}

// ========================================
// TEST-FUNKTIONEN - GLOBAL FÜR onclick
// ========================================

window.testSocketConnect = function () {
  console.log("🔌 Teste Verbindung...");
  addLogEntry("info", "Verbinde mit Socket...");

  if (!socket) {
    initializeSocket();
  } else if (!socket.connected) {
    socket.connect();
  } else {
    addLogEntry("warning", "Bereits verbunden!");
  }
};

window.testSocketPing = function () {
  if (!socket || !socket.connected) {
    addLogEntry("error", "Nicht verbunden!");
    return;
  }

  console.log("🏓 Sende Ping...");
  addLogEntry("info", "Sende Ping...");
  socket.emit(`${APP_NAME}_ping`);
};

window.testSocketDisconnect = function () {
  if (!socket || !socket.connected) {
    addLogEntry("warning", "Bereits getrennt!");
    return;
  }

  console.log("👋 Trenne Verbindung...");
  addLogEntry("info", "Trenne Verbindung...");
  socket.emit(`${APP_NAME}_disconnect`);
  socket.disconnect();
};

window.clearTestLog = function () {
  const logElement = document.getElementById("testLog");
  if (!logElement) return;

  logElement.innerHTML = `
    <div class="log-entry log-info">
      <span class="log-time">--:--:--</span>
      <span class="log-message">Log gelöscht - Bereit für Tests...</span>
    </div>
  `;
};

// ========================================
// DYNAMISCHER SOCKET-REFRESH (GEÄNDERT!)
// ========================================

window.refreshSocketList = async function () {
  console.log("🔄 Lade Socket-Liste neu...");
  addLogEntry("info", "Socket-Liste wird aktualisiert...");

  // Prüfe ob API URL definiert ist
  if (typeof API_GET_SOCKETS === "undefined") {
    console.warn("⚠️ API_GET_SOCKETS nicht definiert - verwende Reload");
    location.reload();
    return;
  }

  try {
    const response = await fetch(API_GET_SOCKETS, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
      console.log("✅ Socket-Daten:", data);

      // Aktualisiere Tabelle wenn Funktion existiert
      if (typeof window.updateSocketTable === "function") {
        window.updateSocketTable(data);
      }

      // Aktualisiere Statistiken wenn Funktion existiert
      if (typeof window.updateStatistics === "function") {
        window.updateStatistics(data);
      }

      addLogEntry("success", `${data.total || 0} Sockets geladen`);
    } else {
      throw new Error(data.message || "Unbekannter Fehler");
    }
  } catch (error) {
    console.error("❌ Fehler beim Laden:", error);
    addLogEntry("error", "Fehler - lade Seite neu...");

    // Fallback: Reload nach kurzer Verzögerung
    setTimeout(() => location.reload(), 1500);
  }
};

window.disconnectAllSockets = function () {
  console.log("⚠️ Trenne alle Sockets...");
  alert("Diese Funktion wird in einer späteren Version implementiert");
};

window.disconnectSocket = function (sid) {
  console.log("⚠️ Trenne Socket:", sid);
  alert(`Socket ${sid} trennen - wird in einer späteren Version implementiert`);
};

// ========================================
// UI-UPDATE FUNKTIONEN
// ========================================

function updateConnectionStatus(connected, socketId) {
  const statusElement = document.getElementById("socketStatus");
  const socketIdElement = document.getElementById("socketId");
  const connectBtn = document.getElementById("connectBtn");
  const pingBtn = document.getElementById("pingBtn");
  const disconnectBtn = document.getElementById("disconnectBtn");

  if (!statusElement) return;

  if (connected) {
    statusElement.className = "status-badge online";
    statusElement.innerHTML = `
      <span class="status-dot"></span>
      <span class="status-text">Verbunden</span>
    `;
    socketIdElement.textContent = `Socket ID: ${socketId}`;

    if (connectBtn) connectBtn.disabled = true;
    if (pingBtn) pingBtn.disabled = false;
    if (disconnectBtn) disconnectBtn.disabled = false;
  } else {
    statusElement.className = "status-badge offline";
    statusElement.innerHTML = `
      <span class="status-dot"></span>
      <span class="status-text">Getrennt</span>
    `;
    socketIdElement.textContent = "Socket ID: -";

    if (connectBtn) connectBtn.disabled = false;
    if (pingBtn) pingBtn.disabled = true;
    if (disconnectBtn) disconnectBtn.disabled = true;
  }
}

function addLogEntry(type, message) {
  const logElement = document.getElementById("testLog");
  if (!logElement) return;

  const now = new Date();
  const time = now.toLocaleTimeString("de-DE");

  const entry = document.createElement("div");
  entry.className = `log-entry log-${type}`;
  entry.innerHTML = `
    <span class="log-time">${time}</span>
    <span class="log-message">${message}</span>
  `;

  logElement.appendChild(entry);
  logElement.scrollTop = logElement.scrollHeight;
}

function updateLastPing() {
  const lastPingElement = document.getElementById("lastPing");
  if (!lastPingElement) return;

  const now = new Date();
  lastPingElement.textContent = `Letzter Ping: ${now.toLocaleTimeString("de-DE")}`;
}

// ========================================
// HELPER API FÜR CUSTOM CODE
// ========================================

window.AppSocket = {
  appName: APP_NAME,

  emit: (eventName, data) => {
    if (socket && socket.connected) {
      socket.emit(`${APP_NAME}_${eventName}`, data);
      console.log(`📤 ${APP_NAME}_${eventName}:`, data);
    } else {
      console.warn("⚠️ Socket nicht verbunden");
    }
  },

  on: (eventName, callback) => {
    if (socket) {
      socket.on(`${APP_NAME}_${eventName}`, callback);
    }
  },

  sendPing: () => {
    if (socket && socket.connected) {
      socket.emit(`${APP_NAME}_ping`);
      console.log("🏓 Ping gesendet");
    } else {
      console.warn("⚠️ Socket nicht verbunden");
    }
  },

  isConnected: () => socket && socket.connected,

  getSocket: () => socket,
};

// ========================================
// AUTO-INITIALISIERUNG
// ========================================

document.addEventListener("DOMContentLoaded", function () {
  console.log(`🏁 ${APP_NAME}: Socket Client wird initialisiert`);
  initializeSocket();
});

window.addEventListener("beforeunload", () => {
  if (socket && socket.connected) {
    console.log("👋 Seite wird geschlossen - trenne Socket");
    socket.emit(`${APP_NAME}_disconnect`);
  }
});

console.log(`✅ ${APP_NAME} Socket Integration bereit`);
