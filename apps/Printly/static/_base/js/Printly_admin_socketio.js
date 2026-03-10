/**
 * Printly - Socket.IO Integration
 *
 * Zuständig NUR für:
 * - Socket Verbindung (connect / disconnect)
 * - Ping / Pong Tests
 * - UI Status Badge (Verbunden / Getrennt)
 * - Event Log Einträge
 *
 * NICHT zuständig für (→ admin.js):
 * - Socket-Tabelle
 * - refreshSocketList
 * - disconnectSocket / disconnectAllSockets
 * - Accordion
 */

console.log("🔌 Printly Socket.IO wird initialisiert");

// ========================================
// GLOBALE VARIABLEN
// ========================================

let socket = null;
let isConnected = false;

console.log(`📱 Socket App: ${APP_NAME}`);

// ========================================
// SOCKET INITIALISIERUNG
// ========================================

function initializeSocket() {
  if (typeof io === "undefined") {
    console.error("❌ Socket.IO Library nicht gefunden!");
    return null;
  }

  try {
    socket = io(`/${APP_NAME}`);

    socket.on("connect", () => {
      console.log("✅ Socket.IO verbunden! SID:", socket.id);
      isConnected = true;
      updateConnectionStatus(true, socket.id);
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

    socket.on(`${APP_NAME}_connected`, (data) => {
      addLogEntry("success", `Verbunden: ${data.message || "Erfolgreich"}`);
    });

    socket.on("pong", (data) => {
      const receiveTime = Date.now();
      const totalMs = receiveTime - data.client_sent;

      const sentStr = new Date(data.client_sent).toLocaleTimeString("de-DE");
      const sentMs = data.client_sent % 1000;
      const serverDate = new Date(data.server_time);
      const serverStr = serverDate.toLocaleTimeString("de-DE");
      const serverMs = serverDate.getMilliseconds();
      const receiveStr = new Date(receiveTime).toLocaleTimeString("de-DE");
      const receiveMs = receiveTime % 1000;

      addLogEntry("info", `📤 Gesendet:  ${sentStr}:${sentMs}ms`);
      addLogEntry("info", `🖥️ Server:    ${serverStr}:${serverMs}ms`);
      addLogEntry(
        "info",
        `📥 Empfangen: ${receiveStr}:${receiveMs}ms | Gesamt: ${totalMs}ms`,
      );
      updateLastPing();
    });

    window.socket = socket;
    window.isSocketConnected = () => isConnected;
    console.log(`✅ ${APP_NAME}: Socket-Events registriert`);
    return socket;
  } catch (error) {
    console.error("❌ Socket Initialisierung fehlgeschlagen:", error);
    return null;
  }
}

// ========================================
// TEST-FUNKTIONEN (für onclick im HTML)
// ========================================

window.testSocketConnect = function () {
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
  const sendTime = Date.now();
  const sendTimeStr = new Date(sendTime).toLocaleTimeString("de-DE");
  const sendMs = sendTime % 1000;
  addLogEntry("info", `Ping gesendet um ${sendTimeStr}:${sendMs}ms`);
  socket.emit("ping", { client_sent: sendTime });
};

window.testSocketDisconnect = function () {
  if (!socket || !socket.connected) {
    addLogEntry("warning", "Bereits getrennt!");
    return;
  }
  addLogEntry("info", "Trenne Verbindung...");
  socket.disconnect();
};

window.clearTestLog = function () {
  const logElement = document.getElementById("testLog");
  if (!logElement) return;
  logElement.innerHTML = `
    <div class="log-entry log-info">
      <span class="log-time">--:--:--</span>
      <span class="log-message">Log gelöscht - Bereit für Tests...</span>
    </div>`;
};

// ========================================
// UI-UPDATE FUNKTIONEN
// ========================================

function updateConnectionStatus(connected, socketId) {
  const statusEl = document.getElementById("socketStatus");
  const socketIdEl = document.getElementById("socketId");
  const connectBtn = document.getElementById("connectBtn");
  const pingBtn = document.getElementById("pingBtn");
  const disconnectBtn = document.getElementById("disconnectBtn");

  if (!statusEl) return;

  if (connected) {
    statusEl.className = "status-badge online";
    statusEl.innerHTML = `<span class="status-dot"></span><span class="status-text">Verbunden</span>`;
    if (socketIdEl) socketIdEl.textContent = `Socket ID: ${socketId}`;
    if (connectBtn) connectBtn.disabled = true;
    if (pingBtn) pingBtn.disabled = false;
    if (disconnectBtn) disconnectBtn.disabled = false;
  } else {
    statusEl.className = "status-badge offline";
    statusEl.innerHTML = `<span class="status-dot"></span><span class="status-text">Getrennt</span>`;
    if (socketIdEl) socketIdEl.textContent = "Socket ID: -";
    if (connectBtn) connectBtn.disabled = false;
    if (pingBtn) pingBtn.disabled = true;
    if (disconnectBtn) disconnectBtn.disabled = true;
  }
}

function addLogEntry(type, message) {
  const logElement = document.getElementById("testLog");
  if (!logElement) return;
  const time = new Date().toLocaleTimeString("de-DE");
  const entry = document.createElement("div");
  entry.className = `log-entry log-${type}`;
  entry.innerHTML = `<span class="log-time">${time}</span><span class="log-message">${message}</span>`;
  logElement.appendChild(entry);
  logElement.scrollTop = logElement.scrollHeight;
}

function updateLastPing() {
  const el = document.getElementById("lastPing");
  if (el)
    el.textContent = `Letzter Ping: ${new Date().toLocaleTimeString("de-DE")}`;
}

// ========================================
// HELPER API FÜR CUSTOM CODE
// ========================================

window.AppSocket = {
  appName: APP_NAME,
  emit: (eventName, data) => {
    if (socket?.connected) socket.emit(`${APP_NAME}_${eventName}`, data);
  },
  on: (eventName, cb) => {
    if (socket) socket.on(`${APP_NAME}_${eventName}`, cb);
  },
  isConnected: () => socket?.connected ?? false,
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
  if (socket?.connected) socket.disconnect();
});

console.log(`✅ ${APP_NAME} socketio.js bereit`);
